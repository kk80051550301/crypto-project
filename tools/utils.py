from matplotlib import pyplot as plt


def percent_calc(value, pre_value):
    # return percentage(unit is 1%)
    return (value - pre_value) / pre_value * 100


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
