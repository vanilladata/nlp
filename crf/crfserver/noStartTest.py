# coding:utf8

from baseutils.ExeContext import ExeContext
from baseutils.SegmentUtil import JieBaSegment


def test():
    # -----------------------------  分词调用测试 ------------------------- #
    ExeContext.initProject()
    inner_log = ExeContext.getLogger()
    # 加载停用词词典
    # stopkey = [line.strip().decode('utf-8') for line in open('stopkey.txt').readlines()]

    # 测试代码
    testSentence = u"我们是中国人，中国人很棒，我们的3D打印技术很棒，他的很好，我的更好。打印在过程工业与传动技术领域有很大作为,也在其他领域很有作为。"
    result = JieBaSegment.segmentByDefault(testSentence)
    print u"分词结果: ", result
    pass


if __name__ == "__main__":
    test();
    pass
