import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', backCount=5, maxBytes=10*1024*1024, fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)                       # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))     # 设置日志级别
        th = handlers.RotatingFileHandler(filename=filename, backupCount=backCount, maxBytes=maxBytes)  # 文件达到指定大小自动生成新日志文件
        th.setFormatter(format_str)        # 设置文件里写入的格式
        self.logger.addHandler(th)