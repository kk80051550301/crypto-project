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
    x_axis = np.arange(-5, 5, 0.01)
    vfunc = np.vectorize(risk_cal)
    y_axis = vfunc(x_axis, 0, 2, 0.000724, 3)
    print(np.max(y_axis))
    plt.plot(x_axis, y_axis)
    plt.show()


if __name__ == '__main__':
    plot_formula()