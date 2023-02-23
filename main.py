import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


class Candle:
    def __init__(self, high, low, open, close, stamp):
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.stamp = stamp
        self.pvt = None

    def get_data(self):
        return self.high, self.low, self.open, self.close, self.stamp

    def __str__(self):
        return f"High: {self.high} | Low: {self.low} | Open: {self.open} | Close: {self.stamp}"


class Graph:
    def __init__(self):
        self.data = None
        self.sp = []
        self.pvtss = []
        self.pvtsb = []
        self.fvgb = []
        self.fvgs = []
        self.pvtn = 3

    def add_candle(self, candle):
        if isinstance(candle, Candle):
            if candle not in self.sp:
                for pvts in self.pvtss:
                    if candle.high > pvts.high:
                        self.pvtss.remove(pvts)
                for pvtb in self.pvtsb:
                    if candle.low < pvtb.low:
                        self.pvtsb.remove(pvtb)
                self.sp.append(candle)

    def update(self, tick, start, end):
        data = pdr.get_data_moex(tick, start=start,
                                 end=end)
        new_data = (Candle(data['HIGH'][date],
                           data['LOW'][date],
                           data['OPEN'][date],
                           data['CLOSE'][date],
                           date) for date in data['OPEN'].keys())
        for cndl in new_data:
            self.add_candle(cndl)
        self.set_pivots()
        self.set_fvgs()

    def show(self):
        self.data['CLOSE'].plot(grid=True)
        plt.show()

    def set_pivots(self):
        n = self.pvtn
        n = n + (n % 2 == 0)
        m = self.sp

        for i in range(n // 2, len(m) - (n // 2)):
            if all(m[i + j].high < m[i].high for j in (a for a in range(-(n // 2), (n // 2) + 1) if a != 0)):
                self.pvtss.append(m[i])
            if all(m[i + j].low > m[i].low for j in (a for a in range(-(n // 2), (n // 2) + 1) if a != 0)):
                self.pvtsb.append(m[i])

        self.pvtsb = list(filter(lambda x: not any(x.low > i.low for i in self.sp if x.stamp < i.stamp), self.pvtsb))
        self.pvtss = list(filter(lambda x: not any(x.high < i.high for i in self.sp if x.stamp < i.stamp), self.pvtss))

    def set_fvgs(self):
        for i in range(1, len(self.sp) - 1):
            a = self.sp[i - 1]
            b = self.sp[i + 1]
            if a.low > b.high:
                self.fvgs.append((a, b))
            if a.high < b.low:
                self.fvgb.append((a, b))

        self.fvgb = list(
            filter(lambda x: not any(i.low < x[1].low for i in self.sp if x[1].stamp < i.stamp), self.fvgb))
        self.fvgs = list(

            filter(lambda x: not any(i.high < x[1].high for i in self.sp if x[1].stamp < i.stamp), self.fvgs))


if __name__ == '__main__':
    ticker = 'USD000UTSTOM'
    start = datetime.datetime(2022, 12, 19)
    end = datetime.datetime.now()
    graph = Graph()
    graph.update(ticker, start, end)
