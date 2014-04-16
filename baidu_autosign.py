# -*- coding=utf-8 -*-

import baidu_autologin
import re
import urllib
import urllib.request
import multiprocessing
import json
import pickle
import os
from urllib.parse import urlencode

TIEBA_URL = "http://tieba.baidu.com"
GETLIKE_URL = "http://tieba.baidu.com/f/like/mylike"
SIGN_URL = "http://tieba.baidu.com/sign/add"

reg_likeUrl = re.compile("<a href=\"([^\"]+)\" title=\"([^\"]+)\">")
reg_getTbs = re.compile("PageData.tbs = \"(\w+)\"")

def getTbTbs(opener, url):
    return reg_getTbs.findall(opener.open(TIEBA_URL + url).read().decode("gbk"))[0]

#获取喜欢的贴吧列表    
def getList(opener):
    return reg_likeUrl.findall(opener.open(GETLIKE_URL).read().decode("gbk"))
    
signHeaders = {
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36 LBBROWSER",
                "Host":"tieba.baidu.com",
                "Origin":"http://tieba.baidu.com",
                "Referer":"http://tieba.baidu.com",
              }

#要post的表格              
signData = {
            "ie":"utf-8",
            "kw":"",
            "tbs":"",
           }
    
class autoSign:
    def __init__(self, user = "", psw = ""):
        login = baidu_autologin.bdLogin()
        self._opener = login.login(user, psw)
        self.user = user
        
    def getList(self):           
        self._likeList = getList(self._opener)

        
    def sign(self):
        self.getList()
        pool = multiprocessing.Pool(processes = 4)
        list = []
        for url in self._likeList:                  #多进程执行
            list.append(pool.apply_async(self._signProcess, args = (url, )))
        
        for ret in list:                            #取回结果
            print(ret.get())
        
    def _signProcess(self, url):
        signData["kw"] = url[1]
        signData["tbs"] = getTbTbs(self._opener, url[0])   #获取tbs
        signHeaders["Referer"] = signHeaders["Origin"] + url[0]
        request = urllib.request.Request(SIGN_URL, headers = signHeaders)
        result = json.loads(self._opener.open(request, urlencode(signData).encode("utf-8")).read().decode("utf-8"))
        if(result["no"] == 0):           #签到成功
            return "{0}吧签到成功,今天是第{1}个签到!".format(url[1], result["data"]["uinfo"]["user_sign_rank"])
        elif(result["no"] == 1101):      #已签过
            return "{0}吧之前已经签到过了哦!".format(url[1])
        else:                            #出错
            return "未知错误!" + "\n" + url + "\n" + result
        
        
def main():
    for line in open("user.conf"):
        user, password = str(line).strip('\n').split(",")
        asRobot = autoSign(user, password)          #传入用户名和密码
        print ("User:" + user)
        asRobot.sign()
    
if(__name__ == "__main__"):
    main()