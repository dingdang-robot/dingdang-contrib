# -*- coding: utf-8-*-
# 网易云音乐播放插件
import logging
import threading
import hashlib
import time
import subprocess
import sys
import os
import random
from MusicBoxApi import api as NetEaseApi

reload(sys)
sys.setdefaultencoding('utf8')

# Standard module stuff
WORDS = ["YINYUE"]
SLUG = "netease_music"

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

    kwargs = {}
    kwargs['mic'] = mic

    logger.debug("Preparing to start netease music module")
    try:
        netease_wrapper = NetEaseWrapper(**kwargs)
    except:
        logger.error("Couldn't connect to NetEase server", exc_info=True)
        mic.say(u"访问网易云音乐失败了，请稍后再试")
        return

    persona = 'DINGDANG'
    if 'robot_name' in profile:
        persona = profile['robot_name']

    robot_name_cn = u'叮当'
    if 'robot_name_cn' in profile:
        robot_name_cn = profile['robot_name_cn']

    logger.debug("Starting music mode")

    music_mode = MusicMode(persona, robot_name_cn, mic, netease_wrapper, wxbot)
    music_mode.stop = False

    # 登录网易云音乐
    account = ''
    password = ''
    if SLUG in profile:
        if 'account' in profile[SLUG]:
            account = profile[SLUG]['account']
        if 'password' in profile[SLUG]:
            password = profile[SLUG]['password']
    if account == '' or password == '':
        mic.say("请先配置好账户信息再找我播放音乐")
        return

    has_login = False
    if not (os.path.exists('userInfo')):
        mic.say("稍等，正在为您登录网易云音乐")
        res = music_mode.login(account, password)
        if res:
            mic.say("登录成功")
            has_login = True
    else:
        has_login = True

    if not has_login:
        mic.say("登录失败, 退出播放. 请检查配置, 稍后再试")
        return

    if wxbot is not None:
        wxbot.music_mode = music_mode

    if any(word in text for word in [u"歌单", u"我的"]):
        music_mode.handleForever(1)  # 1: 用户歌单
    else:
        # 默认播放推荐歌曲
        music_mode.handleForever(0)  # 0: 推荐榜单
    logger.debug("Exiting music mode")
    return


