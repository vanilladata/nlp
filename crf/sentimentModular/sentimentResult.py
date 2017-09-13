#encoding=utf-8
import jieba
jieba.load_userdict(r'../ximenzidict.txt')
jieba.initialize()
from nltk.corpus import wordnet as wn #wordnet 级性
from nltk.corpus import sentiwordnet as swn #corpus 中文预料，中间包了一层，中英文关系
import codecs

stopwords = set()  #停用词用set存储速度会很快，如果用list存储，会很慢
for word in open('../stop_words.txt', 'r'):
    stopwords.add(word.strip())
allmap = {}
def loadWordNet():
    f = codecs.open('../ximenzicow-not-full02.txt', 'rb', 'utf-8')
    known = set()
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        row = line.strip().split('\t')
        if len(row) == 3:
            (synset, lemma, status) = row #synset同意词,lemma是啥,status状态
        elif len(row) == 2:
            (synset, lemma) = row
            status = 'Y'
        else:
            print 'bad formed line:', line.strip()
        if status in ['Y', 'O']:
            if not (synset.strip(), lemma.strip()) in known:
                #print synset.strip(), lemma.strip()
                known.add((synset.strip(), lemma.strip()))
                if allmap.get(lemma.strip()) != None:
                    allmap[lemma.strip()] = allmap[lemma.strip()].append(synset.strip())
                else:
                    allmap[lemma.strip()] = [synset.strip()]

    return known
known = loadWordNet()

class sentimentResult:
    @classmethod
    def sentiment(cls,datas):
        resultlist = [] #返回结果集
        for data in datas:
            n = 0
            p = 0
            resultValue = "" #存储正负向
            words = cls.doSegExcel(data["content"])
            for word in words:
                ll = cls.findWordNet(word)
                if len(ll) != 0:
                    n1 = 0.0
                    p1 = 0.0
                    for wid in ll:
                        desc = cls.id2ss(wid)
                        swninfo = cls.getSenti(desc)
                        p1 = p1 + swninfo.pos_score()
                        n1 = n1 + swninfo.neg_score()
                    p = p + p1/len(ll)
                    n = n + n1/len(ll)
            if p > n:
                resultValue += u'正'
            elif p < n:
                resultValue += u'负'
            else:
                resultValue += u'中'
            resultlist.append({"id":data["id"],"emotion":resultValue})
            print " 负面评价: ", n, ", 正面评价: ", p
            return resultlist

    # 传入文本并分词存入tokens
    @classmethod
    def doSegExcel(cls,content):
        seg_list = jieba.cut(content)
        tokens = []
        for seg in seg_list:
            if (seg.encode("utf-8") not in stopwords and seg != '' and seg != '\n' and seg != '\n\n'):
                tokens.append(seg)
        return tokens

    @classmethod
    def findWordNet(cls,key):
        tokens = []
        # print key.encode('utf-8')
        value = allmap.get(key)
        if value is not None:
            for innervalue in value:
                tokens.append(innervalue)
        return tokens

    @classmethod
    def id2ss(cls,ID):
        # print ID
        return wn._synset_from_pos_and_offset(str(ID[-1:]), int(ID[:8]))

    @classmethod
    def getSenti(cls,word):
        # print word.name()
        return swn.senti_synset(word.name())

if __name__ == "__main__":
    datas = []
    # datas.append(u"手机整体不错，只是信号有时比较弱,这个价格的手机已经算性价比高的了")
    # datas.append(u"很好用的一款手机，联想品牌真心不错，希望以后都能这样好下去，继续好用，一直好用")
    datas.append({"id": "123", "content": "【律师解读: 阿里云被判侵权, 云服务器行业面临重大转折?】雷锋网按：本文作者赵占领，知名IT与知识产权律师、中国政法大学知识产权研究中心特约研究员、中国网络诚信联盟法律顾问、经济之声与法制日报特约评http://t.cn/RSBAQxA ​ ​"})
    resultlist = sentimentResult.sentiment(datas)
    for result in resultlist:
        print "文档id: ",result["id"],"文档正负向：", result["emotion"]
