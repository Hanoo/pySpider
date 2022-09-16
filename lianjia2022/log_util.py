import logging
from logging import handlers
import colorlog
from inspect import currentframe


class LogUtil:
    """日志工具类"""
    logger = None
    format = '%(asctime)s %(levelname)s: %(message)s'
    colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
    # 颜色格式
    fmt_colored, fmt_colorless = None, None
    # 日志输出端
    console_handler, file_handler = None, None

    @classmethod
    def init(cls, logname, console=False):
        """使用前需要初始化，输入生成的日志文件名
        注意：默认按天生成日志，且保留最近一周的日志文件
        """
        if not cls.logger:
            cls.logger = logging.getLogger(logname)
            cls.logger.setLevel(logging.DEBUG)
            # 有颜色格式
            cls.fmt_colored = colorlog.ColoredFormatter(f'%(log_color)s{cls.format}', datefmt=None, reset=True, log_colors=cls.colors)
            # 无颜色格式
            cls.fmt_colorless = logging.Formatter(cls.format)
            # 输出到控制台和文件
            if console:
                cls.console_handler = logging.StreamHandler()
            cls.file_handler = handlers.TimedRotatingFileHandler(filename=logname, when='D', backupCount=3, encoding='utf-8')

    @classmethod
    def open(cls):
        if cls.console_handler:
            cls.console_handler.setFormatter(cls.fmt_colored)
            cls.logger.addHandler(cls.console_handler)
        cls.file_handler.setFormatter(cls.fmt_colored)
        cls.logger.addHandler(cls.file_handler)

    @classmethod
    def close(cls):
        if cls.console_handler:
            cls.logger.removeHandler(cls.console_handler)
        cls.logger.removeHandler(cls.file_handler)

    @classmethod
    def debug(cls, msg):
        cls.open()
        last_frame = currentframe().f_back
        func_name = last_frame.f_code.co_name
        lineo = last_frame.f_lineno
        cls.logger.debug(f'< {func_name} - {lineo} > {msg}')
        cls.close()

    @classmethod
    def info(cls, msg):
        cls.open()
        last_frame = currentframe().f_back
        func_name = last_frame.f_code.co_name
        lineo = last_frame.f_lineno
        cls.logger.info(f'< {func_name} - {lineo} > {msg}')
        cls.close()

    @classmethod
    def warn(cls, msg):
        cls.open()
        last_frame = currentframe().f_back
        func_name = last_frame.f_code.co_name
        lineo = last_frame.f_lineno
        cls.logger.warning(f'< {func_name} - {lineo} > {msg}')
        cls.close()

    @classmethod
    def error(cls, title, *msg):
        cls.open()
        last_frame = currentframe().f_back
        filepath = last_frame.f_code.co_filename
        funcn = last_frame.f_code.co_name
        lineo = last_frame.f_lineno
        cls.logger.error("< {} >".format(title).center(120, "#"))
        cls.logger.error(f'< {funcn} - {lineo} >')
        if msg or msg == 0 or msg is False:
            cls.logger.error(msg)
        cls.logger.error("")
        cls.close()

    @classmethod
    def critical(cls, title, *msg):
        cls.open()
        last_frame = currentframe().f_back
        filepath = last_frame.f_code.co_filename
        funcn = last_frame.f_code.co_name
        lineo = last_frame.f_lineno
        cls.logger.critical("< {} >".format(title).center(120, "#"))
        cls.logger.critical(f'< {funcn} - {lineo} >')
        if msg or msg == 0 or msg is False:
            cls.logger.critical(msg)
        cls.logger.critical("")
        cls.close()


def main():
    """主函数"""
    LogUtil.init('run.log', console=True)
    filename = 'a.txt'
    filesize = '250KB'
    LogUtil.debug('filesize')
    LogUtil.info('filesize')
    LogUtil.warn('filesize')
    LogUtil.error('filesize', filename, filesize)
    # LogUtil.critical('filesize', filename, filesize)


if __name__ == '__main__':
    main()
