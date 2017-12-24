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
SLUG = "weather"

def analyze_today(weather_code, suggestion):
    """ analyze today's weather """
    weather_code = int(weather_code)
    if weather_code <= 8:
        if u'适宜' in suggestion:
            return u'今天天气不错，空气清新，适合出门运动哦'
        else:
            return u'空气质量比较一般，建议减少出行'
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


def fetch_weather(api, key, location):
    result = requests.get(api, params={
        'key': key,
        'location': location
    }, timeout=3)
    res = json.loads(result.text, encoding='utf-8')
    return res


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
    if SLUG not in profile or \
       'key' not in profile[SLUG] or \
       (
           'location' not in profile[SLUG] and
           'location' not in profile
       ):
        mic.say('天气插件配置有误，插件使用失败', cache=True)
        return
    key = profile[SLUG]['key']
    if 'location' in profile[SLUG]:
        location = profile[SLUG]['location']
    else:
        location = profile['location']
    WEATHER_API = 'https://api.seniverse.com/v3/weather/daily.json'        
    SUGGESTION_API = 'https://api.seniverse.com/v3/life/suggestion.json'
    try:
        weather = fetch_weather(WEATHER_API, key, location)
        logger.debug("Weather report: ", weather)
        if weather.has_key('results'):
            daily = weather['results'][0]['daily']
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
                responds += u'%s：%s，%s到%s摄氏度。' % (day_text[day], daily[day]['text_day'], daily[day]['low'], daily[day]['high'])
                if day == 0:
                    suggestion = fetch_weather(SUGGESTION_API, key, location)
                    if suggestion.has_key('results'):
                        suggestion_text = suggestion['results'][0]['suggestion']['sport']['brief']
                        analyze_res = analyze_today(daily[day]['code_day'], suggestion_text)
            responds += analyze_res
            mic.say(responds, cache=True)
        else:
            mic.say('抱歉，我获取不到天气数据，请稍后再试', cache=True)
    except Exception, e:
        logger.error(e)
        mic.say('抱歉，我获取不到天气数据，请稍后再试', cache=True)
        
    
def isValid(text):
    """
        Returns True if the input is related to weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return any(word in text for word in [u"天气", u"气温"])
