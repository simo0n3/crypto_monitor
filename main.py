import time
from fetch.binance_ws import BinanceWS
from logic.volatility_calc import calc_returns, calc_volatility
from logic.anomaly_detector import is_anomaly_std, is_anomaly_quantile
from notify.telegram_bot import send_bark
from utils.logger import setup_logger
from threading import Thread
from flask import Flask

# 配置
BARK_API = 'https://api.day.app/CiBwcJFtZJqN2oDeRx3RK7/'
LOG_FILE = 'data/crypto_monitor.log'
VOLUME_WINDOW = 1000
VOLUME_N = 2
ANOMALY_N = 2
ANOMALY_QUANTILE = 0.95

logger = setup_logger(LOG_FILE)

# 维护每个币的K线历史（用于涨跌幅和波动率计算）
kline_history = {}

class MonitorWS(BinanceWS):
    def on_message(self, ws, message):
        import json
        data = json.loads(message)
        if 'data' in data and 'k' in data['data']:
            kline = data['data']['k']
            if kline['x']:
                symbol = data['data']['s'].lower()
                open_price = float(kline['o'])
                close_price = float(kline['c'])
                volume = float(kline['v'])
                # 维护K线历史
                if symbol not in kline_history:
                    kline_history[symbol] = []
                kline_history[symbol].append((open_price, close_price))
                if len(kline_history[symbol]) > VOLUME_WINDOW:
                    kline_history[symbol] = kline_history[symbol][-VOLUME_WINDOW:]
                # 继承父类的成交量暴增检测
                super().on_message(ws, message)
                # 检测涨跌幅异常
                if len(kline_history[symbol]) >= VOLUME_WINDOW:
                    returns = calc_returns(kline_history[symbol])
                    last_return = returns[-1]
                    hist_returns = returns[:-1]
                    is_spike, threshold = is_anomaly_std(last_return, hist_returns, n=ANOMALY_N)
                    if is_spike:
                        msg = f'{symbol.upper()} 15m暴涨/暴跌: {last_return*100:.2f}%\n阈值: {threshold*100:.2f}%\n开盘: {open_price}, 收盘: {close_price}'
                        logger.warning(msg)
                        send_bark(f'{symbol.upper()}暴动', msg, BARK_API)

def fake_web():
    app = Flask(__name__)
    @app.route('/')
    def index():
        return 'Crypto Monitor Running'
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    logger.info('启动数字货币监控系统...')
    ws = MonitorWS(interval='15m', volume_window=VOLUME_WINDOW, volume_n=VOLUME_N)
    print(f'当前监控币种数量: {len(ws.symbols)}')
    print('后10个币种:', ', '.join(ws.symbols[-10:]))
    ws.run()
    Thread(target=fake_web, daemon=True).start()
    while True:
        time.sleep(60) 