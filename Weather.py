# -*- coding: utf-8-*-
# 天气插件
import logging
import requests
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# Standard module stuff
WORDS = ["TIANQI"]

def handle(text, mic, profile, wxbot=None):
    """
    Responds to user-input, typically speech text

    Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
        wxbot -- wechat bot instance
    """
    logger = logging.getLogger(__name__)
    # get config
    if 'seniverse_weather' not in profile or \
       not profile['seniverse_weather'].has_key('api_key') or \
       not profile['seniverse_weather'].has_key('location'):
        mic.say('天气插件配置有误，插件使用失败')
        return
    key = profile['seniverse_weather']['api_key']
    location = profile['seniverse_weather']['location']
    API = 'https://api.seniverse.com/v3/weather/daily.json'
    try:
        result = requests.get(API, params={
            'key': key,
            'location': location
        }, timeout=3)
        res = json.loads(result.text, encoding='utf-8')
        logger.debug(res)                    
        if res.has_key('results'):
            daily = res['results'][0]['daily']
            days = set([])
            day_text = [u'今天', u'明天', u'后天']
            for word in day_text:
                if word in text:
                    days.add(day_text.index(word))
            if not any(word in text for word in day_text):
                days = set([0, 1, 2])
            responds = u'%s天气：' % location
            for day in days:
                responds += u'%s：%s，最高气温%s摄氏度，最低气温%s摄氏度；' % (day_text[day], daily[day]['text_day'], daily[day]['high'], daily[day]['low'])
            mic.say(responds)
        else:
            mic.say('抱歉，我获取不到天气数据，请稍后再试')
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，我获取不到天气数据，请稍后再试')
        
    

def isValid(text):
    """
        Returns True if the input is related to weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return any(word in text for word in [u"天气", u"气温"])
