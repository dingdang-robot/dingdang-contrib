# -*- coding: utf-8 -*-
# 新闻插件
import sys
import os
import logging
import json, urllib
from urllib import urlencode

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["XINWEN"]
SLUG = "headline_news"

def request(appkey,type, mic, logger, m="GET"):
    url = "http://v.juhe.cn/toutiao/index"
    params = {
        "key" : appkey,
        "type" : type[1]
    }
    params = urlencode(params)
    if m == "GET":
        f = urllib.urlopen("%s?%s" % (url, params))
    else:
        f = urllib.urlopen(url, params)

    content = f.read()
    res = json.loads(content)
    if res:
        error_code = res["error_code"]
        if error_code == 0:
            mic.say(type[0] + u"新闻", cache=True)
            limit = 5;
            news = res["result"]["data"][0:limit]
            news_for_tts = ""
            for new in news:
                news_for_tts = news_for_tts + new["title"] + "."
            mic.say(news_for_tts, cache=True)
        else:
            logger.error(str(error_code) + ':' + res["reason"])
            mic.say(res["reason"], cache=True)
    else:
        mic.say(u"新闻接口调用错误", cache=True)

def getNewsType(text):
    newsTypes = {"头条":"top", "社会":"shehui","国内":"guonei", "国际":"guoji", "娱乐":"yule",
                 "体育":"tiyu", "军事":"junshi", "科技":"keji","财经":"caijing","时尚":"shishang"}
    newsType = ["头条","top"]
    for type in newsTypes:
        if type  in text:
            newsType = [type,newsTypes[type]]
    return  newsType

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)

    if SLUG not in profile or \
       'key' not in profile[SLUG]:
        mic.say(u"新闻插件配置有误，插件使用失败", cache=True)
        return
    key = profile[SLUG]['key']
    type = getNewsType(text)
    request(key,type, mic, logger)

def isValid(text):
    return u"新闻" in text
