from crypto import run_ga
from optimize.crypto_optimize import optimize_main
import random

if __name__ == "__main__" :
    POP_SIZE = 50
    mu = [0, 0]
    sigma = [1, 1]
    FINAL_GEN = 20
    paras_list = [[random.uniform, 0, 2], [random.uniform, 0, 2]]
    hour = 72
    cost_func = lambda paras, min=0.05, max=0.7, hour=hour : run_ga(hour, coef = (min, max, paras))

    max_inds = optimize_main(paras_list, POP_SIZE, mu, sigma, FINAL_GEN, cost_func)
    print(max_inds)