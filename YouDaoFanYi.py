# -*- coding: utf-8 
# 有道翻译插件

import logging
import json
import urllib
import time
import re
import requests
import md5
import random
import sys

reload(sys)
sys.setdefaultencoding('utf8')

SLUG = "youdao"
WORDS = ["FANYI"]

def translate(appId, appSecret, sentence):
    logger = logging.getLogger(__name__)             
    url = 'https://openapi.youdao.com/api'
    salt = random.randint(1, 65536)
    sign = appId+sentence+str(salt)+appSecret
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    params = {
             'q': sentence,
             'from': 'auto',
             'to': 'auto',
             'appKey': appId,
             'salt': salt,
             'sign': sign
    }
    result = requests.get(url, params=params)
    res = json.loads(result.text, encoding='utf-8')
    s = res['translation'][0]
    return s


def getSentence(text):
    pattern1 = re.compile("翻译.*?")
    pattern2 = re.compile(".*?的翻译")

    if re.match(pattern1, text) != None:
        sentence = text.replace("翻译", "")
    elif re.match(pattern2, text) != None:
        sentence = text.replace("的翻译", "")
    else:
        sentence = ""
    sentence = sentence.replace(",","")
    sentence = sentence.replace("，","")
    return sentence


def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    if SLUG not in profile or \
       'appId' not in profile[SLUG] or\
       'appSecret' not in profile[SLUG]:
        mic.say('有道翻译插件配置有误，插件使用失败', cache=True)
        return
    appId = profile[SLUG]['appId']
    appSecret = profile[SLUG]['appSecret']
    sentence = getSentence(text)
    logger.info('sentence: ' + sentence)
    if sentence:
        try:
            s = translate(appId, appSecret, sentence)
            if s:
                mic.say(sentence+"的翻译是" + s, cache=False)
            else:
                mic.say("翻译" + sentence +"失败，请稍后再试", cache=False)
        except Exception, e:
            logger.error(e)
            mic.say('抱歉, 我不知道怎么翻译' + sentence, cache=False)
    else:
        mic.say(u"没有听清楚 请重试", cache=True)

                                                            
def isValid(text):
    return u"翻译" in text
