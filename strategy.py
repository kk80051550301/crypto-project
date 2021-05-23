import math


class PurchaseStrategy:
    def __init__(self, min_thresh, ceiling, a, n):
        self.min_thresh = min_thresh
        self.ceiling = ceiling
        self.a = a
        self.n = n

    def calc_buy_sell_rate(self, change_rate):
        try:
            invest_index = self.a * math.exp(self.n * abs(change_rate))
        except OverflowError as e:
            print(change_rate, self.a, self.n)
            print(e)
            raise e

        invest_index = 0 if invest_index < self.min_thresh else invest_index
        invest_index = min(invest_index, self.ceiling)

        if change_rate < 0:
            invest_index = - invest_index

        return invest_index

    def __str__(self):
        return f"<{self.__class__.__name__}({self.min_thresh:f}, {self.ceiling:f}, {self.a:f}, {self.n:f})>"

    @classmethod
    def plot_samples(cls):
        import matplotlib.pyplot as plt
        import numpy as np

        eval_list = [
            (0.01, .5, 0.00075, 2),
            (0.2, .4, 0.000724, 3),
            (0.03, .7, 0.000724, 4),
        ]

        n_cols = 3
        n_rows = math.ceil(len(eval_list)/n_cols)
        x_axis = np.arange(-5, 5, 0.1)
        for i, item in enumerate(eval_list):
            stg = cls(*item)
            vfunc = np.vectorize(stg.calc_buy_sell_rate)
            y_axis = vfunc(x_axis)

            ax1 = plt.subplot(n_cols, n_rows, i + 1)
            ax1.plot(x_axis, y_axis)
            ax1.set_title(f"{stg}")
        plt.show()


def test():
    stg = PurchaseStrategy(0.001, 0.0002, 0.1, 0.2)
    print(stg)


if __name__ == '__main__':
    # test()
    PurchaseStrategy.plot_samples()
