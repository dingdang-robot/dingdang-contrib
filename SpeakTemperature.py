# -*- coding: utf-8-*-
# 获取室温插件
import logging
import sys
import time
import socket
import subprocess
import RPi.GPIO as GPIO

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["SHIWEN"]
SLUG = "speak_temperature"


def getTempperature(temp):
    data = []
    j = 0
    channel =0 #输入GPIO号
    channel = int(temp)
    GPIO.setmode(GPIO.BCM)
    time.sleep(1)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(channel, GPIO.HIGH)
    GPIO.setup(channel, GPIO.IN)

    while GPIO.input(channel) == GPIO.LOW:
      continue
    while GPIO.input(channel) == GPIO.HIGH:
      continue

    while j < 40:
      k = 0
      while GPIO.input(channel) == GPIO.LOW:
        continue
      while GPIO.input(channel) == GPIO.HIGH:
        k += 1
        if k > 100:
          break
      if k < 8:
        data.append(0)
      else:
        data.append(1)
      j += 1
    print "sensor is working."
    print data
    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check = 0

    for i in range(8):
      humidity += humidity_bit[i] * 2 ** (7-i)
      humidity_point += humidity_point_bit[i] * 2 ** (7-i)
      temperature += temperature_bit[i] * 2 ** (7-i)
      temperature_point += temperature_point_bit[i] * 2 ** (7-i)
      check += check_bit[i] * 2 ** (7-i)

    tmp = humidity + humidity_point + temperature + temperature_point

    if check == tmp:
       print "temperature :", temperature, "*C, humidity :", humidity, "%"
       return "主人，当前家中温度"+str(temperature)+"摄氏度，湿度:百分之"+str(humidity)
    else:
      #print "wrong"
      #return "抱歉主人，传感器犯了点小错"
      getTempperature(channel)
    GPIO.cleanup()

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    if SLUG not in profile or \
       'gpio' not in profile[SLUG]:
        mic.say('DHT11配置有误，插件使用失败', cache=True)
        return
    if 'gpio' in profile[SLUG]:
        temp = profile[SLUG]['gpio']
    else:
        temp = profile['gpio']
    try:
        temper = getTempperature(temp)
        logger.debug('getTempperature: ', temper)
        mic.say(temper)
    except Exception, e:
        print "配置异常"
        logger.error(e)
        mic.say('抱歉，我没有获取到湿度', cache=True)

def isValid(text):
    return any(word in text for word in [u"室温", u"家中温度"])
