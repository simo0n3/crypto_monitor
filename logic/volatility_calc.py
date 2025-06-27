import numpy as np

def calc_returns(kline):
    """
    输入: kline为[(open, close), ...]
    输出: 每根K线的涨跌幅序列 [(close-open)/open, ...]
    """
    return [(close - open_) / open_ for open_, close in kline]


def calc_volatility(returns, quantile=0.95):
    """
    输入: returns为涨跌幅序列
    输出: 均值、标准差、分位数
    """
    arr = np.array(returns)
    mean = np.mean(arr)
    std = np.std(arr)
    q = np.quantile(np.abs(arr), quantile)
    return {
        'mean': mean,
        'std': std,
        'quantile': q
    }

if __name__ == '__main__':
    # 示例
    kline = [(100, 105), (105, 100), (100, 110), (110, 120)]
    returns = calc_returns(kline)
    print('涨跌幅:', returns)
    vol = calc_volatility(returns)
    print('波动率统计:', vol) 