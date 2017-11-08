import urllib.request
import urllib.parse
import json
import time
import re
import requests
import hashlib
import sys

reload(sys)
sys.setdefaultencoding('utf8')

SLUG = "youdao"
WORDS = ["FANYI"]


def translate(self,key):
         d = key
         m = hashlib.md5()
         u = 'fanyideskweb'  #判断是网页还是客户端
         # 由于网页是用的js的时间戳(毫秒)跟python(秒)的时间戳不在一个级别，所以需要*1000a
         f = str(int(time.time()*1000))
         c = "rY0D^0'nM0}g5Mm1z%1G4"
         #根据md5的方式：md5(u + d + f + c)，拼接字符串生成sign参数。
         m.update((u + d + f + c).encode('utf-8'))   #生成加密串
         data= {
             'i':d,
             'from':'AUTO',
             'to':'AUTO',            #判断是自动翻译还是人工翻译
             'smartresult':'dict',
             'client':u,
             'salt':f,               #当前时间戳
             'sign':m.hexdigest(),   #获取加密串
             'doctype':'json',
             'version':'2.1',
             'keyfrom':'fanyi.web',
             'action':'FY_BY_CLICKBUTTION', #判断按回车提交或者点击按钮提交的方式
             'typoResult':'true'
         }
         
         headers = {
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
             'Origin':'http://fanyi.youdao.com/',  #请求头最初是从youdao发起的，Origin只用于post请求
             'Referer':'http://fanyi.youdao.com/', #Referer则用于所有类型的请求
         }
         #print(data)
         #接口
         post = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule&sessionFrom=null'
         youdaojson = requests.post(post,headers = headers,data=data).json()
                                                                                                                            
         s=str(youdaojson['translateResult'][0][0]['tgt'])
         return s

                                                                                                                                             def getWords(text):
     pattern1 = re.compile("翻译.*?")
     pattern2 = re.compile(".*?的翻译")

     if re.match(pattern1, text) != None:
         words = text.replace("翻译", "")
     elif re.match(pattern2, text) != None:
         words = text.replace("的翻译", "")
     else:
         words = ""
     words = words.replace(",","")
     words = words.replace("，","")
     return words

def handle(text, mic, profile, wxbot=None):
    words = getWords(text)
    s=translate(words)
    if words:
        if s:
            mic.say(words+"的翻译是" + s)
        else:
            mic.say("翻译" + words +"有误 请重试")
    else:
        mic.say(u"没有听清楚 请重试")

                                                                                                                                                            
def isValid(text):
    return u"翻译" in text
