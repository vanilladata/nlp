# encoding=utf8
import xlrd
import scipy.sparse as sp
import json


def culGongxian(docs, worddict=None):
    if (not isinstance(docs, list)) or len(docs) <= 0:
        raise Exception("culGongxian excption:[param docs not list or size is 0]!")

    # 将所有词 进行计算
    if worddict is None:
        worddict = set()
        for doc in docs:
            for token in doc:
                worddict.add(token)

    #
    voc2id = dict(zip(worddict, range(len(worddict))))
    rows, cols, vals = [], [], []
    for r, d in enumerate(docs):
        for e in d:
            if isinstance(e, unicode):
                innere = e.strip()
            else:
                innere = e
            if voc2id.get(innere) is not None:
                rows.append(r)
                cols.append(voc2id[innere])
                vals.append(1)
    X = sp.csr_matrix((vals, (rows, cols)))

    Xc = (X.T * X)  # coocurrence matrix
    Xc.setdiag(0)
    # print type(Xc)
    # print(Xc.toarray())
    result = Xc.toarray()

    termIdxValue = dict()
    for term, indx in voc2id.items():
        termIdxValue[indx] = term

    #
    resultObj = dict()
    for tokenIdx in range(0, len(result)):
        targetToken = termIdxValue[tokenIdx]
        tagRst = dict()
        gongxin = result[tokenIdx]
        for idx, value in enumerate(gongxin):
            tagRst[termIdxValue[idx]] = value
        resultObj[targetToken] = tagRst

    # 最后转化成对象返回
    # resultStr = json.dumps(resultObj)
    return resultObj


def test():
    worddict = set([u'万科', u'王健林', u'王思聪', u'万达'])
    docs = []
    dicttag = True
    workbook = xlrd.open_workbook(u'matrix-test.xlsx')
    sheet_names = workbook.sheet_names()
    if (len(worddict) > 0):
        dicttag = False
    for sheet_name in sheet_names:
        sheet2 = workbook.sheet_by_name(sheet_name)

        for rowindex in range(1, sheet2.nrows):
            row = sheet2.row_values(rowindex)
            doc = []
            for colindex in range(1, len(row)):
                doc.append(row[colindex])
                if dicttag:
                    worddict.add(row[colindex])
            docs.append(doc)
    print 'begin'

    result = culGongxian(docs, worddict)
    resultstr = json.dumps(result)
    print resultstr
    resultJson = json.loads(resultstr)
    print resultJson
