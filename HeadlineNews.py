# -*- coding: utf-8 -*-
# 新闻头条插件
import sys
import os
import logging
import json, urllib
from urllib import urlencode

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["TOUTIAOXINWEN"]
SLUG = "headline_news"

def request(appkey, mic, logger, m="GET"):
    url = "http://v.juhe.cn/toutiao/index"
    params = {
        "key" : appkey,
        "type" : "top",
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
            limit = 5;
            news = res["result"]["data"][0:limit]
            news_for_tts = ""
            for new in news:
                news_for_tts = news_for_tts + new["title"] + "."
            mic.say(news_for_tts)
        else:
            logger.error(str(error_code) + ':' + res["reason"])
            mic.say(res["reason"])
    else:
        mic.say(u"新闻头条接口调用错误")


def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)

    if SLUG not in profile or \
       'key' not in profile[SLUG]:
        mic.say(u"新闻头条插件配置有误，插件使用失败")
        return
    key = profile[SLUG]['key']
    request(key, mic, logger)

def isValid(text):
    return any(word in text for word in [u"新闻头条", u"头条新闻", u"头条"])
