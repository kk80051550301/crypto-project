import math


def get_stg_class(stg_name):
    # https://stackoverflow.com/a/1176179
    try:
        return globals()[stg_name]
    except KeyError:
        print(f"Cannot find strategy class: {stg_name}")
        return None


class StrategyBase:

    def __init__(self):
        self.id_ = -1

    @property
    def params(self):
        raise NotImplemented

    @classmethod
    def param_limits(cls):
        raise NotImplemented()

    def calc_buy_sell_rate(self, change_rate):
        raise NotImplemented()

    @classmethod
    def sample_parameters(cls):
        return []

    @classmethod
    def plot_samples(cls):
        if not cls.sample_parameters():
            return

        import matplotlib.pyplot as plt
        import numpy as np

        n_cols = 3
        n_rows = math.ceil(len(cls.sample_parameters())/n_cols)
        x_axis = np.arange(-20, 20, 0.1)
        for i, item in enumerate(cls.sample_parameters()):
            stg = cls(*item)
            vfunc = np.vectorize(stg.calc_buy_sell_rate)
            y_axis = vfunc(x_axis)

            ax1 = plt.subplot(n_cols, n_rows, i + 1)
            ax1.plot(x_axis, y_axis)
            ax1.set_title(f"{stg}")
        plt.show()

    def path_str(self):
        return "st[{:d}({})]".format(self.id_, "_".join(map(str, self.params)))


class ExpRatioStrategy(StrategyBase):
    """f(x)= a * exp(n * x)
    The return value will be set to 0 if it is less than min_thresh
    The return value will be less than ceiling
    """
    min_thresh = 0.01
    ceiling = 0.2

    def __init__(self, a, n):
        super().__init__()
        # self.min_thresh = min_thresh
        # self.ceiling = ceiling
        self.a = a
        self.n = n

    @property
    def params(self):
        # self.min_thresh, self.ceiling,
        return [self.a, self.n]

    @classmethod
    def param_limits(cls):
        # (0, .2),
        # (0, .8),
        return [
            (0.0001, 1),
            (0.001, 10)
        ]

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
    def sample_parameters(cls):
        return [
            (0.01, .5, 0.00075, 2),
            (0.2, .4, 0.000724, 3),
            (0.03, .7, 0.000724, 4),
            (0.426715, 0.258681, 288.190216, 3.928983),
            (0.592046, 0.091942, 306.110021, 4.229820),
            (0.615946, 0.999249, 0.008156, 0.740697),
        ]


class LinearRatioStrategy(StrategyBase):
    """f(x)= a * x + b
    The return value will be set to 0 if it is less than min_thresh
    The return value will be less than ceiling
    """
    min_thresh = 0.01
    ceiling = 0.2

    def __init__(self, a, b):
        super().__init__()
        # self.min_thresh = min_thresh
        # self.ceiling = ceiling
        self.a = a
        self.b = b

    @classmethod
    def param_limits(cls):
        return [
            # (0, .1),
            # (0, .8),
            (0.0001, 50),
            (-100, 100)
        ]

    @property
    def params(self):
        return [self.min_thresh, self.ceiling, self.a]

    def calc_buy_sell_rate(self, change_rate):
        try:
            invest_index = self.a * abs(change_rate)
        except OverflowError as e:
            print(change_rate, self.a)
            print(e)
            raise e

        invest_index = 0 if invest_index < self.min_thresh else invest_index
        invest_index = min(invest_index, self.ceiling)

        if change_rate < 0:
            invest_index = - invest_index

        return invest_index

    def __str__(self):
        return f"<{self.__class__.__name__}({self.min_thresh:f}, {self.ceiling:f}, {self.a:f})>"

    @classmethod
    def sample_parameters(cls):
        return [
            (0.01, .5, 0.5),
            (0.2, .4, 1),
            (0.03, .7, 3),
        ]


def test():
    stg = ExpRatioStrategy(0.001, 0.0002)
    print(stg)


if __name__ == '__main__':
    # test()
    ExpRatioStrategy.plot_samples()
    # LinearRatioStrategy.plot_samples()
