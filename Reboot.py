# -*- coding: utf-8-*-
# 重启系统插件
import logging
import sys
import time
import subprocess

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["CHONGQI"]
SLUG = "reboot"

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    try:
        mic.say('将要重新启动系统，请在滴一声后进行确认，授权相关操作')
        input = mic.activeListen(MUSIC=True)
        if input is not None and any(word in input for word in [u"确认", u"好", u"是", u"OK"]):
            mic.say('授权成功，开始进行相关操作')
            time.sleep(3)
            subprocess.Popen("reboot -f", shell=True)
            return
        mic.say('授权失败，操作已取消，请重新尝试')
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，重新启动系统失败')

def isValid(text):
    return any(word in text for word in [u"重启", u"重新启动"])
