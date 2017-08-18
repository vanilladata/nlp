# encoding:utf8

# The BaseHTTPServer module has been merged into http.server in Python 3.
# import http.server #python 3
# # from http.server import SimpleHTTPRequestHandler
# from http.server import BaseHTTPRequestHandler
# from http.server import HTTPServer
from BaseHTTPServer import HTTPServer  # python 2.7
import traceback
import logging
import logging.config
import time
import os
import sys
from baseutils.myWrapper import exceptionIgnore

import threading

global_logger = None


class ThreadSafeHolder(object):
    ServerStatus = {"ready": 1, "run": 2, "stop": 3, "termination": 4}

    def __init__(self, innerObj):
        self.status = ThreadSafeHolder.ServerStatus["ready"]
        self.threadCondition = threading.Condition()
        self.innerObj = innerObj

    def safeExecute(self, newStatus, object, funcName):
        self.threadCondition.acquire()
        if self.status != newStatus:
            self.status = ThreadSafeHolder.ServerStatus[newStatus]
            getattr(object, funcName)()
        self.threadCondition.notify()
        self.threadCondition.release()


class CRFServer(object):
    """条件随机场服务"""

    # 构造方法
    def __init__(self, handler_Class, port=8000, hostName='127.0.0.1', logName='root', protocal="HTTP/1.0",
                 ServerClass=HTTPServer):

        self.port = port  # 端口
        self.hostName = hostName  # 服务端hostname
        self.protocal = protocal
        self.handler_Class = handler_Class
        self.ServerClass = ServerClass
        self.inner_logger = logging.getLogger(logName)

        # 初始化日志

    def initAndStart(self):
        self.inner_logger.debug("start CRFServer ...")

        server_address = (self.hostName, self.port)

        handler_Class = self.handler_Class
        ServerClass = self.ServerClass

        handler_Class.protocol_version = self.protocal
        handler_Class.inner_logger = self.inner_logger

        # httpd = http.server.HTTPServer(server_address, HandlerClass)
        httpd = ServerClass(server_address, handler_Class)

        # holder = ThreadSafeHolder(httpd)

        # self.holder = holder
        self.httpd = httpd

        sa = self.httpd.socket.getsockname()
        self.inner_logger.debug("will start CRFServer on:[%s] port:[%d]." % (sa[0], sa[1]))
        # httpd.serve_forever()

        # 静默模式启动服务
        self.starInSilent()
        # try:
        #     httpd.serve_forever()
        # except KeyboardInterrupt as ex:
        #     # msg =traceback.format_exc()   # 方式1
        #     # print(msg)
        #     msg = "httpd server exception:[%s],host:[%s], at port:[%d]" % (traceback.format_exc(), hostName, port)
        #     logging.error(traceback.format_exc())  # 方式2

    @exceptionIgnore([KeyboardInterrupt], global_logger)
    def starInSilent(self):
        try:
            self.inner_logger.debug("start CRFServer in silent ...")
            self.status = ThreadSafeHolder.ServerStatus["run"]
            self.httpd.serve_forever()
        except Exception as excp:
            self.inner_logger.error(
                "httpd server exception:[%s],host:[%s], at port:[%d]" % (
                    traceback.format_exc(), self.hostName, self.port))
            self.httpd.server_close()
            # sys.exit(0)

    def tryStop(self):
        # 退出
        # self.holder.safeExecute("stop", self.httpd, "server_close")
        self.httpd.server_close()

    # 暂时不支持重新启动操作
    def tryStart(self):
        # self.holder.safeExecute("run", self, "starInSilent")
        # self.starInSilent()
        pass

    def tryTerminate(self):
        pass
