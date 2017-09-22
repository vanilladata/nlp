# encoding:utf8
import json
import logging

import jieba
import jieba.analyse

import MyCommonutils as myutils
from baseutils.ExeContext import ExeContext


class JieBaSegment:
    # 分词工具类

    # 停用词
    stopWords = set()

    # 文本分词 用户指定分词词典
    @staticmethod
    def segment(text, dictFullName=None):
        # dictDir = ExeContext.context["dictDir"]
        # dictFullPath = myUtils.getChildDir(dictDir, dictFileName)
        logName = ExeContext.context["logName"]
        # 记录日志
        logger = logging.getLogger(logName)

        if not dictFullName is None:
            logger.info("load user dict from path:[%s]" % dictFullName)
            jieba.load_userdict(dictFullName)
        else:
            logger.info("user dict file name is null.")

        # 精确模式
        seg_list = jieba.cut(text, cut_all=False)

        if len(JieBaSegment.stopWords) == 0:
            JieBaSegment.loadStopWords()

        tokens = []
        for token in seg_list:
            if (token in JieBaSegment.stopWords):
                continue
            tokens.append(token)

        result = {u"text": text, u"tokens": tokens}
        respDataLog = json.dumps(result, "utf8", ensure_ascii=False)
        logger.debug("segment for text:[%s] success." % (respDataLog))
        logger.info("segment for text success.")

        # 返回处理结果
        return result

    @staticmethod
    def loadStopWords():
        dictDir = ExeContext.context["dictDir"]
        # 加载停用次词典
        ExeContext.loadStopWord(dictDir, JieBaSegment.stopWords)

    @staticmethod
    def segmentByDefault(text):
        dictDir = ExeContext.context["dictDir"]
        dictFileName = ExeContext.context["default_dictFileName"]
        # 获取分词词典
        dictFullPath = myutils.getChildDir(dictDir, dictFileName)

        logName = ExeContext.context["logName"]
        # 记录日志
        logger = logging.getLogger(logName)
        logger.info("load user dict from path:[%s]" % dictFullPath)
        jieba.load_userdict(dictFullPath)

        # 精确模式
        seg_list = jieba.cut(text, cut_all=False)

        if len(JieBaSegment.stopWords) == 0:
            JieBaSegment.loadStopWords()

        tokens = []
        for token in seg_list:
            if (token in JieBaSegment.stopWords):
                continue
            tokens.append(token)

        result = {u"text": text, u"tokens": tokens}
        respDataLog = json.dumps(result, "utf8", ensure_ascii=False)
        logger.debug("segment for text:[%s] success." % (respDataLog))
        logger.info("segment for text success.")

        # 返回处理结果
        return result

    def extractTags(self, text):
        tags = jieba.analyse.extract_tags(text)
        pass

    pass
