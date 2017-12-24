# -*- coding: utf-8-*-
import sys
import os
import logging

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["BEIWANG"]
SLUG = "todo"

def file_input(file_path):
	global flist
	global line_number
	global last_line
	f=open('%s' % file_path,'r')
	flist=f.readlines()
	n = 0
	for fline in flist:
		n += 1
		line_number = n
		last_line = fline
	last_line = last_line.rstrip('\n')

def handle(text, mic, profile, wxbot=None):
	logger = logging.getLogger(__name__)
	if SLUG not in profile or \
		not profile[SLUG].has_key('file_path'):
		mic.say('备忘插件配置有误，插件使用失败', cache=True)
		return
	file_path = profile[SLUG]['file_path']
	if not os.path.isfile(file_path):
		os.system('touch %s' % file_path)
	os.system("sed -i '/^$/d' %s" % file_path)
	try:
		if any(word in text for word in [u"增加", u"添加"]):
			mic.say('请在滴一声后回复备忘内容', cache=True)
			input = mic.activeListen(MUSIC=True)
			if input is None:
				mic.say('抱歉，我没听清', cache=True)
				return
			else:
				os.system("echo %s >> %s" % (input, file_path))
				mic.say('好的，已添加备忘%s' % input, cache=True)
		elif any(word in text for word in [u"上", u"刚"]):
			try:
				file_input(file_path)
			except:
				mic.say('您还没有备忘', cache=True)
				return
			if any(word in text for word in [u"删除", u"清除"]):
				mic.say('即将删除上一条备忘%s，请在滴一声后进行确认' % last_line, cache=True)
				input = mic.activeListen(MUSIC=True)
				if input is not None and any(word in input for word in [u"确认", u"好", u"是", u"OK"]):
					os.system("sed -i '$d' %s" % file_path)
					mic.say('已删除上一条备忘', cache=True)
				else:
					mic.say('已取消', cache=True)
			else:
				mic.say('上一条备忘是：%s' % last_line, cache=True)
		else:
			try:
				file_input(file_path)
			except:
				mic.say('您还没有备忘', cache=True)
				return
			if any(word in text for word in [u"删除", u"清除", u"清空"]):
				mic.say('即将清空备忘，请在滴一声后进行确认', cache=True)
				input = mic.activeListen(MUSIC=True)
				if input is not None and any(word in input for word in [u"确认", u"好", u"是", u"OK"]):
					os.system('> %s' % file_path)
					mic.say('已清空备忘', cache=True)
				else:
					mic.say('已取消', cache=True)
			else:
				mic.say('您共有以下%d条备忘：' % line_number)
				for fline in flist:
					mic.say('%s' % fline)
	except Exception, e:
		logger.error(e)
		mic.say('抱歉，备忘插件出错', cache=True)
def isValid(text):
	return any(word in text for word in [u"备忘"])
