from hashlib import new
import random
import numpy as np
from deap import base, creator, tools
from deap.benchmarks import ackley
# DEAP modual tutorial: https://deap.readthedocs.io/en/master/overview.html

def gen_func_list(func, para1, para2):
    return lambda: func(para1, para2)

def paras_func(para_list):
    func_seq = []
    for para in para_list:
        func_seq.append(gen_func_list(para[0], para[1], para[2]))
    return func_seq

def optimize_main(paras_list, POP_SIZE, mu, sigma, FINAL_GEN, cost_func):
    # decide params-range 
    func_seq = paras_func(paras_list)
    # decide min/max optimize
    creator.create("FitMax", base.Fitness, weights=(1, ))
    creator.create("Individual", list, fitness=creator.FitMax)
    toolbox = base.Toolbox()
    toolbox.register("genInd", tools.initCycle, creator.Individual, func_seq, 1)
    toolbox.register("genPop", tools.initRepeat, list, toolbox.genInd, POP_SIZE)
    # def cost func
    toolbox.register("evaluate", cost_func)
    # toolbox.register("evaluate", ackley)
    # def sel func
    tournsize = int(POP_SIZE * 0.1)
    toolbox.register("sel", tools.selTournament, tournsize=tournsize)
    # def crsover func
    toolbox.register("crsover", tools.cxBlend, alpha=0.2)
    # def mutant
    toolbox.register("mutant", tools.mutGaussian, mu=mu, sigma=sigma, indpb=0.1)

    pop = toolbox.genPop()
    for ind, cost in zip(pop, list(map(toolbox.evaluate, pop))):
        ind.fitness.values = cost
    fits = [ind.fitness.values for ind in pop]

    print(f"0 generation avg: {np.average(fits)}")
    best_ind = [[0,0], (0,)]
    for g in range(1, FINAL_GEN):
        # select better cost
        offspring = toolbox.sel(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))
        # mate process
        MATE_PB = 0.5
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < MATE_PB:
                toolbox.crsover(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        # mutant process
        MUTANT_PB = 0.2
        for child in offspring:
            if random.random() < MUTANT_PB:
                toolbox.mutant(child)
                del child.fitness.values
        # re-calculate cost
        invalid_inds = [child for child in offspring if not child.fitness.valid]
        fits = list(map(toolbox.evaluate, invalid_inds))
        for ind, cost in zip(invalid_inds, fits):
            ind.fitness.values = cost
        pop[:] = offspring

        fits = [ind.fitness.values for ind in pop]
        max_ind = [offspring[fits.index(max(fits))], fits[fits.index(max(fits))]]
        best_ind = max_ind if max_ind[-1][0] > best_ind[-1][0] else best_ind

        print(f"{g} generation, avg: {np.average(fits)}, MAX: {max(fits)}, MIN: {min(fits)}")
    print("best ind", best_ind)

if __name__ == "__main__":
    POP_SIZE = 1000
    mu = [0, 0, 0]
    sigma = [500, 200, 500]
    FINAL_GEN = 100
    paras_list = [[random.uniform, -10, 10], [random.randint, -200, 300], [random.uniform, -1000, 1500]]
    # test cost
    def cost_func(coef):
        return (-1 * (coef[0] ** 2 + coef[1] ** 2 + coef[2] ** 2), )

    optimize_main(paras_list, POP_SIZE, mu, sigma, FINAL_GEN, cost_func)