def isValid(text):
    """
        Returns True if the input is related to music.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return any(word in text for word in [u"听歌", u"音乐", u"播放",
                                         u"唱歌", u"唱首歌", u"歌单",
                                         u"榜单"])


# The interesting part
class MusicMode(object):

    def __init__(self, PERSONA, robot_name_cn, mic,
                 netease_wrapper, wxbot=None):
        self._logger = logging.getLogger(__name__)
        self.persona = PERSONA
        self.robot_name_cn = robot_name_cn
        self.music = netease_wrapper
        self.mic = mic
        self.wxbot = wxbot
        self.search_mode = False
        self.to_listen = True
        if self.wxbot is not None:
            self.msg_thread = threading.Thread(target=self.wxbot.proc_msg)

    def login(self, account, password):
        return self.music.login(account, password)

    def delegateInput(self, input, call_by_wechat=False):

        command = input.upper()
        if command.startswith(self.robot_name_cn+": "):
            return

        if call_by_wechat:
            self._logger.debug('called by wechat')
            self.music.stop()
            time.sleep(.1)

        # check if input is meant to start the music module
        if u"榜单" in command:
            self.mic.say(u"播放榜单音乐")
            self.music.update_playlist_by_type(0)
            self.music.play()
            return
        elif u"歌单" in command:
            self.music.update_playlist_by_type(1)
            self.music.play()
            return
        elif any(ext in command for ext in [u"停止聆听", u"关闭聆听", u"别听我的"]):
            if self.wxbot is None or not self.wxbot.is_login:
                self.mic.say(u"您还未登录微信，不能关闭语音交互功能")
                return
            self.mic.say(u"关闭语音交互功能")
            self.to_listen = False
            self.music.play(False)
            return
        elif any(ext in command for ext in [u"恢复聆听", u"开始聆听", u"开启聆听", u"听我的"]):
            self.mic.say(u"开启语音交互功能")
            self.to_listen = True
            self.music.play(False)
            return
        elif u"暂停" in command:
            self.mic.say(u"暂停播放")
            self.music.pause()
            return
        elif any(ext in command for ext in [u"结束", u"退出", u"停止"]):
            self.music.exit()
            self.mic.say(u"结束播放")
            if self.wxbot is not None:
                self.wxbot.music_mode = None
            return
        elif any(ext in command for ext in [u"大声", u"大声点", u"大点声"]):
            self.mic.say(u"大点声")
            self.music.increase_volume()
            return
        elif any(ext in command for ext in [u"小声", u"小点声", u"小声点"]):
            self.mic.say(u"小点声")
            self.music.decrease_volume()
            return
        elif any(
                 ext in command for ext in [
                                            u'下一首', u"下首歌", u"切歌",
                                            u"下一首歌", u"换首歌", u"切割",
                                            u"那首歌"]):
            self.mic.say(u"下一首歌")
            self.music.next()
            return
        elif any(ext in command for ext in [u'上一首', u'上一首歌', u'上首歌']):
            self.mic.say(u"上一首歌")
            self.music.previous()
            return
        elif any(ext in command for ext in [u'搜索', u'查找']):
            if call_by_wechat:
                self.search_mode = True
                self.mic.say(u"请直接回复要搜索的关键词")
                return
            else:
                self.mic.say(u"请在滴一声后告诉我您要搜索的关键词")
                input = self.mic.activeListen(MUSIC=True)
                if input is None or input.strip() == '':
                    self.mic.say("没有听到关键词呢，请重新叫我查找吧")
                    self.music.play(False)
                    return
                self.mic.say(u'正在为您搜索%s' % input)
                self.music.update_playlist_by_type(2, input)
                self.music.play()
            return
        elif u'什么歌' in command:
            self.mic.say(u"正在播放的是%s的%s" % (
                self.music.song['artist'],
                self.music.song['song_name']))
            self.music.play(False)
            return
        elif u'随机' in command:
            self.mic.say(u"随机播放")
            self.music.randomize()
            return
        elif u'顺序' in command:
            self.mic.say(u"顺序播放")
            self.music.serialize()
            return
        elif any(ext in command for ext in [u"播放", u"继续"]):
            if u'即将播放' not in command:
                self.music.play()
            return
        elif self.search_mode:
            self.search_mode = False
            input = command
            if input is None or input.strip() == '':
                self.mic.say("没有听到关键词呢，请重新叫我查找吧")
                self.music.play(False)
                return
            self.mic.say(u'正在为您搜索%s' % input)
            self.music.update_playlist_by_type(2, input)
            self.music.play()
        else:
            self.mic.say(u"没有听懂呢。要退出播放，请说退出播放")
            self.music.play(False)
            return
        return

    def handleForever(self, play_type=0):
        """
        进入音乐播放
        play_type - 0：播放推荐榜单；1：播放用户歌单
        """

        self.music.update_playlist_by_type(play_type)
        self.music.start()
        if self.wxbot is not None:
            self.msg_thread.start()
        while True:

            if self.music.is_stop:
                self._logger.info('Stop Netease music mode')
                return

            if not self.to_listen:
                self._logger.info("Listening mode is disabled.")
                continue

            try:
                self._logger.info('离线唤醒监听中')
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except Exception, e:
                self._logger.debug(e)
                threshold, transcribed = (None, None)

            if not transcribed or not threshold:
                self._logger.info("Nothing has been said or transcribed.")
                continue

            # 当听到呼叫机器人名字时，停止播放
            self.music.stop()
            time.sleep(.1)

            # 听用户说话
            input = self.mic.activeListen(MUSIC=True)

            if input:
                if any(ext in input for ext in [u"结束", u"退出", u"停止"]):
                    self.mic.say(u"结束播放")
                    self.music.stop()
                    self.music.exit()
                    return
                self.delegateInput(input)
            else:
                self.mic.say(u"什么？")
                if not self.music.is_pause:
                    self.music.play(False)


class NetEaseWrapper(threading.Thread):

    def __init__(self, mic):
        super(NetEaseWrapper, self).__init__()
        self.cond = threading.Condition()
        self.netease = NetEaseApi.NetEase()
        self.mic = mic
        self.userId = 33120312
        self.volume = 0.7
        self.song = None  # 正在播放的曲目信息
        self.idx = -1  # 正在播放的曲目序号
        self.random = False
        self.playlist = []
        self.is_pause = False
        self.is_stop = False

    def set_cond(self, cond):
        self.cond = cond

    def update_playlist_by_type(self, play_type, keyword=''):
        if play_type == 0:
            # 播放热门榜单音乐
            self.playlist = self.get_top_songlist()
        elif play_type == 1:
            # 播放用户歌单
            user_playlist = self.get_user_playlist()
            if user_playlist > 0:
                self.playlist = self.get_song_list_by_playlist_id(
                    user_playlist[0]['id'])
                if len(self.playlist) == 0:
                    self.mic.say("用户歌单没有歌曲，改为播放推荐榜单")
                    self.playlist = self.get_top_songlist()
            else:
                self.mic.say("当前用户没有歌单，改为播放推荐榜单")
                self.playlist = self.get_top_songlist()
        elif play_type == 2:
            # 搜索歌曲
            self.playlist = self.search_by_name(keyword)

    def get_top_songlist(self):  # 热门单曲
        music_list = self.netease.top_songlist()
        datalist = self.netease.dig_info(music_list, 'songs')
        playlist = []
        for data in datalist:
            music_info = {}
            music_info.setdefault("song_id", data.get("song_id"))
            music_info.setdefault("song_name", data.get("song_name"))
            music_info.setdefault("artist", data.get("artist"))
            music_info.setdefault("album_name", data.get("album_name"))
            music_info.setdefault("mp3_url", data.get("mp3_url"))
            music_info.setdefault("playTime", data.get("playTime"))
            music_info.setdefault("quality", data.get("quality"))
            playlist.append(music_info)
        return playlist

    def login(self, username, password):  # 用户登陆
        password = hashlib.md5(password).hexdigest()
        login_info = self.netease.login(username, password)
        if login_info['code'] == 200:
            res = True
            userId = login_info.get('profile').get('userId')
            self.userId = userId
            file = open("./userInfo", 'w')
            file.write(str(userId))
            file.close()
        else:
            res = False
        return res

    def get_user_playlist(self):  # 获取用户歌单
        play_list = self.netease.user_playlist(self.userId)  # 用户歌单
        return play_list

    def get_song_list_by_playlist_id(self, playlist_id):
        songs = self.netease.playlist_detail(playlist_id)
        song_list = self.netease.dig_info(songs, 'songs')
        return song_list

    def search_by_name(self, song_name):
        data = self.netease.search(song_name)
        song_ids = []
        if 'songs' in data['result']:
            if 'mp3Url' in data['result']['songs']:
                songs = data['result']['songs']

            else:
                for i in range(0, len(data['result']['songs'])):
                    song_ids.append(data['result']['songs'][i]['id'])
                songs = self.netease.songs_detail(song_ids)
        song_list = self.netease.dig_info(songs, 'songs')
        return song_list

    def current_song(self):
        if self.song is not None:
            return self.song['song_name']
        else:
            return ''

    def run(self):
        while True:
            if self.cond.acquire():
                self.play()
                self.pick_next()

    def play(self, report=True):
        if self.is_pause:
            self.is_pause = False
        if self.idx < len(self.playlist):
            if self.idx == -1:
                self.idx = 0
            if not self.random:
                song = self.playlist[self.idx]
            else:
                song = random.choice(self.playlist)
            self.song = song
            subprocess.Popen("pkill play", shell=True)
            if report:
                song['mp3_url'] = self.netease.songs_detail_new_api(
                    [song['song_id']])[0]['url']
            mp3_url = song['mp3_url']
            if mp3_url is None:
                self.next()
                self.cond.wait()
            try:
                if report:
                    self.mic.say(u"即将播放 %s %s" % (
                        song['artist'], song['song_name']))
                time.sleep(.1)
                subprocess.Popen("play -v %f %s" % (
                    self.volume, mp3_url), shell=True, stdout=subprocess.PIPE)
                self.cond.notify()
                self.cond.wait(int(song.get('playTime')) / 1000)
            except:
                pass
        else:
            try:
                subprocess.Popen("pkill play", shell=True)
                self.cond.notify()
                self.cond.wait()
            except:
                pass

    def notify(self):
        if self.cond.acquire():
            self.cond.notifyAll()
            self.cond.release()

    def previous(self):
        self.idx -= 2
        if self.idx < 0:
            self.idx = len(self.playlist) - 1
        self.notify()

    def pick_next(self):
        self.idx += 1
        if self.idx > len(self.playlist) - 1:
            self.idx = 0

    def next(self):
        self.notify()

    def randomize(self):
        self.random = True
        self.next()

    def serialize(self):
        self.random = False
        self.notify()

    def increase_volume(self):
        self.volume += .1
        if self.volume > 1:
            self.volume = 1
        self.notify()

    def decrease_volume(self):
        self.volume -= .1
        if self.volume < 0:
            self.volume = 0
        self.notify()

    def stop(self):
        try:
            subprocess.Popen("pkill play", shell=True)
            self.cond.notifyAll()
            self.cond.release()
            self.cond.wait()
        except:
            pass

    def pause(self):
        self.is_pause = True
        # 暂不支持断点续播，因此暂停和停止相同处理
        self.stop()

    def exit(self):
        self.is_stop = True
        self.playlist = []
        self.notify()
