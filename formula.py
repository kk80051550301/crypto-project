import matplotlib.pyplot as plt
import numpy as np
import math


def risk_cal(x, min, max, a, slop):
    if abs(x) > 2:
        x = 2 * x / abs(x)
    elif abs(x) < min:
        return 0
    return a * math.exp(slop * abs(x))


def plot_formula():

    eval_list = [
        (0.5, 1.5, 0.00075, 2),
        (0, 2, 0.000724, 3),
        (0, 2, 0.000724, 4),
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