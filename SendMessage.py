# -*- coding: utf-8-*-
# 向微信好友发消息插件
import logging
import sys
import re
import time

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["FAXIN"]
SLUG = "send_message"

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    try:
        text_utf8 = text.decode('utf8')
        # 匹配规则：[给|向] XXX(微信昵称) [发信|发信息|发送信息|发送消息|发消息]  说 XXX(消息内容)
        # 微信昵称 -- 中文，名称2-15位长度; 消息内容 -- 1-25位长度
        PATTERN = ur'(给|向)([\u4e00-\u9fa5]{2,15})(发信|发送|发消息)(\S+)(说)(\S+)'
        pattern = re.compile(PATTERN)
        m = pattern.search(text_utf8)
        if not m or m.lastindex < 3:
            mic.say('抱歉，没能识别联系人，请重试')
            return;
        username = m.group(2)
        mic.say('好嘞，开始给%s送信' % (username))
        time.sleep(.3)
        if m.lastindex < 6:
            mic.say('抱歉，没有听清楚消息内容')
            return;
        msgbody = m.group(6)
        comfirm_input = u'确认'
        confirm_message_body = True
        if SLUG in profile:
            if 'confirm_message_body' in profile[SLUG]:
                confirm_message_body = profile[SLUG]['confirm_message_body']
        if confirm_message_body:
            mic.say('将要提交消息，消息内容是：%s，请在滴一声后确认' % (msgbody))
            comfirm_input = mic.activeListen(MUSIC=True)
        if comfirm_input is not None and any(word in comfirm_input for word in [u"确认", u"好", u"是", u"OK"]):
            wxbot.send_msg(username, msgbody, False)
            mic.say('提交成功，消息内容：%s' % (msgbody))
            return
        mic.say('确认失败，操作已取消，请重新尝试')
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，消息没有提交成功')

def isValid(text):
    return any(word in text for word in [u"发信", u"发送", u"发消息"])
