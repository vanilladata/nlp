#encoding=utf8
import jieba
jieba.load_userdict(r'../mydict.txt')
jieba.initialize()
from utile import *
import os
import json
import CRFPP

stopwords = {} #停用词用dict存储速度会很快，如果用list存储，会很慢
for word in open('../stop_words.txt', 'r'):
    stopwords[word.strip().decode('gbk', 'ignore').encode('utf-8')] = 1
jieba.suggest_freq((u'反应',u'速度'),True)
jieba.suggest_freq((u'反应速度',u'快'),True)
jieba.suggest_freq((u'综合',u'性'),True)
jieba.suggest_freq((u'价格',u'便宜'),True)
jieba.suggest_freq((u'很',u'大气'),True)
class crfppresult:
    @classmethod
    def crfpptest(self,datas):
        """通过传入的list数据，返回CRF标注的结果并拼接成json格式返回"""
        connect = ""
        # 把传入的list拼接成一个以句号拼接这样在分句的时候会自动把句号进行切分
        # for data in datas: connect = connect + data.encode("utf-8") + "。"
        # # print connect
        # subsection = utile()
        # subsectlist = subsection.subsection(connect) #切分成句子
        # model = "-m " + model_path +" -n1"
        tagger = CRFPP.Tagger("-m /data/3inlp/nlp/crf/crftest/model -n1")   #CRFPP 读取模型，现在是写死的，以后可以直接改成参数
        taglist = []    #接json用的,把所有的标签放到list中
        wordlist = []   #接json用的，把所有的词放到list中
        dict = {}       #接json用的
        resultlist = [] #接json用的,也是最后返回的
        for r in datas:
            tagger.clear()
            seg_list = jieba.cut(r.encode("utf-8"))
            seg_list_after = []
            # 去掉停用词
            for seg in seg_list:
                if stopwords.has_key(seg.encode('utf-8')):
                    continue
                else:
                    seg_list_after.append(seg)

            #去掉停用词后的词加载到CRFPP中
            for seg in seg_list_after:
                if (seg.encode("utf-8") not in stopwords and seg != ' ' and seg != '\n' and seg != '\n\n'):
                    tagger.add(seg.encode('utf-8'))
            tagger.parse()
            size = tagger.size() #行数
            xsize = tagger.xsize()
            # print size
            # print xsize
            for i in range(0, size):
                for j in range(0,xsize):
                    wordlist.append(tagger.x(i,j).decode('utf-8'))  #返回的是词
                    taglist.append(tagger.y2(i))    #返回的是标签
                    # print tagger.x(i,j).decode('utf-8'), tagger.y2(i)
            dict["lables"] = taglist
            dict["tokens"] = wordlist
            resultlist.append(dict)
            wordlist = []
            taglist = []
            dict = {}
        return resultlist

if __name__ == '__main__':
    datas = []
    datas.append("手机整体不错，只是信号有时比较弱,这个价格的手机已经算性价比高的了")
    datas.append("很好用的一款手机，联想品牌真心不错，希望以后都能这样好下去，继续好用，一直好用")
    crfppresult.crfpptest(datas)
