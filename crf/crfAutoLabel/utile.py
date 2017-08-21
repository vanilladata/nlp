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