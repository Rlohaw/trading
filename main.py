import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt


class Candle:
    def __init__(self, high, low, open, close, stamp):
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.stamp = stamp

    def get_data(self):
        return self.high, self.low, self.open, self.close, self.stamp


class Graph:
    def __init__(self, tick, start, end):
        self.data = pdr.get_data_moex(tick, start=start,
                                      end=end)

    def get_candles(self):
        lst = tuple(
            Candle(self.data['HIGH'][date], self.data['LOW'][date], self.data['OPEN'][date], self.data['CLOSE'][date],
                   date) for date in self.data['OPEN'].keys())
        return lst

    def show(self):
        self.data['CLOSE'].plot(grid=True)
        plt.show()

    # def get_pvt(self):
    #     tp = tuple(map(Candle.get_data, self.get_candles()))
    #     for n, (h, l, o, c, s) in enumerate(tp):
    #         if t[n-1] < tp[n] <


apple = Graph('USD000UTSTOM', datetime.datetime(2022, 1, 1), datetime.datetime.now())
apple.get_pvt()
