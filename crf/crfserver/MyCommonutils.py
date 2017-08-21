# coding:utf8
"""常用工具类"""
import logging
import os


# 获取当前路径
def script_path():
    import inspect, os
    this_file = inspect.getfile(inspect.currentframe())
    return os.path.abspath(os.path.dirname(this_file))


# 初始化日志
def initlog(workdir, logcfgFile):
    logcfgFullName = os.path.join(workdir, logcfgFile)
    logging.config.fileConfig(logcfgFullName)
    # create logger
    # test log
    inner_logger = logging.getLogger('root')
    inner_logger = inner_logger
    inner_logger.info("mode:[logger] init success!")


def getInStr(strSource):
    if isinstance(strSource, unicode):
        strSource = strSource.encode('UTF-8')
        return strSource
    else:
        return strSource
