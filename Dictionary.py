# -*- coding: utf-8 -*-
import urllib
import re
from urllib import urlencode
import sys

reload(sys)
sys.setdefaultencoding('utf8')

SLUG = "dictionary"
WORDS = ["CHENGYU"]


def getHtml(words):
    url = 'http://dict.baidu.com/s'
    values = {'wd' : words}
    data = urlencode(values)
    html = ""
    try:
        response = urllib.urlopen("%s?%s" % (url, data))
        html = response.read()
    except :
        pass
    return html

def handleHtml(html):
    patten1 = re.compile('<div class="tab-content">.*?</div>', re.S)
    results = re.findall(patten1, html)
    str = ""
    for i in results:
        if "出自" in i:
            patten2 = re.compile("<li>(.*?)</li>", re.S)
            results2 = re.findall(patten2, i)
            str = results2[0] + results2[1]
    return str

def getWords(text):
    pattern1 = re.compile("成语.*?")
    pattern2 = re.compile(".*?的成语意思")

    if re.match(pattern1, text) != None:
        words = text.replace("成语", "")
    elif re.match(pattern2, text) != None:
        words = text.replace("的成语意思", "")
    else:
        words = ""
    words = words.replace(",","")
    words = words.replace("，","")
    return words

def info(html):
    pass

def handle(text, mic, profile, wxbot=None):
    words = getWords(text)
    if words:
        html = getHtml(words)
        info(html)
        if html:
            str = handleHtml(html)
            if str:
                mic.say(words + str, cache=True)
            else:
                mic.say("成语" + words +"有误 请重试", cache=True)

        else:
            mic.say(u"网络连接有误 请重试", cache=True)
    else:
        mic.say(u"没有听清楚 请重试", cache=True)

def isValid(text):
    return u"成语" in text
