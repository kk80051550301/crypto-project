import matplotlib.pyplot as plt
import numpy as np
import math

from matplotlib import pyplot as plt


def percent_calc(value, pre_value):
    # return percentage(unit is 1%)
    return (value - pre_value) / pre_value * 100


def risk_cal(change_rate, min_thresh, ceiling, a, n):
    # def invest index func
    # print(x, min_val, max_val, paras)
    # a, n = paras
    try:
        invest_index = a * math.exp(n * abs(change_rate))
    except OverflowError as e:
        print(change_rate, min_thresh, ceiling, a, n)
        print(e)
        raise e
    # invest_index = min(max(invest_index, min_val), max_val)

    invest_index = 0 if invest_index < min_thresh else invest_index
    invest_index = min(invest_index, ceiling)

    if change_rate < 0:
        invest_index = - invest_index

    return invest_index


def plot_formula():
    eval_list = [
        (0.5, 1.5, (0.00075, 2)),
        (0, 2, (0.000724, 3)),
        (0, 2, (0.000724, 4)),
    ]

    x_axis = np.arange(-30, 30, 0.1)
    vfunc = np.vectorize(risk_cal, excluded=["paras"])
    for i, item in enumerate(eval_list):
        mi, ma, pa = item
        y_axis = vfunc(x_axis, mi, ma, a=pa[0], n=pa[1])
        print(np.max(y_axis))

        ax1 = plt.subplot(3, 3, i + 1)
        ax1.plot(x_axis, y_axis)
        ax1.set_title(f"min[{mi}]_max[{ma}]_p{pa}")
    plt.show()


if __name__ == '__main__':
    plot_formula()
    # POP_SIZE = 1000
    # mu = [0, 0]
    # sigma = [1, 1]
    # FINAL_GEN = 10
    # paras_list = [[random.uniform, 0, 100], [random.uniform, -10, 10]]
    # cost_func = lambda paras, x=1, min=0, max=1000 : risk_cal(x, min, max, paras)
    # optimize_main(paras_list, POP_SIZE, mu, sigma, FINAL_GEN, cost_func)


def plot_history(df_history, fn="plot.png"):
    ax1 = plt.subplot(321)
    ax1.plot(range(len(df_history)), df_history["total"])
    ax1.set_title("total")

    ax4 = plt.subplot(322)
    ax4.plot(range(len(df_history)), df_history["crypto_price"])
    ax4.set_title("crypto_price")

    ax2 = plt.subplot(323)
    ax2.plot(range(len(df_history)), df_history["crypto_amount"])
    ax2.set_title("crypto_amount")

    ax3 = plt.subplot(324)
    ax3.plot(range(len(df_history)), df_history["JPY"])
    ax3.set_title("JPY")

    ax4 = plt.subplot(325)
    ax4.plot(range(len(df_history)), df_history["total_fee"])
    ax4.set_title("total_fee")

    if fn:
        plt.savefig(fn)
    # plt.show()
    plt.close()