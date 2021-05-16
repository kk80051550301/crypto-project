import os

import cryptocompare
import collections 
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from formula import risk_cal 


def percent_calc(value, pre_value):
    return (value - pre_value) / pre_value * 100


def buy_unit(buy_price, crypto_price):
    base = crypto_price * 0.0001
    return (buy_price // base) * base


def sell_unit(sell_price):
    return buy_unit(sell_price, 1)


def plots(history):
    df = pd.DataFrame(history)
    df.to_csv("history.csv")
    
    ax1 = plt.subplot(321)
    ax1.plot(range(len(df)), df["total"])
    ax1.set_title("total")

    ax4 = plt.subplot(322)
    ax4.plot(range(len(df)), df["crypto_price"])
    ax4.set_title("crypto_price")

    ax2 = plt.subplot(323)
    ax2.plot(range(len(df)), df["crypto_amount"])
    ax2.set_title("crypto_amount")

    ax3 = plt.subplot(324)
    ax3.plot(range(len(df)), df["JPY"])
    ax3.set_title("JPY")

    ax4 = plt.subplot(325)
    ax4.plot(range(len(df)), df["total_fee"])
    ax4.set_title("total_fee")

    plt.savefig("plot.png")
    plt.show()
    return


def get_close(crypto_name="BTC", limit=24, end=datetime.now(), currency="JPY", cache_path="cache"):

    fn = os.path.join(cache_path, f"{crypto_name}_{currency}_{end.date()}_{limit}.csv")
    if os.path.exists(fn):
        df = pd.read_csv(fn)
        return df

    values = []
    while limit > 0:
        amount = min(1920, limit)
        tmp = cryptocompare.get_historical_price_hour(crypto_name, currency, limit=amount, toTs=end)
        end -= timedelta(hours=amount)
        limit -= amount
        values.extend(tmp)

    df = pd.DataFrame(values)
    df.sort_values("time", inplace=True)
    df.drop_duplicates(subset="time", inplace=True)

    df["perc_val"] = df.apply(lambda row: percent_calc(row["close"], row["open"]), axis=1)
    df["price"] = df["close"]
    df.to_csv(fn, index=False)
    return df


def simulate(crypto_amount, assets_jpy, coef, crypto_type, end,
             hours):
    crypto_amount, assets_jpy, history = part_simulate(crypto_amount, assets_jpy, coef, crypto_type, end, hours)
    return history


def part_simulate(crypto_amount, assets_jpy, coef, crypto_name, end,
                  hours, fee_rate=0.0012):
    history = []
    close_values = get_close(crypto_name=crypto_name, limit=hours, end=end)

    total_fee = 0
    for index, event in close_values.iterrows():
        state = "nothing"
        fee = 0
        rate = risk_cal(event["perc_val"], coef[0], coef[1], coef[2], coef[3])
        if event["perc_val"] < 0:
            # buy crypto
            buy_cost = buy_unit(assets_jpy * rate, event["price"])
            if buy_cost > 0:
                fee = buy_cost * fee_rate
                assets_jpy -= (buy_cost + fee)
                crypto_amount += buy_cost / event["price"]
                state = "buy"
        elif event["perc_val"] > 0:
            # sell crypto
            sell_amount = sell_unit(crypto_amount * rate)
            if sell_amount > 0:
                crypto_amount -= sell_amount
                sell_price = sell_amount * event["price"]
                fee = sell_price * fee_rate
                assets_jpy += sell_price - fee
                state = "sell"
        total_fee += fee
        crypto_value = event["price"] * crypto_amount
        total = assets_jpy + crypto_value
        history.append({"time": event['time'], "crypto_price": event["price"],
                        "percent_val": event["perc_val"],
                        "JPY": assets_jpy, "crypto_amount": crypto_amount,
                        "crypto_value": crypto_value,
                        "total_fee": total_fee,
                        "total": total, "state": state})
    return crypto_amount, assets_jpy, history


def run():
    # end = datetime(2021, 4, 22)
    end = datetime.today()
    hour = 3840
    INITIAL_ASSETS = assets_jpy = 200000
    crypto_amount = 0
    crypto_name = "ETH"
    coef = (0.5, 1.5, 0.00075, 2) 
    history = simulate(crypto_amount, assets_jpy, coef, crypto_name, end, hour)
    rst = history[-1]
    count = collections.defaultdict(int)

    for term in history:
        count[term['state']] += 1
        
    print(f"jpy assets : {rst['JPY']}")
    print(f"crypto assets : {rst['crypto_amount']}")
    print(f"total assets : {rst['total']}")
    print(f"earn percetange : {(rst['total'] - INITIAL_ASSETS) / INITIAL_ASSETS * 100}%")
    print(f"count :{count}")
    plots(history)


if __name__ == "__main__":
    # main()
    run()
