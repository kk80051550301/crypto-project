from datetime import datetime
import random
from crypto import run_simulation
from optimize.crypto_optimizer_wu import EaSimpleOptimizer


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
        earn_rate = run_ga(coef=individual)
        return earn_rate,

    # pop_size = 1000
    pop_size = 300
    tour_size_factor = 0.01
    # TODO: limit the min_val, max_val to a certain range
    attr_list = [[random.uniform, 0, 0.05], [random.uniform, 0.1, 0.2],
                 [random.uniform, 0.00075, 0.005], [random.uniform, 0.1, 5]]
    mu = [0, 0.15, 0.0008, 2]
    sigma = [0.2, 0.2, 0.001, 3]
    ngen = 40

    opt = EaSimpleOptimizer()
    opt.prepare(attr_list=attr_list, weights=weights, eval_func=eval_func, mu=mu, sigma=sigma,
                pop_size=pop_size, tour_size_factor=tour_size_factor, ngen=ngen)
    hof, pop, log = opt.run(verbose=True)

    # print(log)
    print(hof)
    return pop, log, hof


if __name__ == "__main__":
    # old()
    main()
