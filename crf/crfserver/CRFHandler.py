# coding:utf8
# The BaseHTTPServer module has been merged into http.server in Python 3.
# import http.server
# from http.server import SimpleHTTPRequestHandler
# from http.server import BaseHTTPRequestHandler
# from __future__ import unicode_literals
from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse as urlparse
# from urllib import parse as urlparse
import traceback
import cgi
import io
import shutil
import json
import MyCommonutils
import os
import sys
import GongXianCul
from ExeContext import ExeContext
from SegmentUtil import JieBaSegment as segmentUtils

import_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
import_dir = os.path.abspath(os.path.join(import_dir, "crftest"))
sys.path.append(import_dir)

import crfppResult as crfpp


class CRFHttpHandler(BaseHTTPRequestHandler):
    """请求处理器类"""
    pathGetHandlerMap = {"/CRFTag/tagText": "testget"}
    pathPostHandlerMap = {"/CRFTag/tagText": "testDome", "/CRFTag/textEmotionTag": "textEmotionTag",
                          "/GXGX/culRelation": "culRelation", "/nlp/segment": "testSeg"}

    def parsePath(self):
        parsed_result = urlparse.urlparse(self.path)
        return parsed_result

    def do_GET(self):
        # parsed_result = urlparse.urlparse(self.path)
        parsed_result = self.parsePath()
        parsed_path = parsed_result.path
        self.inner_logger.info("Handle request for path:[%s],Method:[%s]" % (parsed_path, "Get"))

        if not (parsed_path in CRFHttpHandler.pathGetHandlerMap.keys()):  # pathGetHandlerMap.has_key("")
            self.inner_logger.error(
                "Handler request for path:[%s] error:[404,not illigel reuqest path!],Method:[%s]" % (
                    parsed_path, "Get"))
            self.send_error(404, "request is invalid!")
            return

        # 处理请求
        try:
            func = CRFHttpHandler.pathGetHandlerMap[parsed_path]
            message = getattr(self, "get" + func)()
            self.inner_logger.debug(
                "Handler request for path:[%s] success,Method:[%s] responseData:[%s]" % (
                    parsed_path, "Get", message))
            message = message.encode(encoding="utf-8")
            self.wfile.write(message)
            self.inner_logger.info(
                "Handle request for path:[%s] success,Method:[%s]." % (
                    parsed_path, "Get"))
        except Exception as excp:
            msg = "handler exception:[%s]." % (traceback.format_exc())
            self.inner_logger.error(msg)
        return

    def do_POST(self):
        parsed_result = self.parsePath()
        parsed_path = parsed_result.path
        self.inner_logger.debug("Handle request for path:[%s],Method:[%s]" % (parsed_path, "Post"))

        if not (parsed_path in CRFHttpHandler.pathPostHandlerMap.keys()):  # pathGetHandlerMap.has_key("")
            self.inner_logger.error(
                "Handler request for path:[%s] error:[404,not illigel reuqest path!],Method:[%s]" % (
                    parsed_path, "Post"))
            self.send_error(404, "request is invalid!")
            return

        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if not ctype == 'application/json':
            self.send_error(400, "content-type is invalid! only:[application/json] is supported.")
            return

        enc = "UTF-8"
        if not pdict["charset"] is None:
            enc = pdict["charset"]
            enc = enc.upper()

        self.encoding = enc

        if enc != "UTF-8":
            self.send_error(400, "charset is invalid! only:[UTF-8] is supported.")
            return
        # if ctype == 'multipart/form-data':
        # self.send_error(400, "content-type is invalid!")
        #     # postvars = cgi.parse_multipart(self.rfile, pdict)
        # elif ctype == 'application/x-www-form-urlencoded':
        #     self.send_error(400, "content-type is invalid!")
        #     # length = int(self.headers['content-length'])
        #     # postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        # else:
        #     postvars = {}
        #     self.inner_logger.debug(postvars.get("listName", "didn't find it"))
        datas = self.rfile.read(int(self.headers['content-length']))
        # datas = datas.decode(enc).encode()
        jsonData = json.loads(datas)
        self.requestJsonData = jsonData

        func = CRFHttpHandler.pathPostHandlerMap[parsed_path]
        respAllData = {}
        respAllData["result"] = True

        try:
            respData = getattr(self, "post" + func)()
        except Exception as excp:
            self.inner_logger.error(
                "Handle request for path:[%s] excption:[invoke fun exption.] funcName:[%s] ErrorMsg:[%s] Method:[%s]." % (
                    parsed_path, "post" + func, traceback.format_exc(), "Post"))
            respAllData[u"errorMsg"] = u"invoke fun:[%s] exption" % ("post" + func)
            respData = "{}"
            respAllData["result"] = False

        # response data in unicode str
        # 将应答的字符串 转化为对象
        respData = json.loads(respData)

        respAllData["respDatas"] = respData
        respAllDataStr = json.dumps(respAllData, encoding=self.encoding)
        content = bytes.encode(respAllDataStr, enc)  # 将应答信息编码为指定编码方式

        # write response data
        f = io.BytesIO()
        f.write(respAllDataStr)
        f.seek(0)
        # write header
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=%s" % enc)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()

        # write body
        shutil.copyfileobj(f, self.wfile)

        self.inner_logger.info(
            "Handle request for path:[%s] success,Method:[%s]." % (
                parsed_path, "Post"))
        return

    def posttestDome(self):
        # 指定返回编码
        reqestJsonData = self.requestJsonData
        if reqestJsonData["name"] and reqestJsonData["name"] == "王超超":
            self.inner_logger.debug("name:[%s]" % reqestJsonData["name"])
            respData = {"result": "true", "data": "hello 老大."}
        else:
            respData = {"result": "true", "data": "hello 小弟."}
        return respData

    def posttextEmotionTag(self):
        respDataList = self.requestJsonData["reqDatas"]

        if self.requestJsonData.has_key("modelPath"):
            modelPath = self.requestJsonData["modelPath"]
        else:
            modelPath = ExeContext.context["modelDir"]

        if self.requestJsonData.has_key("modelName"):
            modelName = self.requestJsonData["modelName"]
        else:
            modelName = ExeContext.context["modelName"]

        context = dict()
        context["modelPath"] = modelPath
        context["modelName"] = modelName

        # reqestJsonData = self.requestJsonData
        logStr = MyCommonutils.getInStr(json.dumps(respDataList, ensure_ascii=False))  # , ensure_ascii=False
        self.inner_logger.info("tag for sentance:[%s]" % (logStr))

        try:
            # -------------------------------测试代码-----------------------------#
            # 固定报文
            # respData = {u"result": True, u"respDatas": [
            #     {
            #         u"tokens": [u"这个", u"冰箱", u"很好", u"快递", u"很", u"给力"],
            #         u"lables": [u"BI", u"BI", u"BI", u"BI", u"BI", u"BI", u"BI"]
            #     },
            #     {
            #         u"tokens": [u"这个", u"冰箱", u"很好", u"快递", u"很", u"给力"],
            #         u"lables": [u"BI", u"BI", u"BI", u"BI", u"BI", u"BI", u"BI"]
            #     }
            # ]}
            # raise Exception("test excpiton.")
            # -------------------------------测试代码-----------------------------#
            # 调用CRFPP接口
            respData = crfpp.crfppresult.crfpptest(respDataList, context)
        except Exception as excp:
            self.inner_logger.error(
                "invoke crfppresult.crfpptest exception:[%s],Input params:[%s]" % (
                    traceback.format_exc(), json.dumps(respDataList)))
            raise excp

        respDataLog = json.dumps(respData, encoding=self.encoding, ensure_ascii=False)
        self.inner_logger.info(
            "tag for sentance success. result:[%s]" % (
                MyCommonutils.getInStr(respDataLog)))

        respData = json.dumps(respData, encoding=self.encoding)
        return respData

    def writeStr(self, str):
        str = str.encode(encoding="utf-8")
        self.wfile.write(str)

    def gettestget(self):
        self.inner_logger.debug("into gettestget ...")
        return "ok test success!"

    def postculRelation(self):
        jsonData = self.requestJsonData
        docs = jsonData[u"docs"]
        tokens = jsonData[u"tokens"]
        tokensSet = set()

        for token in tokens:
            tokensSet.add(token)
        result = GongXianCul.culGongxian(docs, tokensSet)

        # 记录日志
        respDataLog = json.dumps(result, encoding=self.encoding, ensure_ascii=False)
        self.inner_logger.info(
            "calculate gongxin ralation succes. result:[%s]" % (
                MyCommonutils.getInStr(respDataLog)))

        respData = json.dumps(result, encoding=self.encoding)
        return respData

    def posttestSeg(self):
        reqData = self.requestJsonData
        if None == segmentUtils.logger:
            segmentUtils.logger = self.inner_logger

        if u"text" in reqData:
            text = reqData[u"text"]
        else:
            raise Exception("text is null.")

        # 获取分词词典
        if u"dict" in reqData:
            dictFileName = reqData[u"dict"]
            result = segmentUtils.segment(text, dictFileName)
        else:
            result = segmentUtils.segment(text)

        # 记录日志
        respDataLog = json.dumps(result, encoding=self.encoding, ensure_ascii=False)
        self.inner_logger.info(
            "calculate gongxin ralation succes. result:[%s]" % (
                MyCommonutils.getInStr(respDataLog)))

        respData = json.dumps(result, encoding=self.encoding)
        return respData
        pass


