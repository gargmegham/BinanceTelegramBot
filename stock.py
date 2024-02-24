import numpy as np
import pandas as pd
from binance import Binance


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.exchange = Binance(filename="credentials.txt")
        self.closes, self.highs, self.lows, self.opens, self.volumes, self.rsi = (
            self.fetch_stock_data()
        )

    def fetch_stock_data(self):
        stock_data = self.exchange.GetSymbolKlines(self.ticker, "15m", 100)
        ticker_24hr = self.exchange.Get24hrTickerFutures(self.ticker)
        stock_data = stock_data.set_index("date")
        stock_data["time"] = [d.timestamp() for d in stock_data.index]
        stock_data["close"] = pd.to_numeric(stock_data["close"], downcast="float")
        closes = stock_data["close"]
        highs = stock_data["high"]
        lows = stock_data["low"]
        opens = stock_data["open"]
        volumes = stock_data["volume"]
        rsi = self.calculate_rsi(closes)
        return closes, highs, lows, opens, volumes, rsi

    def calculate_rsi(self, prices, n=14):
        deltas = np.diff(prices)
        seed = deltas[: n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100.0 - 100.0 / (1.0 + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.0
            else:
                upval = 0.0
                downval = -delta

            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n

            rs = up / down
            rsi[i] = 100.0 - 100.0 / (1.0 + rs)

        return rsi

    def simple_moving_average(self, period, values=None):
        values = self.closes if values is None else values
        weights = np.repeat(1.0, period) / period
        smas = np.convolve(values, weights, "valid")
        return smas

    def exponential_moving_average(self, period, values=None):
        values = self.closes if values is None else values
        weights = np.exp(np.linspace(-1.0, 0.0, period))
        weights /= weights.sum()
        ema = np.convolve(values, weights, mode="full")[: len(values)]
        ema[:period] = ema[period]
        return ema

    def macd(self, x, slow=26, fast=12):
        emaslow = self.exponential_moving_average(slow, x)
        emafast = self.exponential_moving_average(fast, x)
        return emaslow, emafast, emafast - emaslow
