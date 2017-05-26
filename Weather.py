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

def get_air_quality(PM25_API, pm25_key, location, logger):
    """ get air quality of current day """
    try:
        pm25_result = requests.get(PM25_API, params={
            'token': pm25_key,
            'city': location,
            'stations': 'no'
        }, timeout=3)
        pm25_res = json.loads(pm25_result.text, encoding='utf-8')
        logger.debug("PM2.5 report:", pm25_res)
        if len(pm25_res) > 0:
            return pm25_res[0]['quality']
        else:
            return ''
    except Exception, e:
        logger.error(e)
        return ''
    
    
def analyze_today(weather_code, quality):
    """ analyze today's weather """
    weather_code = int(weather_code)
    if weather_code <= 8:
        if quality in (u'良', u'优'):
            return u'今天天气不错，空气清新，适合出门运动哦'
        elif u'中' in quality:
            return u'空气质量不佳，不建议出外运动了哦'
        elif quality == "":
            return u'今天天气还不错呢'
        else:
            return u'空气质量太差，出门建议带口罩哦'
    elif weather_code in range(10, 16):
        return u'主人，出门记得带伞哦'
    elif weather_code in range(16, 19) or \
    weather_code in range(25, 30) or \
    weather_code in range(34, 37):
        return u'极端天气来临，尽量待屋里陪我玩吧'
    elif weather_code == 38:
        return u'天气炎热，记得多补充水分哦'
    elif weather_code == 37:
        return u'好冷的天，记得穿厚一点哦'
    else:
        return u''



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
    if 'weather' not in profile or \
       not profile['weather'].has_key('seniverse_key') or \
       not profile['weather'].has_key('pm25_key') or \
       not profile['weather'].has_key('location'):
        mic.say('天气插件配置有误，插件使用失败')
        return
    weather_key = profile['weather']['seniverse_key']
    pm25_key = profile['weather']['pm25_key']
    location = profile['weather']['location']
    WEATHER_API = 'https://api.seniverse.com/v3/weather/daily.json'
    PM25_API = 'http://www.pm25.in/api/querys/pm2_5.json'
    try:
        weather_result = requests.get(WEATHER_API, params={
            'key': weather_key,
            'location': location
        }, timeout=3)
        weather_res = json.loads(weather_result.text, encoding='utf-8')
        logger.debug("Weather report: ", weather_res)
        if weather_res.has_key('results'):
            daily = weather_res['results'][0]['daily']
            days = set([])
            day_text = [u'今天', u'明天', u'后天']
            for word in day_text:
                if word in text:
                    days.add(day_text.index(word))
            if not any(word in text for word in day_text):
                days = set([0, 1, 2])
            responds = u'%s天气：' % location
            analyze_res = ''
            for day in days:
                responds += u'%s：%s，最高气温%s摄氏度，最低气温%s摄氏度；' % (day_text[day], daily[day]['text_day'], daily[day]['high'], daily[day]['low'])
                if day == 0:
                    quality = get_air_quality(PM25_API, pm25_key, location, logger)
                    if quality != '':
                        responds += u'空气质量：%s' % quality
                    analyze_res = analyze_today(daily[day]['code_day'], quality)
            responds += analyze_res
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
    return any(word in text for word in [u"天气", u"气温", u"空气质量"])
