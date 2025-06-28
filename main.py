import time
from fetch.binance_ws import BinanceWS
from logic.volatility_calc import calc_returns, calc_volatility
from logic.anomaly_detector import is_anomaly_std, is_anomaly_quantile
from notify.telegram_bot import send_bark
from utils.logger import setup_logger
from data.history_manager import HistoryManager

# 配置
BARK_API = 'https://api.day.app/CiBwcJFtZJqN2oDeRx3RK7/'
LOG_FILE = 'data/crypto_monitor.log'
VOLUME_WINDOW = 1000
VOLUME_N = 2
ANOMALY_N = 8
ANOMALY_QUANTILE = 0.95

logger = setup_logger(LOG_FILE)

# 维护每个币的K线历史（用于涨跌幅和波动率计算）
kline_history = {}
history_manager = HistoryManager()

class AlertManager:
    def __init__(self, max_alerts_per_period=5, cooldown_period=1800):  # 5个警报/30分钟
        self.max_alerts_per_period = max_alerts_per_period
        self.cooldown_period = cooldown_period
        self.alert_count = 0
        self.last_reset_time = time.time()
        self.last_alert_time = {}  # 每个币种的最后推送时间
    
    def can_send_alert(self, symbol):
        current_time = time.time()
        
        # 检查是否需要重置计数器
        if current_time - self.last_reset_time > self.cooldown_period:
            self.alert_count = 0
            self.last_reset_time = current_time
            logger.info("警报冷却期结束，重置计数器")
        
        # 检查是否超过限制
        if self.alert_count >= self.max_alerts_per_period:
            return False
        
        # 检查币种冷却时间（可选，防止同一币种频繁推送）
        if symbol in self.last_alert_time:
            if current_time - self.last_alert_time[symbol] < 600:  # 10分钟币种冷却
                return False
        
        return True
    
    def record_alert(self, symbol):
        self.alert_count += 1
        self.last_alert_time[symbol] = time.time()
        logger.info(f"已推送 {self.alert_count}/{self.max_alerts_per_period} 个警报")

class MonitorWS(BinanceWS):
    def __init__(self, interval='15m', volume_window=1000, volume_n=2):
        super().__init__(interval, volume_window, volume_n)
        self.alert_manager = AlertManager(max_alerts_per_period=5, cooldown_period=1800)

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
                
                # 更新K线历史
                new_kline = (open_price, close_price)
                if symbol in self.kline_history:
                    self.kline_history[symbol].append(new_kline)
                    if len(self.kline_history[symbol]) > VOLUME_WINDOW:
                        self.kline_history[symbol] = self.kline_history[symbol][-VOLUME_WINDOW:]
                
                # 继承父类的成交量暴增检测
                super().on_message(ws, message)
                
                # 检测涨跌幅异常
                if len(self.kline_history[symbol]) >= VOLUME_WINDOW:
                    returns = calc_returns(self.kline_history[symbol])
                    last_return = returns[-1]
                    hist_returns = returns[:-1]
                    is_spike, threshold = is_anomaly_std(last_return, hist_returns, n=ANOMALY_N)
                    if is_spike:
                        if self.alert_manager.can_send_alert(symbol):
                            msg = f'{symbol.upper()} 15m暴涨/暴跌: {last_return*100:.2f}%\n阈值: {threshold*100:.2f}%\n开盘: {open_price}, 收盘: {close_price}'
                            logger.warning(msg)
                            send_bark(f'{symbol.upper()}暴动', msg, BARK_API)
                            self.alert_manager.record_alert(symbol)
                        else:
                            logger.info(f'{symbol.upper()} 触发警报但被冷却机制阻止')

if __name__ == '__main__':
    logger.info('启动数字货币监控系统...')
    ws = MonitorWS(interval='15m', volume_window=VOLUME_WINDOW, volume_n=VOLUME_N)
    
    # 预加载历史K线数据
    ws.preload_kline_history(kline_history)
    
    print(f'当前监控币种数量: {len(ws.symbols)}')
    print('后10个币种:', ', '.join(ws.symbols[-10:]))
    
    ws.run()
    while True:
        time.sleep(60) 