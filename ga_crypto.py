import random
import pandas as pd

from scenario import Scenario
from simulator import run_simulation
from optimize.base import EaSimpleOptimizer
from strategy import ExpRatioStrategy, LinearRatioStrategy
from tools.utils import calc_earn_rate, calc_profit

class StrategyTrainer:

    def __init__(self, stg_class=None, init_currency=200000, init_crypto=0):
        self.opt = EaSimpleOptimizer()
        self.scenario = None
        self.stg_class = stg_class
        self.limits_list = self.stg_class.param_limits()
        self.initial_currency = init_currency
        self.init_crypto_amount = init_crypto



    def simulate_earn_rate(self, df_historical_price, strategy):
        history = run_simulation(crypto_amount=self.init_crypto_amount, assets_jpy=self.initial_currency,
                                 strategy=strategy, df_historical_price=df_historical_price)
        final_state = history[-1]
        final_total_asset = final_state["total"]
        earn_rate = calc_earn_rate(final_total_asset, self.initial_currency)
        # calculate earn_rate by each trade
        # earn_rate = calc_profit(history)
        return earn_rate

    def eval_func(self, individual):
        # TODO: Use constraints instead: https://deap.readthedocs.io/en/master/tutorials/advanced/constraints.html
        for i, limits in enumerate(self.limits_list):
            if not limits[0] <= individual[i] <= limits[1]:
                earn_rate = -100
                break
        else:
            stg = self.stg_class(*individual)
            earn_rate = self.simulate_earn_rate(self.scenario.data, strategy=stg)
        return earn_rate,

    @property
    def weights(self):
        return (1.0, )

    def prepare(self, pop_size=50, tour_size_factor=0.01, ngen=10, sigma_divider=60):
        attr_list = list(map(lambda limits: (random.uniform, *limits), self.limits_list))
        mu = [0] * len(attr_list)
        sigma = list(map(lambda limits: (limits[1] - limits[0])/sigma_divider, self.limits_list))

        self.opt.prepare(attr_list=attr_list, weights=self.weights, eval_func=self.eval_func, mu=mu, sigma=sigma,
                         pop_size=pop_size, tour_size_factor=tour_size_factor, ngen=ngen)

    def update_scenario(self, scenario):
        self.scenario = scenario

    def train(self, verbose=False):
        hof, pop, log = self.opt.run(verbose=verbose)
        best = hof[0]
        stg = self.stg_class(*best)
        return stg


def main():
    random.seed(42)
    scenario_file = "input/market_patterns.csv"
    df_scenarios = pd.read_csv(scenario_file)
    for col in ["start", "end"]:
        df_scenarios[col] = pd.to_datetime(df_scenarios[col])
    scenarios = []
    for i, row in df_scenarios.iterrows():
        if row["skip"] == "yes":
            continue
        del row["skip"]
        s = Scenario(**row)
        s.populate_data()
        scenarios.append(s)

    # stg_class = ExpRatioStrategy
    stg_class = LinearRatioStrategy
    
    for i, scenario in enumerate(scenarios):
        st = StrategyTrainer(stg_class=stg_class)
        st.prepare(pop_size=100, ngen=100, sigma_divider=1000)
        # if i == 1:
        #     continue
        print(f"Training under {scenario}...")
        st.update_scenario(scenario)
        stg = st.train(verbose=True)
        print(f"Best strategy under {scenario}: {stg}")
        print("Scenario: {}".format("\t".join(map(str, stg.params))))


if __name__ == "__main__":
    main()
