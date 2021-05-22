import os

import cryptocompare
import collections
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from formula import risk_cal
from tools.retrieve_data import get_historical_price


def buy_unit(buy_price, crypto_price):
    base = crypto_price * 0.0001
    return (buy_price // base) * base


def sell_unit(sell_price):
    return buy_unit(sell_price, 1)


def plots(df_history, fn="plot.png"):
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


def simulate(id, crypto_amount, assets_jpy, coef, crypto_name, start, end, result_root="simulations/", save=False,
             verbose=False):
    history = run_simulation(crypto_amount, assets_jpy, coef, crypto_name, start, end)

    final_state = history[-1]
    # Count of (buy/sell/nothing)
    count = collections.defaultdict(int)

    for term in history:
        count[term['state']] += 1

    summary = {
        "earn_rate": (final_state['total'] - assets_jpy) / assets_jpy,
        "final_total": final_state['total'],
        "final_jpy": final_state["JPY"],
        "final_crypto_amount": final_state['crypto_amount'],
        **count
    }

    if save:
        sub_path = f"#{id}_{crypto_name}_{assets_jpy:.1f}_coef[{'_'.join(map(lambda x: str(x), coef))}]_{start.date()}_{end.date()}"
        result_path = os.path.join(result_root, sub_path)
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        history_file = os.path.join(result_path, "history.xlsx")
        plot_file = os.path.join(result_path, "plot.png")

        df_history = pd.DataFrame(history)
        df_history.to_excel(history_file)
        plots(df_history, plot_file)

    if verbose:
        print(f"Result of running: {sub_path}:")
        print(summary)

    return summary


def run_simulation(crypto_amount, assets_jpy, coef, crypto_name, start, end, fee_rate=0.0012):
    history = []
    close_values = get_historical_price(crypto_name=crypto_name, start=start, end=end)

    total_fee = 0
    for index, event in close_values.iterrows():
        state = "nothing"
        fee = 0
        rate = risk_cal(event["perc_val"], *coef)
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
    return history


def run():
    parameter_file = "input/parameters.xlsx"
    simulation_result_base = "simulations"
    result_file = os.path.join(simulation_result_base, f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")

    df_para = pd.read_excel(parameter_file)

    summary_all = pd.DataFrame()
    for i, row in df_para.iterrows():
        id = row["#"]
        done = row["done"]
        if done == "Yes":
            continue
        start = row["start_date"]
        end = row["end_date"]
        assets_jpy = row["initial_jpy"]
        crypto_amount = row["initial_crypto"]
        crypto_name = row["crypto_name"]
        coef = (
            row["coef_min"],
            row["coef_max"],
            row["coef_a"],
            row["coef_slop"],
        )

        summary = simulate(
            id=id,
            crypto_amount=crypto_amount,
            assets_jpy=assets_jpy,
            coef=coef,
            crypto_name=crypto_name,
            start=start,
            end=end,
            result_root=simulation_result_base,
            save=True,
            verbose=True)
        summary["#"] = id
        summary_all = summary_all.append(summary, ignore_index=True)

        try:
            summary_all.to_excel(result_file, index=False)
        except PermissionError as e:
            summary_all.to_excel(result_file.replace(".xlsx", ".1.xlsx"), index=False)


if __name__ == "__main__":
    # main()
    run()
