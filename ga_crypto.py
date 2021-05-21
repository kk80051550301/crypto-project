from datetime import datetime

from crypto import run_simulation
from optimize.crypto_optimize import optimize_main
import random

from optimize.crypto_optimizer_wu import EaSimpleOptimizer


def old():
    POP_SIZE = 50
    mu = [0, 0]
    sigma = [1, 1]
    FINAL_GEN = 20
    paras_list = [[random.uniform, 0, 2], [random.uniform, 0, 2]]
    hour = 72
    cost_func = lambda paras, min=0.05, max=0.7, hour=hour: run_ga(hour, coef=(min, max, paras))

    max_inds = optimize_main(paras_list, POP_SIZE, mu, sigma, FINAL_GEN, cost_func)
    print(max_inds)

def run_ga(coef):
    start = datetime(2021, 1, 1)
    end = datetime(2021, 4, 22)
    INITIAL_ASSETS = assets_jpy = 200000
    crypto_name = "ETH"
    crypto_amount = 0
    history = run_simulation(
        crypto_amount=crypto_amount,
        assets_jpy=assets_jpy,
        coef=coef,
        crypto_name=crypto_name,
        start=start,
        end=end)
    final_state = history[-1]
    final_total = final_state["total"]
    earn_rate = (final_total - INITIAL_ASSETS) / INITIAL_ASSETS * 100

    return earn_rate


def main():

    weights = (1.0,)

    def eval_func(individual):
        # TODO: replace with earn-value based on simulation
        return sum(individual),

    # pop_size = 1000
    pop_size = 300
    tour_size_factor = 0.01
    paras_list = [[random.uniform, -10, 10], [random.randint, -200, 300], [random.uniform, -1000, 1500]]
    ngen = 40

    opt = EaSimpleOptimizer()
    opt.prepare(paras_list, weights, eval_func, pop_size=pop_size, tour_size_factor=tour_size_factor, ngen=ngen)
    hof, pop, log = opt.run(verbose=True)

    # print(log)
    print(hof)
    return pop, log, hof


if __name__ == "__main__":
    # old()
    main()
