# -*- coding: utf-8-*-
import sys
import os
import logging
import json, urllib
from urllib import urlencode

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["XIANLU"]
SLUG = "direction"

def request(url, params):
    params = urlencode(params)

    f = urllib.urlopen("%s?%s" % (url, params))

    content = f.read()
    return json.loads(content)

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)

    mic.say(u'去哪里')
    input = mic.activeListen(MUSIC=True)
    if input is None:
        mic.say(u'已取消')
        return

    if SLUG not in profile or \
       'app_key' not in profile[SLUG] or \
       'city' not in profile[SLUG] or \
       'origin' not in profile[SLUG] or \
       'method' not in profile[SLUG]:
        mic.say(u"插件配置有误，插件使用失败")
        return

    app_key = profile[SLUG]['app_key']
    city = profile[SLUG]['city']

    url_place = "http://api.map.baidu.com/place/v2/suggestion"
    params_place = {
        "query" : input,
        "region" : city,
        "city_limit" : "true",
        "output" : "json",
        "ak" : app_key,
    }

    res = request(url_place, params_place)

    if res:
        status = res["status"]
        if status == 0:
            if len(res['result']) > 0:
                place_name = res['result'][0]["name"]
                destination = "%f,%f" % (res['result'][0]["location"]['lat'], res['result'][0]["location"]['lng'])
            else:
                mic.say(u"错误的位置")
                return
        else:
            logger.error(u"位置接口:" + res['message'])
            return
    else:
        logger.error(u"位置接口调用失败")
        return

    origin = profile[SLUG]['origin']

    url_direction = "http://api.map.baidu.com/direction/v2/transit"
    params_direction = {
        "origin" : origin,
        "destination" : destination,
        "page_size" : 1,
        "ak" : app_key,
    }

    res = request(url_direction, params_direction)
    if res:
        status = res["status"]
        if status == 0:
            if len(res['result']['routes']) > 0:
                direction = ""
                for step in res['result']['routes'][0]['steps']:
                    direction = direction + step[0]["instructions"] + "."
                    result = place_name + u"参考路线:" + direction
                if 'method' in profile[SLUG]:
                    if profile[SLUG]['method'] == "voice" or \
                        wxbot is None:
                        mic.say(result)
                    else:
                        wxbot.send_msg_by_uid(result, 'filehelper')
                        mic.say(u"已发送到微信")
            else:
                mic.say(u"导航错误")
                return
        else:
            logger.error(u"导航接口:" + res['message'])
            return
    else:
        logger.error(u"导航接口调用失败")
        return

def isValid(text):
    return any(word in text for word in [u"怎么去", u"线路", u"路线"])
