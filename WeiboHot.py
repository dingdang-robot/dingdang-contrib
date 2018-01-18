# -*- coding: utf8 -*-
# 输入：微博热门
from __future__ import unicode_literals
import re
import requests
import sys
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')
WORDS = ["WEIBORESOU"]
SLUG = "weibo_resou"

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent': user_agent}

index_dic = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
             '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
             '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
             '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
             '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
             '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
             '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
             '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
             '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45,
             '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50
             }


def handle(text, mic, profile, wxbot=None):
    if SLUG not in profile:
        mic.say(u'微博热搜插件未启用')
        return
    else:
        pass
    try:
        list_50, list_50_name, list_href2 = return_resou_realtime()
    except:
        mic.say('奇怪的事情发生了', cache=True)
        return
    text_utf8 = text.decode('utf8')
    PATTERN = u'(微博热门|微博热搜|微博热点)([\u4e00-\u6760]{0,3}[\d]{0,3})(条*)'
    pattern = re.compile(PATTERN)
    m = pattern.search(text_utf8)
    if len(m.group(2)) == 0 or (int(m.group(2))) > 0:
        if len(m.group(2)) == 0:
            num_mic = 10
            num = 10
        elif (int(m.group(2))) > 0 and (int(m.group(2))) < 21:
            num_mic = int(m.group(2))
            num = num_mic
        else:
            if wxbot:
                num_mic = 20
                mic.say(u'条数过多,只播放二十条,热搜将发到微信')
                if (int(m.group(2))) < len(list_50_name):
                    num = int(m.group(2))
                else:
                    num = len(list_50_name)
            else:
                if (int(m.group(2))) < len(list_50_name):
                    num_mic = int(m.group(2))
                else:
                    num_mic = len(list_50_name)
        
        if wxbot:
            list_send = list_50[0:num]
            list_send = str(list_send).replace('u\'', '\'')
            list_send = list_send.decode("unicode-escape")
            list_send = list_send.encode('utf-8')
            wxbot.send_msg_by_uid(list_send, 'filehelper')
        else:
            pass
        for i in range(num_mic):
            mic.say(list_50_name[i])
        mic.say(u'您对第几条感兴趣？', cache=True)
        interest = mic.activeListen(MUSIC=True)
        if not interest or len(interest) == 0:
            mic.say(u'没有收到指令，已结束', cache=True)
            return
        else:
            try:
                PATTERN_in = u'(第)([\u4e00-\u6760]{0,3}[\d]{0,3})(条*)'
                pattern_in = re.compile(PATTERN_in)
                m_in = pattern_in.search(interest)
                if isinstance(m_in.group(2), unicode):
                    pass
                else:
                    int(m_in.group(2))
            except:
                mic.say(u'指令有错误', cache=True)
                return
            try:
                if(int(m_in.group(2))) > 0 and (int(m_in.group(2))) < num_mic + 1:
                    index = int(m_in.group(2))
                    interest = get_interest(list_href2[index - 1])
                    interest = interest.encode('utf-8')
                    mic.say(interest)
                else:
                    mic.say(u'不存在这个序号的微博')
            except:
                if m_in.group(2) in index_dic:
                    index = index_dic[m_in.group(2)]
                    if index < len(list_href2):
                        interest = get_interest(list_href2[index - 1])
                        interest = interest.encode('utf-8')
                        mic.say(interest)
                    else:
                        mic.say(u'不存在这个序号的微博', cache=True)
                else:
                    mic.say(u'不存在这个序号的微博', cache=True)
    else:
        mic.say(u'指令有错误', cache=True)


def get_interest(url):
    url_get = requests.get(url, headers=headers)
    soup = BeautifulSoup(url_get.text, "html5lib")
    hot = soup.find_all('p', class_='comment_txt')
    x = (hot[0])
    x = str(x)
    rm_label = re.compile(r'<[^>]+>')
    rm_result = rm_label.sub('', x)
    rm_result = rm_result.replace('@', '').replace(
        '\n', '').replace('\r', '').replace('#', '')
    return rm_result


def resou(url):
    try:
        try:
            url_get = requests.get(url, headers=headers)
        except:
            print("微博热搜模块提醒您请检查网络或者微博服务器")
            return 0, 0, 0
        soup = BeautifulSoup(url_get.text, "html5lib")
        # 获取热搜名称
        # 获取热搜关注数
        # 获取热搜地址
        list_name = []
        list_num = []
        list_href = []
        for tag_name in soup.find_all(href=re.compile("Refer=top"), target="_blank"):
            if tag_name.string is not None:
                list_name.append(tag_name.string)
        for tag_num in soup.find_all(class_="star_num"):
            if tag_num.string is not None:
                list_num.append(tag_num.string)
        for tag_name in soup.find_all(href=re.compile("Refer=top"), target="_blank"):
            if tag_name['href'] is not None:
                tag_name_ = 'http://s.weibo.com' + tag_name['href']
                list_href.append(tag_name_)
        return list_name, list_num, list_href
    except:
        return 1, 1, 1


'''
#微博热搜前十
def return_resou_homepage():

    list_name1, list_num1, list_href1=resou(
        'http://s.weibo.com/top/summary?cate=homepage')
    return list_name1, list_num1, list_href1

'''


def return_resou_realtime():
    list_name2, list_num2, list_href2 = resou(
        'http://s.weibo.com/top/summary?cate=realtimehot')
    if list_num2 == 0 or list_num2 == 1:
        return 0
    else:
        list_href2 = list_href2[::2]
        list_50 = range(len(list_name2))
        list_50_name = range(len(list_name2))
        if(len(list_name2)) == 49:
            del list_href2[2]
        for i in range(len(list_name2)):
            list_50[i] = '第' + str(i + 1) + '条' + ' ' + '热搜值: ' + str(
                list_num2[i]) + ' ' + list_name2[i] + ' ' + list_href2[i] + '\n '
            list_50_name[i] = '第' + \
                str(i + 1) + '条' + '.' + list_name2[i] + '\n'
        return list_50, list_50_name, list_href2


def isValid(text):
    return any(word in text for word in [u"微博热搜", u"微博热点", u"微博热门"])


if __name__ == '__main__':

    try:
        a, b, c = return_resou_realtime()
        for x in a:
            print(x)
    except:
        print("奇怪的事情发生了")   # d, e, f=return_resou_homepage()
