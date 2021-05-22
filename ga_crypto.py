from datetime import datetime
import random
from simulator import run_simulation
from optimize.base import EaSimpleOptimizer
from strategy import PurchaseStrategy
from tools.retrieve_data import get_historical_price


class StrategyTrainer:

    def __init__(self, stg_class=None):
        self.opt = EaSimpleOptimizer()
        self.df_historical_price = None
        self.stg_class = stg_class

    @staticmethod
    def run_ga(df_historical_price, strategy):
        initial_jpy_asset = 200000
        crypto_amount = 0

        history = run_simulation(crypto_amount=crypto_amount, assets_jpy=initial_jpy_asset, strategy=strategy,
                                 df_historical_price=df_historical_price)
        final_state = history[-1]
        final_total_asset = final_state["total"]
        earn_rate = (final_total_asset - initial_jpy_asset) / initial_jpy_asset * 100

        return earn_rate

    def eval_func(self, individual):
        if not (0 <= individual[0] <= 1 and 0 <= individual[1] <= 1):
            earn_rate = -100
        else:
            stg = self.stg_class(*individual)
            earn_rate = self.run_ga(self.df_historical_price, strategy=stg)
        return earn_rate,

    def prepare(self, weights, attr_list, sigma, crypto_name="ETH", start=datetime(2021, 4, 20),
                end=datetime(2021, 4, 22), pop_size=50, tour_size_factor=0.01, ngen=10):

        mu = [0] * len(attr_list)
        self.df_historical_price = get_historical_price(crypto_name=crypto_name, start=start, end=end)

        self.opt.prepare(attr_list=attr_list, weights=weights, eval_func=self.eval_func, mu=mu, sigma=sigma,
                         pop_size=pop_size, tour_size_factor=tour_size_factor, ngen=ngen)

    def train(self, verbose=False):
        hof, pop, log = self.opt.run(verbose=verbose)

        best = hof[0]
        stg = self.stg_class(*best)
        return stg


def main():
    pop_size = 50
    ngen = 10
    weights = (1.0,)
    attr_list = [[random.uniform, 0, 0.1], [random.uniform, 0.1, 0.2],
                 [random.uniform, 0.00075, 0.005], [random.uniform, 0.1, 5]]
    sigma = [0.2, 0.2, 0.001, 3]
    st = StrategyTrainer(stg_class=PurchaseStrategy)
    st.prepare(weights=weights, attr_list=attr_list, sigma=sigma)
    stg = st.train(verbose=True)

    print(stg)


if __name__ == "__main__":
    main()
