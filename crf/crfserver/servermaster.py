# coding:utf8
# The BaseHTTPServer module has been merged into http.server in Python 3.
import threading
# from http.server import HTTPServer
from BaseHTTPServer import HTTPServer
from CRFTaggerServer import CRFServer
from CRFHandler import CRFHttpHandler
from CRFHandler import CRFManagerHandler
from CRFTaggerServer import ThreadSafeHolder
import time
from MyCommonutils import initlog
import MyCommonutils as myutils
import logging
from baseutils.ExeContext import ExeContext


class ServerThread(threading.Thread):
    def __init__(self, threadName, handler_Class, port=8000, hostName='127.0.0.1', logName='root',
                 protocal="HTTP/1.0", serverClass=HTTPServer):

        threading.Thread.__init__(self, None, None, name=threadName)

        if handler_Class is None:
            raise Exception("ServerThread init exception:[param handler_Class is null.]")
        self.requestHandler = handler_Class
        self.port = port
        self.hostName = hostName
        self.logName = logName
        self.inner_log = logging.getLogger(logName)
        self.protocal = protocal
        self.serverClass = serverClass
        serverSupportor = CRFServer(self.requestHandler, self.port, self.hostName, logName, self.protocal,
                                    self.serverClass)
        self.serverSupportor = serverSupportor

    def run(self):
        if None != self.serverSupportor:
            self.serverSupportor.initAndStart()


class ServerManagerThread(ServerThread):
    # def __init__(self):
    #     ServerThread.__init__()

    def setHolder(self, CRFServer):
        # self.CRFServer = CRFServer
        self.serverSupportor.handler_Class.innerCrfServer = CRFServer

        # def stopHolder(self):
        #     self.CRFServer.tryStop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")

    parser.add_argument('--bind', '-b', default='0.0.0.0', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]', dest="bind")

    parser.add_argument('--port', "-p", action='store',
                        default=8000, type=int,
                        nargs='?', dest="port",
                        help='Specify alternate port [default: 8000]')

    parser.add_argument('--filelog', action='store_true',
                        default=False,
                        help='log all info to console otherwise to file by Specify param'
                             ':[logfile] [default:True]')

    parser.add_argument('--logcfg', "-l", action='store',
                        default="logcfg/logfile.conf", type=str, dest="logcfg",
                        nargs='?',
                        help='Specify log config fileName[default: logcfg/logfile.conf]')
    # parser.add_argument('logfile', action='store',
    #                     default="logcfg/logfile.conf", type=str,
    #                     nargs='?',
    #                     help='Specify log config fileName[default: logcfg/logfile.conf]')
    args = parser.parse_args()
    # args = parser.parse_args(['--filelog', '-b 180.121.11.1', '-p8000', '-l logNewFile'])
    # print ("测试:[" + args + "].")
    # if args.cgi:
    #     handler_class = CGIHTTPRequestHandler
    # else:
    #     handler_class = SimpleHTTPRequestHandler
    # test(HandlerClass=handler_class, port=args.port, bind=args.bind)
    # if sys.argv[1:]:
    #     port = int(sys.argv[1])
    # else:
    #     port = 8000

    if not args.filelog:
        logName = "root"
    else:
        logName = "filelog"

    # 初始化日志
    logCfgFileName = args.logcfg
    workDir = myutils.script_path()
    initlog(workDir, logCfgFileName)

    inner_log = logging.getLogger(logName)

    port = args.port

    hostName = args.bind

    ExeContext.context["logName"] = logName
    ExeContext.context["bind"] = hostName
    ExeContext.context["port"] = port
    ExeContext.context["logcfg"] = logCfgFileName

    projectDir = myutils.getParentDir(workDir)
    ExeContext.context["projectDir"] = projectDir
    ExeContext.context["crfServerDir"] = workDir

    # 设置模型目录
    modelDir = myutils.getChildDir(projectDir, "model")
    ExeContext.context["modelDir"] = modelDir

    # 设置词典目录
    dictDir = myutils.getChildDir(projectDir, "dict")
    ExeContext.context["dictDir"] = dictDir

    # 启动CRF服务线程
    crfserver = ServerThread("[CRF-Server-Tread]", CRFHttpHandler, port, hostName=hostName, logName=logName)
    crfserver.start()
    inner_log.info("success start CRFServer on:[%s] port:[%d] at:[%s]" % (hostName, port, time.asctime()))

    # server_address = (hostName, port)
    holder = crfserver.serverSupportor

    managerPort = 8001
    managerServer = ServerManagerThread("[CRF-Manager-Tread]", CRFManagerHandler, managerPort, hostName='127.0.0.1',
                                        logName=logName)
    managerServer.setHolder(holder)
    managerServer.start()
    inner_log.info("success start CRFManagerServer on:[%s] port:[%d] at:[%s]" % (hostName, managerPort, time.asctime()))
