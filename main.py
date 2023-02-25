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
        self.priority = 0

    def get_data(self):
        return self.high, self.low, self.open, self.close, self.stamp

    def __str__(self):
        return f"High: {self.high} | Low: {self.low} | Open: {self.open} | Close: {self.close} | Priority: {self.priority} | Stamp: {self.stamp}\n"


class Graph:
    def __init__(self):
        self.data = None
        self.sp = []

        self.pvtss = []
        self.pvtsb = []
        self.fvgb = []
        self.fvgs = []
        self.pvtmax = 10

    def update(self, tick, start, end):
        data = pdr.get_data_moex(tick, start=start,
                                 end=end)

        new_data = (Candle(data['HIGH'][date],
                           data['LOW'][date],
                           data['OPEN'][date],
                           data['CLOSE'][date],
                           date) for date in data['OPEN'].keys())
        for cndl in new_data:
            self.sp.append(cndl)
        self.set_pivots()
        self.set_fvgs()

    def show(self):
        self.data['CLOSE'].plot(grid=True)
        plt.show()

    def set_pivots(self, n=3):
        if self.pvtmax != n:
            n = n + (n % 2 == 0)
            m = self.sp
            for i in range(n // 2, len(m) - (n // 2)):
                if all(m[i + j].high < m[i].high for j in (a for a in range(-(n // 2), (n // 2) + 1) if a != 0)):
                    # if dnd or not any(m[i].high < j.high and m[i].stamp < j.stamp for j in self.sp):
                    if m[i].priority == 0:
                        self.pvtss.append(m[i])
                    m[i].priority = n

                if all(m[i + j].low > m[i].low for j in (a for a in range(-(n // 2), (n // 2) + 1) if a != 0)):
                    # if dnd or not any(m[i].low > j.low and m[i].stamp < j.stamp for j in self.sp):
                    if m[i].priority == 0:
                        self.pvtsb.append(m[i])
                    m[i].priority = n
            self.set_pivots(n + 1)

    def set_fvgs(self, dnd=False):
        for i in range(1, len(self.sp) - 1):
            a = self.sp[i - 1]
            b = self.sp[i + 1]
            if a.low > b.high:
                # if dnd or not any(i.high < b.high and b.stamp < i.stamp for i in self.sp):
                self.fvgs.append((a, b))
            if a.high < b.low:
                # if dnd or not any(i.low < b.low and b.stamp < i.stamp for i in self.sp):
                self.fvgb.append((a, b))

    def strategy(self, priority=3):
        sell_cond = False
        sell_cndl = None
        buy_cond = False
        buy_cndl = None
        break_cndl = None
        for cndl in self.sp:
            if not sell_cond:
                for scndl in self.pvtsb:
                    if scndl.low > cndl.low and scndl.stamp < cndl.stamp:
                        sell_cond = True
                        sell_cndl = scndl
                        self.pvtsb.remove(scndl)
                        break
            if sell_cond:
                for scndl in self.pvtss:
                    if cndl.high > scndl.high and scndl.stamp < cndl.stamp:
                        buy_cond = True
                        buy_cndl = scndl
                        break_cndl = cndl
                        self.pvtss.remove(scndl)
                        print(sell_cndl, buy_cndl, break_cndl)
                        print()
                        sell_cond = False
                        sell_cndl = None
                        buy_cond = False
                        buy_cndl = None
                        break_cndl = None

                        break


if __name__ == '__main__':
    ticker = 'USD000UTSTOM'
    start = datetime.datetime(2022, 12, 21)
    end = datetime.datetime.now()
    graph = Graph()
    graph.update(ticker, start, end)
    graph.strategy()
