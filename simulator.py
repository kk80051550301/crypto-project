import os

import collections
import pandas as pd
from datetime import datetime

from scenario import Scenario
from strategy import get_stg_class
from tools.utils import plot_history, calc_earn_rate
from tools.retrieve_data import get_historical_price


def legitimize_buy_cost(buy_cost, crypto_price):
    """Calculate the legitimate cost (in currency) of crypto to buy

    :param buy_cost: The cost (in currency) you want to spend to buy the crypto
    :param crypto_price: The current price of the crypto (in currency)
    :return: the legitimate cost
    """
    expected_amount = buy_cost / crypto_price
    legitimate_amount = legitimize_amount(expected_amount)
    return legitimate_amount * crypto_price


def legitimize_amount(crypto_amount):
    """ Calculate the legitimate amount of crypto to trade

    :param crypto_amount: the amount of crypto you want to trade
    :return: the legitimate amount of crypto you can trade
    """
    minimum_unit_to_trade = 0.0001  # bitbank
    return (crypto_amount // minimum_unit_to_trade) * minimum_unit_to_trade


def run_simulation(crypto_amount, assets_jpy, strategy, df_historical_price, fee_rate=0.0012):
    history = []

    total_fee = 0
    for index, event in df_historical_price.iterrows():
        state = "nothing"
        fee = 0
        # rate = risk_cal(event["perc_val"], *coef)
        rate = strategy.calc_buy_sell_rate(event["perc_val"])
        trade_value = 0  # amount of trade in currency (e.g., JPY)
        if rate < 0:
            buy_rate = - rate
            if buy_rate < 1:
                # buy crypto
                buy_cost = legitimize_buy_cost(assets_jpy * buy_rate, event["price"])
                if buy_cost > 0:
                    fee = buy_cost * fee_rate
                    assets_jpy -= buy_cost + fee
                    crypto_amount += buy_cost / event["price"]
                    state = "buy"
                    trade_value = buy_cost
            else:
                print(f"WARNING: you are buying more than your currency asset, skip! rate: {rate}")
        elif rate > 0:
            if rate < 1:
                # sell crypto
                sell_amount = legitimize_amount(crypto_amount * rate)
                if sell_amount > 0:
                    crypto_amount -= sell_amount
                    sell_price = sell_amount * event["price"]
                    fee = sell_price * fee_rate
                    assets_jpy += sell_price - fee
                    state = "sell"
                    trade_value = sell_price
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
                        "trade_value": trade_value,
                        "total": total, "state": state})
    return history


def simulate(id, crypto_amount, assets_jpy, stg, scenario, result_root="simulations/", save=False,
             verbose=False):
    history = run_simulation(crypto_amount, assets_jpy, stg, scenario.data)

    final_state = history[-1]
    # Count of (buy/sell/nothing)
    count = collections.defaultdict(int)

    for term in history:
        count[term['state']] += 1

    summary = {
        "earn_rate": calc_earn_rate(final_state['total'], assets_jpy),
        "final_total": final_state['total'],
        "final_jpy": final_state["JPY"],
        "final_crypto_amount": final_state['crypto_amount'],
        **count
    }

    sub_path = f"#{id}_{scenario.path_str()}_{stg.path_str()}]"
    if save:
        result_path = os.path.join(result_root, sub_path)
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        history_file = os.path.join(result_path, "history.xlsx")
        plot_file = os.path.join(result_path, "plot.png")
        script_file = os.path.join(result_path, "pine_scripts.txt")

        df_history = pd.DataFrame(history)
        df_history.to_excel(history_file)
        plot_history(df_history, plot_file)
        scripts = create_pine_script(df_history, title=f"History #{id:d}")
        with open(script_file, 'w') as f:
            f.write(scripts)

    if verbose:
        print(f"Result of running: {sub_path}:")
        print(summary)

    return summary


