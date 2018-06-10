# -*- coding: utf-8-*-
import sys
import os
import logging
import json
import requests

WORDS = ["LUKUANG"]
SLUG = "roadcondition"

def request(url, params): 
    result = requests.post(url, data=params)
    return json.loads(result.text, encoding='utf-8')


def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    
    if SLUG not in profile or \
       'app_key' not in profile[SLUG] or \
       'adcode' not in profile[SLUG]:
        mic.say(u"插件配置有误，插件使用失败")
        return
        
    app_key = profile[SLUG]['app_key']  
    adcode  = profile[SLUG]['adcode']
    mic.say(u'哪条道路')
    input = mic.activeListen(MUSIC=True)
    if input is None:
        input = "龙岗大道"
    
  
    url_transit = "http://restapi.amap.com/v3/traffic/status/road"
    params = {"adcode" : adcode,"name" : input,"key" : app_key}
   
    res = request(url_transit,params)
    print res
    if res:        
        status = res["status"]
        if status == "1":
            print "status == 1"
            print res['trafficinfo']
            if len(res['trafficinfo']) > 0:
                trafficinfo = res['trafficinfo']['evaluation']['description']
                trafficinfo1 = res['trafficinfo']['description']
                mic.say(trafficinfo)
                mic.say(trafficinfo1)                
            else:
                mic.say(u"无法获取到信息")
                return
        else:
            logger.error(u"接口错误:")
            return
    else:
        logger.error(u"接口调用失败")
        return 


def isValid(text):
    return any(word in text for word in [u"路况"])
