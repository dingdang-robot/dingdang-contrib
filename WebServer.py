# -*- coding: utf-8-*-
# HTTP服务器插件
import logging
import sys
import os
import time
import subprocess

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["LIULAN"]
SLUG = "webserver"

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    if 'wechat' not in profile or not profile['wechat'] or wxbot is None:
        mic.say(u'请先在配置文件中开启微信接入功能')
        return
    sys.path.append(mic.dingdangpath.LIB_PATH)
    dest_file = os.path.join(mic.dingdangpath.LOGIN_PATH, 'wxqr.png')
    wxbot.get_uuid()
    wxbot.gen_qr_code(dest_file)
    webport = "8080"
    if SLUG in profile:
        if 'webport' in profile[SLUG]:
            webport = profile[SLUG]['webport']
    # start server
    cmd = 'cd %s && python -m SimpleHTTPServer %s' % (mic.dingdangpath.LOGIN_PATH, webport)
    try:
        mic.say('正在启动服务器')
        subprocess.Popen(cmd, shell=True)
        time.sleep(3)
        success = u'后台服务器启动成功，服务端口：%s' % (webport)
        mic.say(success)
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，后台服务器启动失败')

def isValid(text):
    return any(word in text for word in [u"浏览", u"服务器"])