def create_pine_script(df_history, title="History", max_lines=200):
    lines = [
        "// @version=4\n\nstudy(\"{}\", overlay=true, max_labels_count=500)\n".format(title),
    ]

    count = 0
    for i, row in df_history.iterrows():

        if row["state"] == "nothing":
            continue

        count += 1
        if count > max_lines:
            break

        if row["state"] == "sell":
            color = "color.red"
            text = "Sell\\n"
        elif row["state"] == "buy":
            color = "color.green"
            text = "Buy\\n"
        text += "{0:.0f}".format(row["trade_value"])

        time = datetime.fromtimestamp(row["time"])
        line = 'label.new(timestamp("GMT+9",{time}),close,xloc=xloc.bar_time,' \
               'yloc=yloc.abovebar,text="{text}",style=label.style_labeldown,color={color})' \
            .format(time=",".join(map(str, [time.year, time.month, time.day, time.hour, time.minute])),
                    text=text, color=color)
        lines.append(line)

    return "\n".join(lines)


def run():
    parameter_file = "input/parameters.xlsx"
    simulation_result_base = "output/simulations/"
    simulation_details_base = os.path.join(simulation_result_base, "runs")
    result_file = os.path.join(simulation_result_base, f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")

    df_para = pd.read_excel(parameter_file)

    summary_all = pd.DataFrame()
    for i, row in df_para.iterrows():
        id = row["#"]
        done = row["done"]
        if done == "Yes":
            continue
        assets_jpy = row["initial_jpy"]
        crypto_amount = row["initial_crypto"]

        names = list(row.index)
        purchase_stg = row["purchase_stg"]
        param_count = row["param_count"]
        start = names.index("param_count") + 1
        params = row[start: start + param_count]

        stg_class = get_stg_class(purchase_stg)
        if not stg_class:
            continue
        stg = stg_class(*params)

        scenario = Scenario(crypto_name=row["crypto_name"],
                            start=row["start_date"],
                            end=row["end_date"],
                            currency="JPY")

        summary = simulate(
            id=id,
            crypto_amount=crypto_amount,
            assets_jpy=assets_jpy,
            stg=stg,
            scenario=scenario,
            result_root=simulation_details_base,
            save=True,
            verbose=True)
        summary["#"] = id
        summary_all = summary_all.append(summary, ignore_index=True)

        try:
            summary_all.to_excel(result_file, index=False)
        except PermissionError as e:
            summary_all.to_excel(result_file.replace(".xlsx", ".1.xlsx"), index=False)


def profile_simulation():
    import time
    import statistics

    n = [3, 1000]  # Run 3 * 1000 times
    n = [3, 100]  # Run 3 * 100 times

    crypto_name = "ETH"
    # start = datetime(2021, 1, 1)
    start = datetime(2021, 4, 20)
    end = datetime(2021, 4, 22)
    df_historical_price = get_historical_price(crypto_name=crypto_name, start=start, end=end)
    crypto_amount = 0
    assets_jpy = 200000
    coef = [0.077137627, 0.147341631, 0.003388124, 0.585231967]
    stg_class = get_stg_class("ExpRatioStrategy")
    stg = stg_class(*coef)

    res = []
    n_data_records = 0
    for i in range(n[0]):
        start = time.time()
        for j in range(n[1]):
            history = run_simulation(crypto_amount, assets_jpy, stg, df_historical_price)
            n_data_records = len(history)

        elapsed = time.time() - start
        print(f"Time cost of run #{i + 1:d} of [{n[1]:d}] times with [{n_data_records:d}] data records: {elapsed:.5f}s")
        res.append(elapsed)

    avg_single_run = statistics.mean(res) / n[1]
    avg_single_record = avg_single_run / n_data_records
    print(f"Avg time cost of single run: {avg_single_run:.5f}s")
    print(f"Avg time cost of single record: {avg_single_record:.8f}s")


def test_trade_unit():
    crypto_amount = 0.00022
    res = legitimize_amount(crypto_amount)
    assert res == 0.0002

    jpy = 0.00052
    crypto_price = 2
    res = legitimize_buy_cost(jpy, crypto_price)
    print(res)

    assert res == 0.0004


if __name__ == "__main__":
    run()
    # profile_simulation()
    # test_trade_unit()
