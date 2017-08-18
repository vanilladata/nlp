#encoding=utf8
import xlrd
import xlwt
import jieba
import jieba.posseg as pseg
jieba.load_userdict(r'mydict.txt')
jieba.initialize()
from utile import *
import os

#此代码主要是把excel转换成CRF++训练语料的格式
stopwords = {} #停用词用dict存储速度会很快，如果用list存储，会很慢
for word in open('stop_words.txt', 'r'):
    stopwords[word.strip().decode('gbk', 'ignore').encode('utf-8')] = 1

nounwords = {} #名词字典
adjectivewords = {} #形容词字典
def nasavedict(filename,sheet):
    """把名词和形容词存入到nounwords和adjectivewords中"""
    dataexcel = xlrd.open_workbook(filename)

    sheet = dataexcel.sheet_by_name(u"" + sheet + "")  # 通过名称获取
    rows = sheet.nrows  # 获取行数 并暂时也代表总数
    for r in range(1,rows):
        rowlist = sheet.row_values(r)
        if rowlist[0] == u'名词':
            nounwords[rowlist[1]] = rowlist[2]
        if rowlist[0] == u'形容词':
            adjectivewords[rowlist[1]] = rowlist[2]
statwords = {} #副词
for word in open('stat_d.txt','r'):
    statwords[word.strip().decode('gbk', 'ignore').encode('utf-8')] = 1

#把标注的词存入到dict中
nasavedict(u"名词形容词标注.xlsx",u'Sheet1')

