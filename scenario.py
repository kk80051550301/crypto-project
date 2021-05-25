from datetime import datetime
from dateutil.relativedelta import relativedelta

from tools.retrieve_data import get_historical_price


class Scenario:

    def __init__(self, crypto_name="BTC",
                 start=datetime.now() - relativedelta(months=6),
                 end=datetime.now(),
                 currency="JPY",
                 window="hour",
                 id_="",
                 type_="",
                 comment=""):
        self.crypto_name = crypto_name
        self.start = start
        self.end = end
        self.currency = currency
        self.id_ = id_
        self.type_ = type_
        self.comment = comment
        self.window = window
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self.populate_data()
        return self._data

    def populate_data(self):
        self._data = get_historical_price(crypto_name=self.crypto_name, start=self.start, end=self.end,
                                          currency=self.currency)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return f"<{self.__class__.__name__}({self.type_}, {self.crypto_name}, {self.start}, {self.end})>"

    def path_str(self):
        return f"sc[{self.type_}_{self.crypto_name}_{self.start.strftime('%Y%m%d')}_{self.end.strftime('%Y%m%d')}]"
