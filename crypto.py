import cryptocompare
import collections 
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from formula import risk_cal 


def get_close(crypto_name="BTC", limit=24, end=datetime(2021, 4, 22)):
    rst = []
    pre_val = 1
    tmp = cryptocompare.get_historical_price_hour(crypto_name, 'JPY', limit=limit, toTs=end)
    for i, hr in enumerate(tmp):
        if i % 2 == 1:
            continue
        rst.append({"cost": hr["close"], "perc_val": percent_calc(hr["close"], pre_val), "time": hr["time"]})
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
    
    ax1 = plt.subplot(221)
    ax1.plot(range(len(df)), df["total"])
    ax1.set_title("total")

    ax4 = plt.subplot(222)
    ax4.plot(range(len(df)), df["cost"])
    ax4.set_title("cost")

    ax2 = plt.subplot(223)
    ax2.plot(range(len(df)), df["crypto"])
    ax2.set_title("crypto")

    ax3 = plt.subplot(224)
    ax3.plot(range(len(df)), df["JPY"])
    ax3.set_title("JPY")
    plt.show()
    return


def simulate(crypto_assets, assets_jpy, coef, crypto_type, end,
             hours):
    history = []
    end -= timedelta(hours=hours)
    r = hours
    while r > 0:
        if r > 1920:
            end += timedelta(hours=1920)
            crypto_assets, assets_jpy, history = part_simulate(crypto_assets, assets_jpy, coef, crypto_type, end, 1920)
            r -= 1920
        else:
            end += timedelta(hours=r)
            crypto_assets, assets_jpy, history = part_simulate(crypto_assets, assets_jpy, coef, crypto_type, end, r)
            return history


def part_simulate(crypto_assets, assets_jpy, coef, crypto_type, end,
                  hour, history=[]):
    close_values = get_close(crypto_name="ETH", limit=hour, end=end)
    for event in close_values:
        state = "nothing"
        rate = risk_cal(event["perc_val"], coef[0], coef[1], coef[2], coef[3])
        if event["perc_val"] < 0:
            # buy crypto
            buy_cost = buy_unit(assets_jpy * rate, event['cost'])
            if buy_cost > 0:
                fee = buy_cost * 0.0012
                assets_jpy -= (buy_cost + fee)
                crypto_assets += buy_cost / event["cost"]
                state = "buy"
        elif event["perc_val"] > 0:
            # sell crypto
            sell_cost = sell_unit(crypto_assets * rate)
            if sell_cost > 0:
                crypto_assets -= sell_cost
                assets_jpy += sell_cost * event["cost"] * 0.9988
                state = "sell"
        total = assets_jpy + event["cost"] * crypto_assets
        history.append({"time": event['time'], "cost": event["cost"],
                        "percent_val": event["perc_val"],
                        "JPY": assets_jpy, "crypto": crypto_assets,
                        "total": total, "state": state})
    return crypto_assets, assets_jpy, history


def run():
    end = datetime(2021, 4, 22)
    hour = 3840
    INITIAL_ASSETS = assets_jpy = 200000
    crypto_assets = 0
    crypto_type = "ETH"
    coef = (0.5, 1.5, 0.00075, 2) 
    history = simulate(crypto_assets, assets_jpy, coef, crypto_type, end, hour)
    rst = history[-1]
    count = collections.defaultdict(int)

    for term in history:
        count[term['state']] += 1
        
    print(f"jpy assets : {rst['JPY']}")
    print(f"crypto assets : {rst['crypto']}")
    print(f"total assets : {rst['total']}")
    print(f"earn percetange : {(rst['total'] - INITIAL_ASSETS) / INITIAL_ASSETS * 100}%")
    print(f"count :{count}")
    plots(history)


if __name__ == "__main__":
    # main()
    run()
