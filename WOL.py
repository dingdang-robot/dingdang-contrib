# -*- coding: utf-8-*-
import socket, sys
import struct
import logging

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["KAIJI"]
SLUG = "wol"

def Waker(ip,mac):
	global sent
	def to_hex_int(s):
		return int(s.upper(), 16)
	
	dest = (ip, 9)

	spliter = ""
	if mac.count(":") == 5: spliter = ":"
	if mac.count("-") == 5: spliter = "-"

	parts = mac.split(spliter)
	a1 = to_hex_int(parts[0])
	a2 = to_hex_int(parts[1])
	a3 = to_hex_int(parts[2])
	a4 = to_hex_int(parts[3])
	a5 = to_hex_int(parts[4])
	a6 = to_hex_int(parts[5])
	addr = [a1, a2, a3, a4, a5, a6]
	
	packet = chr(255) + chr(255) + chr(255) + chr(255) + chr(255) + chr(255)
	
	for n in range(0,16):
		for a in addr:
			packet = packet + chr(a)
	
	packet = packet + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0)
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
	s.sendto(packet,dest)
	
	if len(packet) == 108:
		sent = True

def handle(text, mic, profile, wxbot=None):
	logger = logging.getLogger(__name__)
	if SLUG not in profile or \
		not profile[SLUG].has_key('ip') or \
		not profile[SLUG].has_key('mac'):
			mic.say('WOL配置有误，插件使用失败')
			return
	ip = profile[SLUG]['ip']
	mac = profile[SLUG]['mac']
	try:
		Waker(ip,mac)
		if sent:
			mic.say('启动成功')
	except Exception, e:
		logger.error(e)
		mic.say('抱歉，启动失败')


def isValid(text):
	return any(word in text for word in [u"开机", u"启动电脑", u"开电脑"])
