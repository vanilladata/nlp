# encoding:utf8
import jieba
from ExeContext import ExeContext
import MyCommonutils as myUtils
import json


class JieBaSegment:
    # 分词工具类
    logger = None

    # 文本进词
    @staticmethod
    def segmentWithoutDic():
        pass

    # 文本分词 用户指定分词词典
    @staticmethod
    def segment(text, dictFileName="default.dict"):
        dictDir = ExeContext.context["dictDir"]
        dictFullPath = myUtils.getChildDir(dictDir, dictFileName)
        # 记录日志
        JieBaSegment.logger.info("load user dict from path:[%s]" % dictFullPath)

        jieba.load_userdict(dictFullPath)
        # 精确模式
        seg_list = jieba.cut(text, cut_all=False)

        tokens = []
        for token in seg_list:
            tokens.append(token)

        result = {u"text": text, "tokens": tokens}
        respDataLog = json.dumps(result, "utf8", ensure_ascii=False)
        JieBaSegment.logger.debug("segment for text:[%s] success." % (respDataLog))
        JieBaSegment.logger.info("segment for text success.")

        # 返回处理结果
        return result

    pass
