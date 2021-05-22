from datetime import datetime
import random
from crypto import run_simulation
from optimize.crypto_optimizer_wu import EaSimpleOptimizer
from tools.retrieve_data import get_historical_price


def run_ga(df_historical_price, coef):
    initial_jpy_asset = 200000
    crypto_amount = 0

    history = run_simulation(crypto_amount=crypto_amount, assets_jpy=initial_jpy_asset, coef=coef,
                             df_historical_price=df_historical_price)
    final_state = history[-1]
    final_total_asset = final_state["total"]
    earn_rate = (final_total_asset - initial_jpy_asset) / initial_jpy_asset * 100

    return earn_rate


def main():
    crypto_name = "ETH"
    start = datetime(2021, 1, 1)
    end = datetime(2021, 4, 22)
    df_historical_price = get_historical_price(crypto_name=crypto_name, start=start, end=end)

    def eval_func(individual):
        earn_rate = run_ga(df_historical_price, coef=individual)
        return earn_rate,

    weights = (1.0,)
    # pop_size = 1000
    pop_size = 50
    tour_size_factor = 0.01
    # TODO: limit the min_val, max_val to a certain range
    attr_list = [[random.uniform, 0, 0.05], [random.uniform, 0.1, 0.2],
                 [random.uniform, 0.00075, 0.005], [random.uniform, 0.1, 5]]
    mu = [0, 0.15, 0.0008, 2]
    sigma = [0.2, 0.2, 0.001, 3]
    ngen = 10

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
