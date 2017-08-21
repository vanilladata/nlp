#encoding=utf8
import jieba
jieba.load_userdict(r'../mydict.txt')
jieba.initialize()
# from utile import *
from utile import *
import os
import json

stopwords = {} #停用词用dict存储速度会很快，如果用list存储，会很慢
for word in open('../stop_words.txt', 'r'):
    stopwords[word.strip().decode('gbk', 'ignore').encode('utf-8')] = 1
class crfresult:
    """此程序适用于windows、和linux下，没采用CRFPP接口调用"""
    @classmethod
    def crftext(self, datas, output):
        """通过传入的list数据，返回CRF标注的结果并拼接成json格式返回"""
        connect = ""
        #把传入的list拼接成一个以句号拼接这样在分句的时候会自动把句号进行切分
        for data in datas: connect = connect + data + "。"
        # print connect
        subsection = utile()
        resultlists = subsection.subsection(connect)

        resultlist = []
        for r in resultlists:
            seg_list = jieba.cut(r)
            seg_list_after = []
            writelist = []
            # 去掉停用词
            for seg in seg_list:
                if stopwords.has_key(seg.encode('utf-8')):
                    continue
                else:
                    seg_list_after.append(seg)

            for seg in seg_list_after:
                if (seg.encode("utf-8") not in stopwords and seg != ' ' and seg != '\n' and seg != '\n\n'):
                    writelist.append(seg)
            resultlist.append(writelist)
        self.writeCrfTrainData(resultlist, output)
        # 调用CRF模型得出结果
        os.system(r'"crf_test -m model test.data > output.txt"')#调用windows exe程序
        # os.system("sh /home/hadoop/nlp/crf/exec.sh")#调用linux shell的脚步
        resultjson = self.readresult(u'output.txt')
        # print resultjson
        return resultjson

    # 按照CRF的格式把数据写入txt
    @classmethod
    def writeCrfTrainData(self, resultlists, outfile):
        f = open(outfile, "w")
        for resultlist in resultlists:
            for resultdata in resultlist:
                f.write(resultdata.encode("utf-8"))
                f.write("\n")
            f.write("\n")

        f.close()

    #读取结果数据
    @classmethod
    def readresult(self, infile):
        taglist = []
        wordlist = []
        dict = {}
        resultlists = []
        for line in open(infile):
            word = line.replace('\n', '')
            if word != '':
                words = word.split('\t')
                taglist.append(words[1])
                wordlist.append(words[0])
            else:
                # resultlists.append(wordlist)
                dict["tag"] = taglist
                dict["word"] = wordlist
                resultlists.append(dict)
                wordlist = []
                taglist = []
                dict = {}
        return json.dumps(resultlists)
if __name__ == '__main__':
    datas = []
    datas.append("手机整体不错，只是信号有时比较弱,这个价格的手机已经算性价比高的了")
    datas.append("很好用的一款手机，联想品牌真心不错，希望以后都能这样好下去，继续好用，一直好用")
    crfresult.crftext(datas,'test.data')
    # 物流是比较给力