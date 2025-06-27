import logging
import os

def setup_logger(log_file=None, level=logging.INFO):
    """
    初始化日志系统
    :param log_file: 日志文件路径（可选）
    :param level: 日志级别
    :return: logger对象
    """
    logger = logging.getLogger('crypto_monitor')
    logger.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 控制台输出
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 文件输出
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

if __name__ == '__main__':
    logger = setup_logger('data/crypto_monitor.log')
    logger.info('测试info日志')
    logger.warning('测试warning日志')
    logger.error('测试error日志') 