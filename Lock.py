# -*- coding: utf-8-*-
# 关闭系统插件
import logging
import sys
import time
import subprocess
import  httplib

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["GUANSUO"]
SLUG = "Lock"

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    try:
        mic.say('将要关闭车锁', cache=True)
        mic.say('三二一', cache=True)
        time.sleep(1)

        http_client=httplib.HTTPConnection('http://',80,timeout=20)
        http_client.request('GET','')
        r=http_client.getresponse()
        print  r.status
        print r.read()

        mic.say('关锁成功', cache=True)
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，关锁失败', cache=True)

def isValid(text):
    return any(word in text for word in [u"关锁", u"关闭车锁"])
