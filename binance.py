import requests
import json
import hmac
import time
import hashlib


class Binance:
    ORDER_STATUS_NEW = 'NEW'
    ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    ORDER_STATUS_FILLED = 'FILLED'
    ORDER_STATUS_CANCELED = 'CANCELED'
    ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    ORDER_STATUS_REJECTED = 'REJECTED'
    ORDER_STATUS_EXPIRED = 'EXPIRED'

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'

    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    KLINE_INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

    def __init__(self, filename=None):
        self.base = 'https://api.binance.com'

        self.endpoints = {
            "order": '/api/v3/order',
            "testOrder": '/api/v3/order/test',
            "allOrders": '/api/v3/allOrders',
            "klines": '/api/v3/klines',
            "exchangeInfo": '/api/v3/exchangeInfo',
            "24hrTicker": '/api/v3/ticker/24hr',
            "24hrTickerFutures": '/fapi/v1/ticker/24hr',
            "averagePrice": '/api/v3/avgPrice',
            "orderBook": '/api/v3/depth',
            "account": '/api/v3/account'
        }
        self.account_access = False

        if filename is None:
            return

        with open(filename, "r") as f:
            contents = f.read().split('\n')

        self.binance_keys = dict(api_key=contents[0], secret_key=contents[1])
        self.headers = {"X-MBX-APIKEY": self.binance_keys['api_key']}
        self.account_access = True

    def _get(self, url, params=None, headers=None) -> dict:
        try:
            response = requests.get(url, params=params, headers=headers)
            data = json.loads(response.text)
            data['url'] = url
        except Exception as e:
            data = {'code': '-1', 'url': url, 'msg': e}
        return data

    def _post(self, url, params=None, headers=None) -> dict:
        try:
            response = requests.post(url, params=params, headers=headers)
            data = json.loads(response.text)
            data['url'] = url
        except Exception as e:
            data = {'code': '-1', 'url': url, 'msg': e}
        return data

    def GetTradingSymbols(self, quoteAssets=None):
        url = self.base + self.endpoints["exchangeInfo"]
        data = self._get(url)
        if 'code' in data:
            return []

        symbols_list = []
        for pair in data['symbols']:
            if pair['status'] == 'TRADING':
                if quoteAssets is not None and pair['quoteAsset'] in quoteAssets:
                    symbols_list.append(pair['symbol'])
        return symbols_list

    def GetSymbolDataOfSymbols(self, symbols=None):
        url = self.base + self.endpoints["exchangeInfo"]
        data = self._get(url)
        if 'code' in data:
            return []

        symbols_list = []
        for pair in data['symbols']:
            if pair['status'] == 'TRADING':
                if symbols is not None and pair['symbol'] in symbols:
                    symbols_list.append(pair)
        return symbols_list

    def GetSymbolKlinesExtra(self, symbol, interval, limit=1000, end_time=False):
        repeat_rounds = 0
        if limit > 1000:
            repeat_rounds = limit // 1000
        initial_limit = limit % 1000 or 1000

        df = self.GetSymbolKlines(symbol, interval, limit=initial_limit, end_time=end_time)
        while repeat_rounds > 0:
            df2 = self.GetSymbolKlines(symbol, interval, limit=1000, end_time=df['time'][0])
            df = df2.append(df, ignore_index=True)
            repeat_rounds -= 1
        return df

    def GetAccountData(self) -> dict:
        url = self.base + self.endpoints["account"]
        params = {'recvWindow': 6000, 'timestamp': int(round(time.time() * 1000))}
        self.signRequest(params)
        return self._get(url, params, self.headers)

    # Other methods go here...

    def signRequest(self, params: dict):
        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(self.binance_keys['secret_key'].encode('utf-8'), query_string.encode('utf-8'),
                             hashlib.sha256)
        params['signature'] = signature.hexdigest()


def Main():
    symbol = 'NEOBTC'
    secrets = json.load(open('secrets.json'))
    client_id = secrets['CLIENT_ID']
    exchange = Binance('credentials.txt')
    info = exchange.GetOrderInfo(symbol, client_id)
    print(info)


if __name__ == '__main__':
    Main()
