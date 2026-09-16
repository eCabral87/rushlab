"""Offset optimization with DEAP on top of Webster timing."""

from __future__ import annotations

import functools
import multiprocessing
import random
from dataclasses import dataclass
from typing import Any

from deap import base, creator, tools

from rushlab.signals.evaluator import DEFAULT_WORKERS, EvaluatorConfig, evaluate_candidate

BUDGETS: dict[str, dict[str, int]] = {
    "light": {"population": 16, "generations": 12},
    "full": {"population": 24, "generations": 20},
}
CROSSOVER_PROBABILITY = 0.7
MUTATION_PROBABILITY = 0.3
MUTATION_SIGMA_FRACTION = 0.1


@dataclass
class OptimizationResult:
    offsets: dict[str, float]
    fitness: float
    history: list[float]
    evaluations: int
    budget: str


def _evaluate_individual(
    individual: list[float], config: EvaluatorConfig, junction_ids: list[str]
) -> tuple[float]:
    offsets = {
        junction: float(value) for junction, value in zip(junction_ids, individual, strict=True)
    }
    result = evaluate_candidate(config, offsets)
    return (float(result["fitness"]),)


def optimize_offsets(
    config: EvaluatorConfig,
    junction_ids: list[str],
    cycles: dict[str, float],
    *,
    budget: str = "light",
    seed: int = 42,
    workers: int = DEFAULT_WORKERS,
) -> OptimizationResult:
    """GA over per-junction offsets; each individual is one SUMO evaluation."""
    if budget not in BUDGETS:
        raise ValueError(f"unknown budget {budget!r}; choose from {sorted(BUDGETS)}")
    if not junction_ids:
        raise ValueError("no junctions to optimize")
    parameters = BUDGETS[budget]
    random.seed(seed)

    if not hasattr(creator, "RushLabFitnessMin"):
        creator.create("RushLabFitnessMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "RushLabIndividual"):
        creator.create("RushLabIndividual", list, fitness=creator.__dict__["RushLabFitnessMin"])
    individual_class = creator.__dict__["RushLabIndividual"]

    def random_offsets() -> Any:
        return individual_class(
            [random.uniform(0.0, cycles[junction]) for junction in junction_ids]
        )

    toolbox: Any = base.Toolbox()
    toolbox.register("individual", random_offsets)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def crossover(first: list[float], second: list[float]) -> tuple[list[float], list[float]]:
        return tools.cxBlend(first, second, alpha=0.3)

    def mutate(individual: list[float], indpb: float = 0.3) -> tuple[list[float]]:
        for index, junction in enumerate(junction_ids):
            if random.random() < indpb:
                spread = cycles[junction] * MUTATION_SIGMA_FRACTION
                individual[index] = (individual[index] + random.gauss(0.0, spread)) % cycles[
                    junction
                ]
        return (individual,)

    toolbox.register("mate", crossover)
    toolbox.register("mutate", mutate)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register(
        "evaluate",
        functools.partial(_evaluate_individual, config=config, junction_ids=junction_ids),
    )

    population = toolbox.population(n=parameters["population"])
    history: list[float] = []
    evaluations = 0

    def evaluate_batch(individuals: list[Any], pool: Any) -> None:
        nonlocal evaluations
        if not individuals:
            return
        fitnesses = pool.map(toolbox.evaluate, individuals)
        for individual, fitness in zip(individuals, fitnesses, strict=True):
            individual.fitness.values = fitness
        evaluations += len(individuals)

    with multiprocessing.Pool(processes=max(workers, 1)) as pool:
        evaluate_batch(population, pool)
        history.append(min(individual.fitness.values[0] for individual in population))
        for _ in range(parameters["generations"]):
            offspring = [toolbox.clone(individual) for individual in population]
            for first, second in zip(offspring[::2], offspring[1::2], strict=False):
                if random.random() < CROSSOVER_PROBABILITY:
                    toolbox.mate(first, second)
                    del first.fitness.values
                    del second.fitness.values
            for mutant in offspring:
                if random.random() < MUTATION_PROBABILITY:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            invalid = [individual for individual in offspring if not individual.fitness.valid]
            evaluate_batch(invalid, pool)
            population[:] = offspring
            history.append(min(individual.fitness.values[0] for individual in population))

    best = tools.selBest(population, 1)[0]
    offsets = {
        junction: float(value) for junction, value in zip(junction_ids, list(best), strict=True)
    }
    return OptimizationResult(
        offsets=offsets,
        fitness=float(best.fitness.values[0]),
        history=history,
        evaluations=evaluations,
        budget=budget,
    )
