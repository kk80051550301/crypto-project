import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from cryptocompare import cryptocompare
from tools.utils import percent_calc


def get_historical_price(crypto_name="BTC",
                         start=datetime.now() - relativedelta(months=6),
                         end=datetime.now(),
                         currency="JPY",
                         cache_path="cache"):
    limit = (end - start).days * 24
    fn = os.path.join(cache_path, f"{crypto_name}_{currency}_{start.date()}_{end.date()}.csv")
    if os.path.exists(fn):
        df = pd.read_csv(fn)
        return df

    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    values = []
    while limit > 0:
        amount = min(1920, limit)
        tmp = cryptocompare.get_historical_price_hour(coin=crypto_name, currency=currency, limit=amount, toTs=end)
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


def test():
    parameter_file = "../input/market_patterns.xlsx"
    # simulation_result_base = "simulations"
    # result_file = os.path.join(simulation_result_base, f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")

    df_para = pd.read_excel(parameter_file)

    for i, row in df_para.iterrows():
        id = row["#"]
        crypto_name = row["crypto_name"]
        start = row["start"]
        end = row["end"]

        get_historical_price(crypto_name=crypto_name,
                             start=start,
                             end=end,
                             currency="USD")


if __name__ == '__main__':
    test()
