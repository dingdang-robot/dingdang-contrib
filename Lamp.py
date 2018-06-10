# -*- coding: utf-8-*-  # 台灯控制
import sys
import os
import logging
import wiringpi 

sys.setdefaultencoding('utf8')

SLUG="Lamp"

WORDS=["TAIDENG"]

def handle(text, mic, profile, wxbot=None):

    logger = logging.getLogger(__name__)
    # get config
    pin=profile[SLUG]['pin']
    wiringpi.wiringPiSetupPhys()
    wiringpi.pinMode(pin,1)

    if any(word in text for word in [u"打开",u"开启"]):
        wiringpi.digitalWrite(pin,0)
        mic.say("好的，已经打开台灯")
    elif any(word in text for word in [u"关闭",u"关掉",u"熄灭"]):
        wiringpi.digitalWrite(pin,1)
        mic.say("好的，已经关闭台灯")
    return True


def isValid(text):
    """
        Returns True if the input is related to weather.
        Arguments:
        text -- user-input, typically transcribed speech
    """

    return u"台灯" in text
