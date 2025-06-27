import requests
import json
import threading
from websocket import WebSocketApp
from collections import defaultdict, deque
import numpy as np
import time

class BinanceWS:
    BASE_URL = 'https://fapi.binance.com'
    WS_BASE = 'wss://fstream.binance.com/stream?streams='

    def __init__(self, interval='15m', volume_window=1000, volume_n=2):
        self.interval = interval
        self.symbols = self.get_all_symbols()
        self.ws_urls = self.make_ws_urls()
        self.ws_list = []
        self.volume_history = defaultdict(lambda: deque(maxlen=volume_window))
        self.volume_n = volume_n
        self.volume_window = volume_window
        self.max_retries = 10
        self.retry_interval = 10  # 秒

    def get_all_symbols(self):
        url = f'{self.BASE_URL}/fapi/v1/exchangeInfo'
        resp = requests.get(url)
        data = resp.json()
        symbols = [s['symbol'].lower() for s in data['symbols'] if s['contractType'] == 'PERPETUAL' and s['quoteAsset'] == 'USDT']
        return symbols

    def make_ws_urls(self, batch_size=200):
        batches = [self.symbols[i:i+batch_size] for i in range(0, len(self.symbols), batch_size)]
        ws_urls = []
        for batch in batches:
            streams = '/'.join([f'{s}@kline_{self.interval}' for s in batch])
            ws_urls.append(self.WS_BASE + streams)
        return ws_urls

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'data' in data and 'k' in data['data']:
            kline = data['data']['k']
            if kline['x']:  # is_final
                symbol = data['data']['s'].lower()
                open_price = float(kline['o'])
                close_price = float(kline['c'])
                volume = float(kline['v'])
                # 维护成交量历史
                self.volume_history[symbol].append(volume)
                # 检测成交量暴增
                if len(self.volume_history[symbol]) >= self.volume_window:
                    hist = list(self.volume_history[symbol])[:-1]
                    mean = np.mean(hist)
                    std = np.std(hist)
                    if volume > mean + self.volume_n * std:
                        print(f'{symbol} 15m成交量暴增: {volume:.2f} (均值: {mean:.2f}, std: {std:.2f}) 开盘={open_price}, 收盘={close_price}')

    def on_error(self, ws, error):
        print('WebSocket error:', error)

    def on_close(self, ws, close_status_code, close_msg):
        print('WebSocket closed')

    def on_open(self, ws):
        print('WebSocket连接成功')

    def run_single_ws(self, ws_url):
        retry_count = 0
        while retry_count < self.max_retries:
            ws = WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            try:
                ws.run_forever()
            except Exception as e:
                print(f'WebSocket连接异常: {e}')
            retry_count += 1
            print(f'已断线，{self.retry_interval}秒后重连...（第{retry_count}次）')
            time.sleep(self.retry_interval)
        print(f' 连续{self.max_retries}次重连失败，停止尝试。')

    def run(self):
        for ws_url in self.ws_urls:
            t = threading.Thread(target=self.run_single_ws, args=(ws_url,))
            t.daemon = True
            t.start()
            self.ws_list.append(t)

if __name__ == '__main__':
    ws = BinanceWS(interval='15m', volume_window=1000, volume_n=2)
    ws.run()
    while True:
        time.sleep(60) 