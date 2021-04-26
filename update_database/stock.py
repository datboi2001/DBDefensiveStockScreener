from datetime import datetime


class Stock:
    """A class that stores the information of a stock"""

    def __init__(self, symbol, name=None, c_price=None, exchange=None, industry=None, weburl=None, market_cap=None,
                 pe=None, pb=None, ps=None, rg5y=None, roe=None, timestamp=datetime.now(), h_price=None):
        self.symbol = symbol
        self.name = name
        self.c_price = c_price
        self.exchange = exchange
        self.industry = industry
        self.weburl = weburl
        self.market_cap = market_cap
        self.pe = pe
        self.pb = pb
        self.ps = ps
        self.rg5y = rg5y
        self.timestamp = timestamp
        self.h_price = h_price
        self.roe = roe

    def modify_attributes(self, **kwargs):
        """Modify the attributes in __init__"""
        for name, value in kwargs.items():
            self.__dict__[name] = value

    def return_all_attributes(self):
        return self.__dict__
