# -*- coding: utf-8-*-
#微软小冰聊天插件

import requests
import sys
import time
import json
import os
reload(sys)
sys.setdefaultencoding('utf8')
SLUG = "XIAOICE"
WORDS = ["XIAOICE"]
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
    if SLUG not in profile or \
                    'get_cookie' not in profile[SLUG] or \
                    'send_cookie' not in profile[SLUG]:
        mic.say('小冰配置错误，暂无法使用')
        return
    get_cookie = profile[SLUG]['get_cookie']
    send_cookie = profile[SLUG]['send_cookie']


    if any(word in text for word in [u"召唤女神", u"找女神聊天"]):
        mic.say(u"我是人见人爱的小冰，快来和我聊聊天吧")
        mic.chatting_mode = True
        mic.skip_passive = True
    elif any(word in text for word in [u"不要女神了", u"再见女神"]):
        mic.say(u"轻轻的我走了，正如我轻轻地来。我们下次再聊吧")
        mic.skip_passive = False
        mic.chatting_mode = False
    else:
        message = text.replace('女神','').replace('，','')
        xiaoice = MS_xiaoice(get_cookie,send_cookie)
        xiaoice.send_message(message)
        txt = xiaoice.get_message()
        if txt:
            mic.say(txt)

def isValid(text):
    """
        Returns True if the input is related to weather.
        Arguments:
        text -- user-input, typically transcribed speech
    """
    return any(word in text for word in [u"女神"])



class MS_xiaoice(object):
    def __init__(self, get_cookie, send_cookie):
        self.text = ''
        self.now = str(int(time.time()))
        self.get_cookie = get_cookie
        self.send_cookie = send_cookie

    def send_message(self,text):
        if text != '':
            self.text = text
        else:
            return
        send_url = 'https://weibo.com/aj/message/add?ajwvr=6&__rnd=' + self.now
        headers = {
            'Referer': 'https://weibo.com/messages?topnav=1&wvr=6',
            'cookie': self.send_cookie
        }
        data = {
            'location': 'msgdialog',
            'module': 'msgissue',
            'style_id': '1',
            'text': self.text,
            'uid': '5175429989',
            'tovfids': '',
            'fids': '',
            'el': '[object HTMLDivElement]',
            '_t': '0'
        }
        try:
            sendMessage = requests.post(send_url, data=data, headers=headers)
            time.sleep(1)
            print '消息发送成功'
        except:
            print '消息发送失败'

    def get_message(self):
        get_url = 'https://m.weibo.cn/msg/messages?uid=5175429989&page=1'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/60.0.3112.113 Safari/537.36',
            'Referer': 'https://login.sina.com.cn/crossdomain2.php?action=login&entry=sinawap&r=\
            https%3A%2F%2Fpassport.weibo.cn%2Fsso%2Fcrossdomain%3Fservice%3Dsinawap%26display%3D0%26ssosavestate%3D153\
            6888171%26url%3Dhttps%253A%252F%252Fm.weibo.cn%252Fmsg%252Fmessages%253Fuid%253D5175429989%2526page%2\
            53D1%26ticket%3DST-NTM0MzE0MjMzMA%3D%3D-1505358289-tc-EA58DC48B5C15C0D82E8C7B93C38C651-1%26retcode%3D0',
            'cookie': self.get_cookie
        }
        getMessage = json.loads(requests.get(get_url, headers=header,verify=False).text)
        time.sleep(1)
        while getMessage['data'][0]['text'] == unicode(self.text,'utf-8'):
            getMessage = json.loads(requests.get(get_url, headers=header,verify=False).text)
        if getMessage['data'][0]['text'] == u'分享语音':
            tts_url = 'http://upload.api.weibo.com/2/mss/msget?source=351354573&fid=' \
                      + str(getMessage['data'][0]['attachment'][0]['fid'])
            r = requests.get(tts_url, headers=header)
            with open('/tmp/tts_voice.mp3', 'wb') as f:
                f.write(r.content)
            os.system('mplayer /tmp/tts_voice.mp3')
            return
        elif getMessage['data'][1]['text'] != unicode(self.text,'utf-8'):
            return getMessage['data'][1]['text'] + getMessage['data'][0]['text']
        else:
            return getMessage['data'][0]['text']