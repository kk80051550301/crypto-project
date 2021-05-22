from datetime import datetime
import random
from simulator import run_simulation
from optimize.base import EaSimpleOptimizer
from strategy import PurchaseStrategy
from tools.retrieve_data import get_historical_price


def run_ga(df_historical_price, strategy):
    initial_jpy_asset = 200000
    crypto_amount = 0

    history = run_simulation(crypto_amount=crypto_amount, assets_jpy=initial_jpy_asset, strategy=strategy,
                             df_historical_price=df_historical_price)
    final_state = history[-1]
    final_total_asset = final_state["total"]
    earn_rate = (final_total_asset - initial_jpy_asset) / initial_jpy_asset * 100

    return earn_rate


def main():
    crypto_name = "ETH"
    start = datetime(2021, 1, 1)
    # start = datetime(2021, 4, 20)
    end = datetime(2021, 4, 22)
    df_historical_price = get_historical_price(crypto_name=crypto_name, start=start, end=end)

    def eval_func(individual):
        if not (0 <= individual[0] <= 1 and 0 <= individual[1] <= 1):
            earn_rate = -100
        else:
            stg = PurchaseStrategy(*individual)
            earn_rate = run_ga(df_historical_price, strategy=stg)
        return earn_rate,

    weights = (1.0,)
    # pop_size = 1000
    pop_size = 50
    tour_size_factor = 0.01
    attr_list = [[random.uniform, 0, 0.1], [random.uniform, 0.1, 0.2],
                 [random.uniform, 0.00075, 0.005], [random.uniform, 0.1, 5]]
    mu = [0] * 4
    sigma = [0.2, 0.2, 0.001, 3]
    ngen = 10

    opt = EaSimpleOptimizer()
    opt.prepare(attr_list=attr_list, weights=weights, eval_func=eval_func, mu=mu, sigma=sigma,
                pop_size=pop_size, tour_size_factor=tour_size_factor, ngen=ngen)
    hof, pop, log = opt.run(verbose=True)

    # print(log)
    print("hof:{0}".format("\t".join(map(str, hof[0]))))
    return pop, log, hof


if __name__ == "__main__":
    # old()
    main()