class CRFManagerHandler(CRFHttpHandler):
    pathGetHandlerMap = {"/CRFServer/manager/stop": "stop",
                         "/CRFServer/manager/start": "start"}

    def do_GET(self):
        parsed_result = self.parsePath()
        parsed_path = parsed_result.path
        self.inner_logger.info("Handle request for path:[%s],Method:[%s]" % (parsed_path, "Get"))

        if not (parsed_path in CRFManagerHandler.pathGetHandlerMap.keys()):  # pathGetHandlerMap.has_key("")
            self.inner_logger.error(
                "Handler request for path:[%s] error:[404,not illigel reuqest path!],Method:[%s]" % (
                    parsed_path, "Get"))
            self.send_error(404, "request is invalid!")
            return

        # 处理请求
        try:
            func = CRFManagerHandler.pathGetHandlerMap[parsed_path]
            message = getattr(self, "get" + func)()
            self.inner_logger.debug(
                "Handle request for path:[%s] success,Method:[%s] responseData:[%s]" % (
                    parsed_path, "Get", message))
            message = message.encode(encoding="utf-8")
            self.wfile.write(message)
            self.inner_logger.info(
                "Handle request for path:[%s] success,Method:[%s]." % (
                    parsed_path, "Get"))
        except Exception as excp:
            msg = "handler exception:[%s]." % (traceback.format_exc())
            self.inner_logger.error(msg)
        return

    def getstop(self):
        self.inner_logger.debug("into getstop ...")
        self.innerCrfServer.tryStop()
        self.inner_logger.info("stop CRFServer success!")
        return "stop CRFServer success!"

    def getstart(self):
        self.inner_logger.info("into getstart ...")
        self.innerCrfServer.tryStart()
        self.inner_logger.info("start CRFServer success!")
        return "start CRFServer success!"

    def do_POST(self):
        pass
