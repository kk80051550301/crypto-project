import matplotlib.pyplot as plt
import numpy as np
import math
import random
from optimize.crypto_optimize import optimize_main


# def risk_cal(x, min, max, a, b):
#     # set max invest value
#     if abs(x) > max:
#         x = max
#     # do none if previous rate < min
#     elif abs(x) < min:
#         return 0
#     return a * math.exp(b * abs(x))

def risk_cal(change_rate, min_val, max_val, a, n):
    # def invest index func
    # print(x, min_val, max_val, paras)
    # a, n = paras
    try:
        invest_index = a * math.exp(n * abs(change_rate))
    except OverflowError as e:
        print(change_rate, min_val, max_val, a, n)
        print(e)
        raise e
    invest_index = min(max(invest_index, min_val), max_val)
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
