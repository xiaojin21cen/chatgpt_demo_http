import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    default_fmt = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    default_fmt2 = '%(asctime)s - %(filename)s - %(levelname)s: %(message)s'
    default_fmt3 = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    default_fmt4 = '%(asctime)s - %(pathname)s - %(levelname)s: %(message)s'

    def __init__(self, filename, level='info', when='D', backCount=10, fmt=default_fmt2):
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别

        formatter = logging.Formatter(fmt)  # 设置日志格式

        handler = logging.StreamHandler()  # 往屏幕上输出
        handler.setFormatter(formatter)  # 设置屏幕上显示的格式

        # 实例化 TimedRotatingFileHandler
        # interval 是时间间隔，
        # backupCount 是备份文件的个数，如果超过这个个数，就会自动删除，
        # when 是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        handler2 = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        handler2.setFormatter(formatter)  # 设置文件里写入的格式

        self.logger.addHandler(handler)
        self.logger.addHandler(handler2)
