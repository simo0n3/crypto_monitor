import requests

class BinanceAPI:
    BASE_URL = 'https://fapi.binance.com'

    def get_symbols(self):
        """
        获取所有USDT合约交易对（symbol）
        返回：['BTCUSDT', 'ETHUSDT', ...]
        """
        url = f'{self.BASE_URL}/fapi/v1/exchangeInfo'
        resp = requests.get(url)
        data = resp.json()
        symbols = [s['symbol'] for s in data['symbols'] if s['contractType'] == 'PERPETUAL' and s['quoteAsset'] == 'USDT']
        return symbols

    def get_kline(self, symbol, interval='15m', limit=100):
        """
        获取指定币种的K线数据
        返回：[(open, close), ...]
        """
        url = f'{self.BASE_URL}/fapi/v1/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        resp = requests.get(url, params=params)
        data = resp.json()
        # K线格式：[开盘时间,开盘价,最高价,最低价,收盘价,...]
        kline = [(float(item[1]), float(item[4])) for item in data]
        return kline

if __name__ == '__main__':
    api = BinanceAPI()
    symbols = api.get_symbols()
    print()
    print('合约币种数量:', len(symbols))
    print('前5个币种:', symbols[:5])
    kline = api.get_kline(symbols[0])
    print(f'{symbols[0]} 15m K线样例:', kline[-3:]) 