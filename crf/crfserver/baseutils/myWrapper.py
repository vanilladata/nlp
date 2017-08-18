# coding:utf8
from functools import wraps
import time
import socket
import traceback


def retry(MyException, tries=4, delay=3, backoff=2, logger=None):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)  # 执行一次
                except MyException as ex:
                    msg = "%s, Retrying in %d seconds..." % (str(ex), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return str(ex)

        return f_retry

    return deco_retry


def exceptionIgnore(MyExceptions, logger=None):
    def wrap_ignore(f):
        @wraps(f)
        def f_ignore(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as ex:
                if type(ex) in MyExceptions:
                    msg = "%s, ignore exception:[%s]." % (traceback.format_exc())
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                else:
                    raise ex
            return str(ex)

        return f_ignore

    return wrap_ignore


if __name__ == "__main__":
    @retry(Exception, logger=None)
    def checkRetry():
        sk = socket.socket()
        sk.settimeout(5)
        sk.connect(('6.6.6.6', 80))
