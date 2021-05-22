import time
import random
from functools import partial
import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

"""
Genes: coef (min, max, a, slop)
Evaluation function: coef: tuple => simulation => earn rate: float
"""


class EaSimpleOptimizer:

    def prepare(self, attr_list, weights, eval_func, mu, sigma, alpha=0.2, pop_size=300, tour_size_factor=0.01,
                ngen=40, mutpb=0.2, cxpb=0.5, indpb=0.05):
        creator.create("FitnessMax", base.Fitness, weights=weights)
        creator.create("Individual", list, fitness=creator.FitnessMax)
        toolbox = base.Toolbox()
        func_seq = [partial(*item) for item in attr_list]
        # Structure initializers
        toolbox.register("individual", tools.initCycle, creator.Individual, func_seq)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", eval_func)
        toolbox.register("mate", tools.cxBlend, alpha=alpha)
        toolbox.register("mutate", tools.mutGaussian, mu=mu, sigma=sigma, indpb=indpb)
        toolbox.register("select", tools.selTournament, tournsize=max(1, int(pop_size * tour_size_factor)))

        self.pop = toolbox.population(n=pop_size)
        self.hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)
        self.stats = stats
        self.toolbox = toolbox

        self.cxpb = cxpb
        self.mutpb = mutpb
        self.ngen = ngen

    def run(self, verbose=False):
        start = time.time()
        pop, log = algorithms.eaSimple(self.pop,
                                       self.toolbox,
                                       cxpb=self.cxpb,
                                       mutpb=self.mutpb,
                                       ngen=self.ngen,
                                       stats=self.stats,
                                       halloffame=self.hof,
                                       verbose=verbose)
        elapsed = time.time() - start
        if verbose:
            print(f"Time cost: {elapsed:.1f}s")

        self.pop = pop
        self.log = log
        return self.hof, self.pop, self.log


def test():
    random.seed(64)

    def eval_func(individual):
        return -1 * (individual[0] ** 2 + individual[1] ** 2 + individual[2] ** 2),

    weights = (1.0,)
    pop_size = 1000
    tour_size_factor = 0.01
    paras_list = [[random.uniform, -10, 10], [random.randint, -200, 300], [random.uniform, -1000, 1500]]
    mu = [0.0, 0.0, 0.0]
    sigma = [500.0, 200.0, 500.0]
    ngen = 100

    opt = EaSimpleOptimizer()
    opt.prepare(attr_list=paras_list, weights=weights, eval_func=eval_func,
                mu=mu, sigma=sigma, pop_size=pop_size,
                tour_size_factor=tour_size_factor, ngen=ngen)
    hof, pop, log = opt.run(verbose=True)

    # print(log)
    print(hof)
    return pop, log, hof


if __name__ == "__main__":
    test()
