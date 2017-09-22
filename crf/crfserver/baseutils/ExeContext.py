# encoding:utf8
import MyCommonutils as myutils
import logging


class ExeContext:
    # 默认的模型名称
    context = dict({"modelName": "model", "default_dictFileName": "default.dict",
                    "default_stop": "default.stop"})

    # 上下文环境类
    # 保存工程运行时候的上下文参数,例如启动脚本时候指定的参数等等
    def __init__(self):
        pass

    @staticmethod
    def initProject(args=None):
        if args is None:
            logCfgFileName = "logcfg/logfile.conf"
            logName = "root"
            port = 8000
            hostName = "0.0.0.0"
        else:
            if not args.filelog:
                logName = "root"
            else:
                logName = "filelog"
            # 初始化日志
            logCfgFileName = args.logcfg
            port = args.port
            hostName = args.bind

        workDir = myutils.script_path()
        myutils.initlog(workDir, logCfgFileName)

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

    @staticmethod
    def getLogger():
        logName = ExeContext.context["logName"]
        # 记录日志
        logger = logging.getLogger(logName)
        return logger
        pass

    @staticmethod
    def loadStopWord(dictDir, targSet):
        stopFile = ExeContext.context["default_stop"]
        stopFullPath = myutils.getChildDir(dictDir, stopFile)
        # stopSet = set()
        with open(stopFullPath) as file:
            allLine = file.readlines()
            for line in allLine:
                line = line.strip().decode('utf-8')
                targSet.add(line)
