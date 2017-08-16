#encoding=utf8
import re

class utile:
    """公共函数类"""

    def subsection(self,content):
        """此函数主要是能文章内容进行分段"""
        # resultlist = re.split("。|！|？|；|，|\.|!|\?|:|,", content)
        resultlist = re.split("。|！|？|；|!|\?|:|\s|\t", content)
        while '' in resultlist:   #删除所有空行
            resultlist.remove('')
        return resultlist

    def readexcel(filename, sheet, outfile):
        # 从excel中读取数据并放入到list中，然后通过分词在把每个评论中的词性为（n和a）的值放入到set集合中

        nounset = set()  # 存入名词
        adjectiveset = set()  # 存入形容词
        dataexcel = xlrd.open_workbook(filename)

        sheet = dataexcel.sheet_by_name(u"" + sheet + "")  # 通过名称获取
        rows = sheet.nrows  # 获取行数 并暂时也代表总数
        # cols = sheet.ncols  # 获取列数

        for i in range(0, rows, 2):
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

        wbk.save(outfile)