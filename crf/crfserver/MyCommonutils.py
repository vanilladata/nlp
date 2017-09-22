# coding:utf8
"""常用工具类"""
import logging
import logging.config
import os


# 获取当前路径
def script_path():
    import inspect, os
    this_file = inspect.getfile(inspect.currentframe())
    return os.path.abspath(os.path.dirname(this_file))


def getParentDir(path):
    parentDir = os.path.abspath(os.path.join(path, os.pardir))
    parentDir = os.path.abspath(parentDir)
    return parentDir
    # import_dir = os.path.abspath(os.path.join(import_dir, "crftest"))


def getChildDir(path, childName):
    childDir = os.path.abspath(os.path.join(path, childName))
    return childDir


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
