# -*- coding=utf-8 -*-

import urllib
import urllib.request
import json
import http
import http.cookiejar
import re
import os
from urllib.parse import urlencode

TOKEN_URL = "https://passport.baidu.com/v2/api/?getapi&tpl=mn&apiver=v3&class=login#"
INDEX_URL = "http://www.baidu.com/"
LOGIN_URL = "https://passport.baidu.com/v2/api/?login"

reg_token = re.compile("\"token\"\s+:\s+\"(\w+)\"")

bdHeaders = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding":"gzip,deflate,sdch",
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Host":"passport.baidu.com",
                "Origin":"http://www.baidu.com",
                "Referer":"http://www.baidu.com/",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36 LBBROWSER",
             }

bdData = {
            "charset":"UTF-8",
            "token":"",
            "tpl":"mn",                               #重要,需要跟TOKEN_URL中的相同
            "u":"http://tieba.baidu.com/",
            "username":"",
            "password":"",
          }

class bdLogin:
    def __init__(self):
        self._cookie = http.cookiejar.LWPCookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookie))
        if (not os.path.isdir("./cookies")):
            os.mkdir("./cookies")


    def login(self, user = "", psw = ""):
        if(not os.path.exists("./cookies/baidu.cookie." + user)):
            self._initial()                         
            self._getToken()                         #取得token,必要

            bdData["username"] = user
            bdData["password"] = psw
            bdData["token"] = self._token

            request = urllib.request.Request(LOGIN_URL, headers = bdHeaders)
            self._opener.open(request, urlencode(bdData).encode("utf-8"))   #登录
            self._cookie.save("./cookies/baidu.cookie." + user, True, True)        #保存cookie
        else:
            self._cookie.load("./cookies/baidu.cookie." + user, True, True)        #加载cookie

        result = json.loads(self._opener.open("http://tieba.baidu.com/f/user/json_userinfo").read().decode("utf-8"))
        print (self._opener.open("http://tieba.baidu.com/f/user/json_userinfo").read().decode("utf-8"))
        if(result["no"] == 0):                                    #判断是否登录成功
            return self._opener
        else:
            return None


    def _getToken(self):
        self._token = reg_token.findall(str(self._opener.open(TOKEN_URL).read()))[0]

    def _initial(self):
        self._opener.open(INDEX_URL)

def main():
    robot = bdLogin()
    #传入用户名和密码
    for line in open("user.conf"):
        user, password = str(line).strip('\n').split(",")
        # print(user)
        # print(password)
        opener = robot.login(user, password)

    #opener = robot.login("hslx1111", "lt86513624bd")


if __name__ == "__main__":
    main()