import numpy as np

def is_anomaly_std(last_return, hist_returns, n=2):
    """
    方法1: 均值+N倍标准差
    last_return: 最新一根K线涨跌幅
    hist_returns: 历史涨跌幅序列（不含最新）
    n: 阈值倍数
    返回: (是否异常, 阈值)
    """
    mean = np.mean(hist_returns)
    std = np.std(hist_returns)
    threshold = mean + n * std
    return abs(last_return) > threshold, threshold


def is_anomaly_quantile(last_return, hist_returns, quantile=0.95):
    """
    方法2: 分位数法
    last_return: 最新一根K线涨跌幅
    hist_returns: 历史涨跌幅序列（不含最新）
    quantile: 分位数（如0.95）
    返回: (是否异常, 阈值)
    """
    threshold = np.quantile(np.abs(hist_returns), quantile)
    return abs(last_return) > threshold, threshold

if __name__ == '__main__':
    # 示例
    returns = [0.01, -0.02, 0.015, -0.01, 0.03, 0.02, -0.025, 0.01, 0.02, 0.015]
    last = 0.05
    print('std法:', is_anomaly_std(last, returns, n=2))
    print('分位数法:', is_anomaly_quantile(last, returns, quantile=0.95)) 