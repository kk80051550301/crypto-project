from matplotlib import pyplot as plt
import pandas as pd


def percent_calc(value, pre_value):
    # return percentage(unit is 1%)
    return (value - pre_value) / pre_value * 100


def calc_profit(history):
    df = pd.DataFrame(history)
    buy_total_cost = df[df["state"]=="buy"]["trade_value"].sum()
    sell_earn = df[df["state"]=="sell"]["trade_value"].sum()
    sell_earn += df.at[len(df)-1, "crypto_value"]
    profit = percent_calc(sell_earn, buy_total_cost)
    # print(df.head())
    # print(f"buy cost : \n{buy_total_cost}")
    # print(f"sell earn + crypto_currancy value : \n{sell_cost}")
    # print(f"profit : {profit} %")
    return profit


def calc_earn_rate(final_asset, initial_asset):
    earn_rate = percent_calc(final_asset, initial_asset)
    return earn_rate


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


if __name__ == '__main__':
    pass
