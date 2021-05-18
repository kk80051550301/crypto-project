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

def risk_cal(x, min, max, paras):
    # def invest index func
    print(x, min, max, paras)
    invest_index = paras[0] * math.exp(paras[1]) * abs(x)
    # set max invest index
    if invest_index >= max:
        invest_index = max
    # set min invest index
    elif invest_index <= min:
        invest_index = min
    return (invest_index, )

def plot_formula():

    eval_list = [
        (0.5, 1.5,(0.00075, 2)),
        (0, 2, (0.000724, 3)),
        (0, 2, (0.000724, 4)),
    ]

    x_axis = np.arange(-5, 5, 0.01)
    vfunc = np.vectorize(risk_cal)
    for i, eval in enumerate(eval_list):
        y_axis = vfunc(x_axis, *eval)
        print(np.max(y_axis))

        ax1 = plt.subplot(3, 3, i+1)
        ax1.plot(x_axis, y_axis)
        ax1.set_title("total")
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
    