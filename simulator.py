import os

import collections
import pandas as pd
from datetime import datetime
from tools.utils import risk_cal, plot_history
from tools.retrieve_data import get_historical_price


def buy_unit(buy_price, crypto_price):
    base = crypto_price * 0.0001
    return (buy_price // base) * base


def sell_unit(sell_price):
    return buy_unit(sell_price, 1)


def run_simulation(crypto_amount, assets_jpy, coef, df_historical_price, fee_rate=0.0012):
    history = []

    total_fee = 0
    for index, event in df_historical_price.iterrows():
        state = "nothing"
        fee = 0
        rate = risk_cal(event["perc_val"], *coef)
        if rate < 0:
            buy_rate = - rate
            if buy_rate < 1:
                # buy crypto
                buy_cost = buy_unit(assets_jpy * buy_rate, event["price"])
                if buy_cost > 0:
                    fee = buy_cost * fee_rate
                    assets_jpy -= buy_cost + fee
                    crypto_amount += buy_cost / event["price"]
                state = "buy"
            else:
                print(f"WARNING: you are buying more than your currency asset, skip! rate: {rate}")
        elif rate > 0:
            if rate < 1:
                # sell crypto
                sell_amount = sell_unit(crypto_amount * rate)
                if sell_amount > 0:
                    crypto_amount -= sell_amount
                    sell_price = sell_amount * event["price"]
                    fee = sell_price * fee_rate
                    assets_jpy += sell_price - fee
                    state = "sell"
            else:
                print(f"WARNING: you are selling more than your crypto asset, skip! rate: {rate}")

        total_fee += fee
        crypto_value = event["price"] * crypto_amount
        total = assets_jpy + crypto_value
        history.append({"time": event['time'],
                        "percent_val": event["perc_val"],
                        "rate": rate,
                        "crypto_price": event["price"],
                        "JPY": assets_jpy, "crypto_amount": crypto_amount,
                        "crypto_value": crypto_value,
                        "total_fee": total_fee,
                        "total": total, "state": state})
    return history


def simulate(id, crypto_amount, assets_jpy, coef, crypto_name, start, end, result_root="simulations/", save=False,
             verbose=False):

    df_historical_price = get_historical_price(crypto_name=crypto_name, start=start, end=end)
    history = run_simulation(crypto_amount, assets_jpy, coef, df_historical_price)

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
        plot_history(df_history, plot_file)

    if verbose:
        print(f"Result of running: {sub_path}:")
        print(summary)

    return summary


def run():
    parameter_file = "input/parameters.xlsx"
    simulation_result_base = "output/simulations/"
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