class crftraindata:
    """此代码主要是把excel转换成CRF++训练语料的格式"""


    def __init__(self, filename,sheet,outfile,fragmentation):
        #filename 为输入的excel文件，sheet为excel中的文档，outfile为输出的txt文件,fragmentation 是否分句
        self.filename = filename
        self.sheet = sheet
        self.outfile = outfile
        self.fragmentation = fragmentation

    def readexcel(self):
        # 从excel中读取数据并放入到list中，以便传给函数写到txt中

        resultlist = []
        dataexcel = xlrd.open_workbook(self.filename)

        sheet = dataexcel.sheet_by_name(u"" + self.sheet + "")  # 通过名称获取
        rows = sheet.nrows  # 获取行数 并暂时也代表总数
        cols = sheet.ncols  # 获取列数

        for i in range(0, rows, 2):
            lists = sheet.row_values(i)
            writelist = []
            for j in range(1, cols):
                labellists = sheet.row_values(i + 1)
                if lists[j] != '':
                    seg_list = jieba.cut(lists[j])
                    seg_list_after = []
                    # 去掉停用词
                    for seg in seg_list:
                        # if seg.encode('utf-8') not in stopwords.keys():
                        #     seg_list_after.append(seg) #用not in 速度很慢，1.63秒才出
                        if stopwords.has_key(seg.encode('utf-8')):
                            continue
                        else:
                            seg_list_after.append(seg)
                    col2 = labellists[j]
                    for colword in seg_list_after:
                        if colword != ' ' and colword != '\n' and colword != '\n\n':
                            if col2 == '':
                                col2 = 'N'
                                writelist.append(colword + ' ' + col2)
                                # print colword + '   ' + col2clear
                            else:
                                writelist.append(colword + ' ' + col2)
                                # print colword + '   ' + col2
            resultlist.append(writelist)
        # print '行数: ', rows, ' 列数: ', cols
        self.writeCrfTrainData(resultlist,self.outfile)

    # 得到的数据写入txt
    @classmethod
    def writeCrfTrainData(self,resultlists,outfile):
        f = open(outfile, "w")
        for resultlist in resultlists:
            for resultdata in resultlist:
                f.write(resultdata.encode("utf-8"))
                f.write("\n")
            f.write("\n")

        f.close()

    def generatingNounAdjectivesExcel(self):
        # 从excel中读取数据并放入到list中，然后通过分词在把每个评论中的词性为（n和a）的值放入到set集合中
        nounset = set()  # 存入名词
        adjectiveset = set()  # 存入形容词
        dataexcel = xlrd.open_workbook(self.filename)

        sheet = dataexcel.sheet_by_name(u"" + self.sheet + "")  # 通过名称获取
        rows = sheet.nrows  # 获取行数 并暂时也代表总数
        # cols = sheet.ncols  # 获取列数

        for i in range(0, rows):
            lists = sheet.row_values(i)
            words = pseg.cut(lists[0])
            for w in words:
                # print w.word,' ',w.flag
                if w.flag == 'n':
                    nounset.add(w.word)
                if w.flag == 'a':
                    adjectiveset.add(w.word)

        wbk = xlwt.Workbook(encoding='utf-8')  # 创建一个新的excel
        wbksheet = wbk.add_sheet("Sheet1", cell_overwrite_ok=False)
        wbksheet.write(0, 0, "词性")
        wbksheet.write(0, 1, "词")
        wbksheet.write(0, 2, "标注")
        i = 1
        for n in nounset:
            # print '名词：',n
            wbksheet.write(i, 0, "名词")
            wbksheet.write(i, 1, n)
            i += 1
        for a in adjectiveset:
            wbksheet.write(i, 0, "形容词")
            wbksheet.write(i, 1, a)
            i += 1
            # print '形容词：',a

        wbk.save(self.outfile)

    # 通过标注的dict字典中，对评论进行自己标注,把整段句子切分后在进行存储
    def annotationformat(self):
        """读取filename进行分词，同时对分词判断是否在nounwords或adjectivewords中，
        如果出现则进行标注"""
        dataexcel = xlrd.open_workbook(self.filename)

        sheet = dataexcel.sheet_by_name(u"" + self.sheet + "")  # 通过名称获取
        rows = sheet.nrows  # 获取行数 并暂时也代表总数
        # cols = sheet.ncols  # 获取列数

        wbk = xlwt.Workbook(encoding='utf-8')  # 创建一个新的excel
        wbksheet = wbk.add_sheet("Sheet1", cell_overwrite_ok=False)
        rownum = 0
        for r in range(0, rows):
            row = sheet.row_values(r)
            subsection = utile()
            content = row[0]
            resultlists = subsection.subsection(content.encode("utf-8"))
            for r in resultlists:
                seg_list = jieba.cut(r)
                entitytaggin = ''  # 实体标注
                wordlists = []  # 写入excel时的词
                tagginglists = []  # 写入excel时的词标注
                for seg in seg_list:
                    if (seg.encode("utf-8") not in stopwords and seg != ' ' and seg != '\n' and seg != '\n\n'):
                        if nounwords.has_key(seg):
                            entityword = seg
                            entitytaggin = nounwords.get(seg)
                            wordlists.append(entityword)
                            tagginglists.append(entitytaggin)
                            # print entityword,' ',entitytaggin
                        elif adjectivewords.has_key(seg):
                            adjectiveword = seg
                            taggingword = adjectivewords.get(seg)
                            wordlists.append(adjectiveword)
                            # tagginglists.append(taggingword) # 不进行实体属性和形容词拼接
                            if (entitytaggin == 'N' or entitytaggin == ''):
                                tagginglists.append('I-MB')
                            else:
                                tagginglists.append('I-' + entitytaggin[2:])
                        else:
                            wordlists.append(seg)
                            tagginglists.append('N')

                for i in range(0, len(wordlists)):  # 如果形容词前出现副词，那就给副词也打上跟形容词一样的标注
                    if statwords.has_key(wordlists[i].encode("utf-8")):
                        if i + 1 != len(wordlists):
                            if tagginglists[i + 1] != 'N':
                                tagginglists[i] = tagginglists[i + 1]
                # 调用存储函数，把词和标注放到excel中
                wbksheet.write(rownum, 0, row[0])
                self.xlwtText(wbksheet, rownum, len(wordlists), wordlists, tagginglists)
                rownum += 2
        wbk.save(self.outfile)

    def xlwtText(self, wbksheet, rownum, colelen, wordlists, tagginglists):
        """此函数主要是对结果进行输出,rownum(行),colelen(列),wordlists(词),tagginglists(词对应的标注)"""
        for j in range(0, colelen):
            wbksheet.write(rownum, j + 1, wordlists[j])
            wbksheet.write(rownum + 1, j + 1, tagginglists[j])

if __name__ == '__main__':
    # 从原评论中提取出名词和形容词
    # NounAdjectivesExcel = crftraindata(u"整体评论-联想手机全部.xlsx",u"Sheet1",u'名词形容词.xls',False)
    # NounAdjectivesExcel.generatingNounAdjectivesExcel()
    # 提取出excel中的名词和形容词
    # readexcel(u"整体评论-联想手机全部.xlsx",u"Sheet1",u'名词形容词.xls')

    # 给文本自动打标注
    annotatformat = crftraindata(u'整体评论-联想手机训练.xlsx', u'Sheet1', u'结果.xls', False)
    annotatformat.annotationformat()




