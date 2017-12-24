# -*- coding: utf-8-*-
import json
import logging
import os
import socket
import subprocess
import sys
import tempfile
import threading
from urllib import urlopen

reload(sys)
sys.setdefaultencoding('utf8')
socket.setdefaulttimeout(10)

WORDS = ["BAIDUYINYUE"]
SLUG = "baidufm"

DEFAULT_CHANNEL = 14


class MusicPlayer(threading.Thread):

    def __init__(self, playlist, logger):
        super(MusicPlayer, self).__init__()
        self.event = threading.Event()
        self.event.set()
        self.playlist = playlist
        self.idx = 0
        self.is_stop = False
        self.is_pause = False
        self.song_file = "dummy"
        self.directory = tempfile.mkdtemp()
        self.logger = logger

    def run(self):
        while True:
            if self.event.wait():
                self.play()
                if not self.is_pause:
                    self.pick_next()

    def play(self):
        self.logger.debug('MusicPlayer play')
        song_url = "http://music.baidu.com/data/music/fmlink?" +\
            "type=mp3&rate=320&songIds=%s" % self.playlist[self.idx]['id']
        song_name, song_link, song_size, song_time =\
            self.get_song_real_url(song_url)
        self.download_mp3_by_link(song_link, song_name, song_size)
        self.play_mp3_by_link(song_link, song_name, song_size, song_time)

    def get_song_real_url(self, song_url):
        try:
            htmldoc = urlopen(song_url).read().decode('utf8')
        except:
            return(None, None, 0, 0)

        content = json.loads(htmldoc)

        try:
            song_link = content['data']['songList'][0]['songLink']
            song_name = content['data']['songList'][0]['songName']
            song_size = int(content['data']['songList'][0]['size'])
            song_time = int(content['data']['songList'][0]['time'])
        except:
            self.logger.error('get real link failed')
            return(None, None, 0, 0)

        return song_name, song_link, song_size, song_time

    def play_mp3_by_link(self, song_link, song_name, song_size, song_time):
        process = subprocess.Popen("pkill play", shell=True)
        process.wait()
        if os.path.exists(self.song_file):
            if not self.is_stop:
                cmd = ['play', self.song_file]
                self.logger.debug('begin to play')
                with tempfile.TemporaryFile() as f:
                    subprocess.call(cmd, stdout=f, stderr=f)
                    f.seek(0)
                    output = f.read()
                    print(output)
            self.logger.debug('play done')
            if not self.is_pause:
                self.logger.debug('song_file remove')
                os.remove(self.song_file)

    def download_mp3_by_link(self, song_link, song_name, song_size):
        file_name = song_name + ".mp3"

        self.song_file = os.path.join(self.directory, file_name)
        if os.path.exists(self.song_file):
            return
        self.logger.debug("begin DownLoad %s size %d" % (song_name, song_size))
        mp3 = urlopen(song_link)

        block_size = 8192
        down_loaded_size = 0

        file = open(self.song_file, "wb")
        while True and not self.is_stop:
            try:
                buffer = mp3.read(block_size)

                down_loaded_size += len(buffer)

                if(len(buffer) == 0):
                    if down_loaded_size < song_size:
                        if os.path.exists(self.song_file):
                            os.remove(self.song_file)
                    break
                file.write(buffer)

                if down_loaded_size >= song_size:
                    self.logger.debug('%s download finshed' % self.song_file)
                    break

            except:
                if os.path.getsize(self.song_file) < song_size:
                    self.logger.debug('song_file remove')
                    if os.path.exists(self.song_file):
                        os.remove(self.song_file)
                break

        file.close()

    def pick_next(self):
        self.idx += 1
        if self.idx > len(self.playlist) - 1:
            self.idx = 0

    def pause(self):
        try:
            self.event.clear()
            self.is_pause = True
            subprocess.Popen("pkill play", shell=True)
        except:
            pass

    def resume(self):
        self.is_pause = False
        self.event.set()

    def stop(self):
        self.pause()
        self.is_stop = True
        self.playlist = []
        if os.path.exists(self.song_file):
            os.remove(self.song_file)
        if os.path.exists(self.directory):
            os.removedirs(self.directory)


def get_channel_list(page_url):
    try:
        htmldoc = urlopen(page_url).read().decode('utf8')
    except:
        return {}

    content = json.loads(htmldoc)
    channel_list = content['channel_list']

    return channel_list


def get_song_list(channel_url):
    try:
        htmldoc = urlopen(channel_url).read().decode('utf8')
    except:
        return{}

    content = json.loads(htmldoc)
    song_id_list = content['list']

    return song_id_list


def handle(text, mic, profile, bot=None):
    logger = logging.getLogger(__name__)
    page_url = 'http://fm.baidu.com/dev/api/?tn=channellist'
    channel_list = get_channel_list(page_url)

    if 'robot_name' in profile:
        persona = profile['robot_name']

    channel = DEFAULT_CHANNEL

    if SLUG in profile and 'channel' in profile[SLUG]:
        channel = profile[SLUG]['channel']

    channel_id = channel_list[channel]['channel_id']
    channel_name = channel_list[channel]['channel_name']
    mic.say(u"播放" + channel_name)

    while True:
        channel_url = 'http://fm.baidu.com/dev/api/' +\
            '?tn=playlist&format=json&id=%s' % channel_id
        song_id_list = get_song_list(channel_url)

        music_player = MusicPlayer(song_id_list, logger)
        music_player.start()

        while True:
            try:
                threshold, transcribed = mic.passiveListen(persona)
            except Exception, e:
                logger.error(e)
                threshold, transcribed = (None, None)

            if not transcribed or not threshold:
                logger.info("Nothing has been said or transcribed.")
                continue

            music_player.pause()
            input = mic.activeListen()

            if input and any(ext in input for ext in [u"结束", u"退出", u"停止"]):
                mic.say(u"结束播放", cache=True)
                music_player.stop()
                return
            else:
                mic.say(u"什么？", cache=True)
                music_player.resume()


def isValid(text):
    return any(word in text for word in [u"百度音乐", u"百度电台"])
