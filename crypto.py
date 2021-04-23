import cryptocompare
import collections 
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date


# magic rate = 1.016 [ETH /2hrs -> 12hrs 10%]

def get_close(crypto_name="BTC", limit=24, timestamp=1619009695):
    rst = []
    pre_val = 1
    tmp = cryptocompare.get_historical_price_hour(crypto_name, 'JPY', limit=limit, toTs=date.fromtimestamp(timestamp))
    for i, hr in enumerate(tmp):
        if i % 2 == 1:
            continue
        rst.append({"cost":hr["close"], "perc_val":percent_calc(hr["close"], pre_val), "time":hr["time"]})
        pre_val = hr['close']
    return rst[1:]


def percent_calc(value, pre_value):
    return (value - pre_value) / pre_value * 100


def buy_unit(buy_price, crypto_price):
    base = crypto_price * 0.0001
    return (buy_price // base) * base


def sell_unit(sell_price):
    return buy_unit(sell_price, 1)


def plots(history):
    df = pd.DataFrame(history)
    print(df.head())
    
    ax1 = plt.subplot(131)
    ax1.plot(range(len(df)), df["total"])
    ax1.set_title("total")

    ax2 = plt.subplot(132)
    ax2.plot(range(len(df)), df["crypto"])
    ax2.set_title("crypto")

    ax3 = plt.subplot(133)
    ax3.plot(range(len(df)), df["JPY"])
    ax3.set_title("JPY")
    plt.show()
    return


def main():
    MAGIC_BUY = 1
    MAGIC_SELL = 1
    INITIAL_ASSETS = assets_jpy = 200000
    buy_rate = 0.01
    crypto_assets = 0
    sell_rate = 0.01
    count = collections.defaultdict(int)
    history = []
    state = ""

    close_values = get_close(crypto_name="BTC", limit=1920)
    for event in close_values:
        if event["perc_val"] < -1 * MAGIC_BUY:
            # buy crypto
            buy_cost = buy_unit(assets_jpy * buy_rate, event['cost'])
            assets_jpy -= buy_cost
            crypto_assets += buy_cost / event["cost"]
            count['buy'] += 1
            state = "buy"
        elif event["perc_val"] > 1 * MAGIC_SELL:
            # sell crypto
            sell_cost = sell_unit(crypto_assets * sell_rate)
            crypto_assets -= sell_cost
            assets_jpy += sell_cost * event["cost"]
            count['sell'] += 1
            state = "sell"
        else: 
            state = "nothing"
        count['total'] += 1
        total = assets_jpy + close_values[-1]['cost'] * crypto_assets
        history.append({"time": event['time'], "cost": event["cost"], "percent_val": event["perc_val"],
                        "JPY": assets_jpy, "crypto": crypto_assets, "total": total, "state": state})

    print(f"jpy assets : {assets_jpy}")
    print(f"crypto assets : {crypto_assets}")
    print(f"total assets : {total}")
    print(f"earn percetange : {(total - INITIAL_ASSETS) / INITIAL_ASSETS * 100} %")
    print(f"buy times : {count['buy']}, sell times : {count['sell']}, total times : {count['total']}")
    plots(history)


if __name__ == "__main__":
    main()

