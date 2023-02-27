import datetime
import numpy as np
import pandas as pd
import requests


class Candle:
    def __init__(self, open_time, open, high, low, close, volume, close_time, quote, num_of_trades, *args):
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.open_time = open_time
        self.close_time = close_time
        self.quote = quote
        self.num_of_trades = num_of_trades
        self.volume = volume
        self.priority_buy = 0
        self.priority_sell = 0

    def __str__(self):
        return f"High: {self.high} | Low: {self.low} | Open: {self.open} | Close: {self.close} | Time: {datetime.datetime.fromtimestamp(self.open_time / 1000)}\n"


class Data:
    def __init__(self, symbol, interval, start_time, end_time):
        self.symbol = symbol
        self.interval = interval
        self.start_time = start_time.timestamp() * 1000
        self.end_time = end_time.timestamp() * 1000

    def get_data(self):
        params = {'symbol': self.symbol,
                  'interval': self.interval,
                  'startTime': self.start_time,
                  'endTime': self.end_time}
        r = requests.get('https://fapi.binance.com/fapi/v1/klines', params=params)
        res = np.array(list(map(lambda x: Candle(*x), r.json())))
        return res


class Graph:
    def __init__(self):
        self.sp = np.array([])
        self.pvtss = np.array([])
        self.pvtsb = np.array([])
        self.fvgb = np.array([])
        self.fvgs = np.array([])
        self.pvtmax = 10

    def update(self, sp):
        self.sp = np.append(self.sp, sp)
        self.set_pivots()
        self.set_fvgs()

    def set_pivots(self, n=3):
        if self.pvtmax != n:
            n = n + (n % 2 == 0)
            m = self.sp
            for i in range(n // 2, len(m) - (n // 2)):
                if all(m[i + j].high <= m[i].high for j in (a for a in range(-(n // 2), (n // 2) + 1) if a != 0)):
                    if m[i] not in self.pvtss:
                        self.pvtss = np.append(self.pvtss, m[i])
                    m[i].priority_sell = n

                if all(m[i + j].low >= m[i].low for j in (a for a in range(-(n // 2), (n // 2) + 1) if a != 0)):
                    if m[i] not in self.pvtsb:
                        self.pvtsb = np.append(self.pvtsb, m[i])
                    m[i].priority_buy = n
            self.set_pivots(n + 1)

    def set_fvgs(self):
        for i in range(1, len(self.sp) - 1):
            a = self.sp[i - 1]
            b = self.sp[i + 1]
            if a.low > b.high:
                self.fvgs = np.append(self.fvgs, np.array([a, b]))
            if a.high < b.low:
                self.fvgb = np.append(self.fvgb, np.array([a, b]))
        self.fvgs = np.resize(self.fvgs, (len(self.fvgs) // 2, 2))
        self.fvgb = np.resize(self.fvgb, (len(self.fvgb) // 2, 2))

    def strategy(self):

        buy_l1 = []
        sell_l1 = []
        buy_l2 = []
        sell_l2 = []
        pvtsb = self.pvtsb.copy()
        pvtss = self.pvtss.copy()
        for cndl in self.sp:
            rb = None
            rs = None
            for bstp in pvtsb:
                if cndl.low < bstp.low and cndl.open_time > bstp.open_time:
                    if rb is None or bstp.low < rb.low:
                        rb = bstp
                    pvtsb = np.delete(pvtsb, np.where(pvtsb == bstp))

            for sstp in pvtss:
                if cndl.low < sstp.low and cndl.open_time > sstp.open_time:
                    if rb is None or sstp.low < rb.low:
                        rb = bstp
                    pvtss = np.delete(pvtss, np.where(pvtss == bstp))

            if rb is not None:
                buy_l1.append([rb, cndl])
            if rs is not None:
                sell_l2.append([rs, cndl])
        for pair in buy_l1:
            lst = tuple(filter(lambda x: pair[0].open_time < x.open_time < pair[1].open_time, self.pvtss))
            if lst:
                res = max(lst, key=lambda x: x.open_time)
                for take_cndl in self.sp[int(np.where(self.sp == pair[1])[0]):]:
                    if take_cndl.high > res.high:
                        buy_l2.append((pair[0], res, pair[1], take_cndl))
                        break
        for q in buy_l2:
            print(*q)


if __name__ == '__main__':
    cur = 'ltcusdt'
    tf = '1h'
    start = datetime.datetime(2023, 2, 27, hour=12)
    end = datetime.datetime.now()
    data = Data(cur, tf, start, end)
    mass = data.get_data()
    graph = Graph()
    graph.update(mass)
    graph.strategy()
