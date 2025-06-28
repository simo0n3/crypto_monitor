import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_kline_history(self, symbol, klines):
        """保存币种K线历史到文件"""
        filename = f'{self.data_dir}/{symbol}_kline.json'
        data = {
            'symbol': symbol,
            'last_update': datetime.now().isoformat(),
            'klines': klines
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
    
    def load_kline_history(self, symbol):
        """从文件加载币种K线历史"""
        filename = f'{self.data_dir}/{symbol}_kline.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('klines', [])
        return []
    
    def update_kline_history(self, symbol, new_kline):
        """更新币种K线历史（追加新K线）"""
        klines = self.load_kline_history(symbol)
        klines.append(new_kline)
        
        # 保持1000根窗口
        if len(klines) > 1000:
            klines = klines[-1000:]
        
        self.save_kline_history(symbol, klines)
        return klines 