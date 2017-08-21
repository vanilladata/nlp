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

import_dir = os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 'crftest')
sys.path.append(import_dir)
print "add :[%s]" % import_dir
# sys.path.insert(0, import_dir)
import crfppResult.crfppresult as crfpp


# crfppResult = __import__(file_name)


class CRFHttpHandler(BaseHTTPRequestHandler):
    """请求处理器类"""
    pathGetHandlerMap = {"/CRFTag/tagText": "testget"}
    pathPostHandlerMap = {"/CRFTag/tagText": "testDome", "/CRFTag/textEmotionTag": "textEmotionTag"}

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
        respData = getattr(self, "post" + func)()

        # response data in unicode
        # respData = respData.encode(enc)
        content = bytes.encode(respData, enc)  # 将应答信息编码为指定编码方式

        # write response data
        f = io.BytesIO()
        f.write(respData)
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
        # reqestJsonData = self.requestJsonData
        self.inner_logger.info(
            "tag for sentance:[%s]" % (
                MyCommonutils.getInStr(json.dumps(respDataList, ensure_ascii=False))))

        # respData = {"result": True, "respDatas": [
        #     {
        #         "tokens": ["这个", "冰箱", "很好", "快递", "很", "给力"],
        #         "lables": ["BI", "BI", "BI", "BI", "BI", "BI", "BI"]
        #     },
        #     {
        #         "tokens": ["这个", "冰箱", "很好", "快递", "很", "给力"],
        #         "lables": ["BI", "BI", "BI", "BI", "BI", "BI", "BI"]
        #     }
        # ]}

        respData = crfpp.crfpptest(respDataList)

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
