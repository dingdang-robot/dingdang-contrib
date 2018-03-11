# -*- coding: utf-8-*-
# 关闭系统插件
import logging
import sys
import time
import subprocess

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["GUANJI"]
SLUG = "halt"

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    try:
        mic.say('将要关闭系统，请在滴一声后进行确认，授权相关操作', cache=True)
        input = mic.activeListen(MUSIC=True)
        if input is not None and any(word in input for word in [u"确认", u"好", u"是", u"OK"]):
            mic.say('授权成功，开始进行相关操作', cache=True)
            time.sleep(3)
            subprocess.Popen("shutdown -h now", shell=True)
            return
        mic.say('授权失败，操作已取消，请重新尝试', cache=True)
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，关闭系统失败', cache=True)

def isValid(text):
    return any(word in text for word in [u"关机", u"关闭系统"])
