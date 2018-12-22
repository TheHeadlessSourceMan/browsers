#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A full-fledged standalone browser application.

There may be many different kinds on an os.  This
should locate and represent any of the major ones.
"""
import os
import signal
import time
from subprocess import Popen, PIPE
import urllib
from _browser import *


HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep

def getOpenerCommandForFile(filename,operation='open',w=None,h=None):
	"""
	Returns the command line for opening a given file
	(currently only supports Windows)
	"""
	ext=filename.rsplit('/',1)[-1].split('?',1)[0].rsplit('.',1)[-1]
	key='.'+ext
	reg_query="reg query HKCR\\"+key
	#print reg_query
	text=Popen(reg_query,stdout=PIPE).communicate()[0].split("\n")
	for line in text:
		line=line.lstrip()
		if line and (line[0]=='<' or line[0]=='('):
			key=line.split()[2]
			break
	#print key
	reg_query="reg query HKCR\\"+key+"\\shell\\"+operation+"\\command"
	#print reg_query
	text=Popen(reg_query,stdout=PIPE).communicate()[0].split("\n")
	command=None
	for line in text:
		line=line.lstrip()
		if line and (line[0]=='<' or line[0]=='('):
			command=' '.join(line.split()[2:])
			break
	params=''
	if command.find('firefox')>=0:
		profile=HERE+'firefox_profile'
		# trick firefox into opening a new window/process
		params='-no-remote -profile "'+profile+'"'
		#params='-new-window'
		if w!=None:
			params=params+' -width '+str(w)
		if h!=None:
			params=params+' -height '+str(h)
		# remove existing params so it does the right thing
		if command[0]=='"':
			command=command[1:].split('"',1)
			command='"'+command[0]+'" "%1"'
		else:
			command=command.split(' ',1)
			command=command[0]+' "%1"'
	# add any additional parameters
	if command[0]=='"':
		command=command[1:].split('"',1)
		command='"'+command[0]+'" '+params+command[1]
	else:
		command=command.split(' ',1)
		command=command[0]+' '+params+' '+command[1]
	#print command
	if command is None:
		return command
	if command.find('%1')<1:
		return command+' '+filename
	return command.replace('%1',filename)


def setTransparency(hwnd,amount):
	"""
	This is how the method SetTransparent()is implemented
	 on all MS Windows platforms.
	"""
	try:
		import ctypes
		_winlib=ctypes.windll.user32
		style=_winlib.GetWindowLongA(hwnd,0xffffffecL)
		style|=0x00080000
		_winlib.SetWindowLongA(hwnd,0xffffffecL,style)
		_winlib.SetLayeredWindowAttributes(hwnd,0,amount,2)
	except ImportError:
		import win32api
		import win32con
		import winxpgui
		_winlib=win32api.LoadLibrary("user32")
		pSetLayeredWindowAttributes=win32api.GetProcAddress(_winlib,"SetLayeredWindowAttributes")
		if pSetLayeredWindowAttributes is None:
			return
		exstyle=win32api.GetWindowLong(hwnd,win32con.GWL_EXSTYLE)
		if (exstyle&0x80000)==0:
			win32api.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,exstyle|0x80000)
	winxpgui.SetLayeredWindowAttributes(hwnd,0,amount,2)


def enquote(path):
	"""
	enclose a windows path in quotes if necessary
	"""
	if path.find(' ')>=0:
		return '"'+path+'"'
	return path


def filenameToFamily(name):
	"""
	Assume the browser's family type based on the filename
	"""
	name=name.rsplit(os.sep,1)[-1].split('.',1)[0].lower()
	if name in ['firefox','mozilla','palemoon']:
		return 'mozilla'
	elif name in ['ie','iexplore','edge','msedge']:
		return 'ie'
	elif name in ['webkit','chrome']:
		return 'webkit'
	return 'other'


def findChrome():
	"""
	find installed versions of google chrome

	returns []
	"""
	found=[]
	chromepath=os.path.abspath(os.environ['LOCALAPPDATA']+r'\Google')
	if os.path.isdir(chromepath):
		for app in ['Chrome',r'Application\chrome.exe']:
			if os.path.exists(chromepath+'\\'+app):
				found.append(enquote(chromepath+'\\'+app))
	# search registry HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\Application
	return found


def findFirefox():
	"""
	Find firefox and variants

	returns []
	"""
	found=[]
	for pf in [r'C:\Program Files',r'C:\Program Files (x86)']:
		test=pf+r'\Mozilla Firefox\firefox.exe'
		if os.path.isfile(test):
			found.append(enquote(test))
		test=pf+r'\Palemoon\palemoon.exe'
		if os.path.isfile(test):
			found.append(enquote(test))
	# check HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox\*\Main\PathToExe
	return found


def findIexplore():
	"""
	find installed internet explorer

	returns []
	"""
	found=[]
	for pf in [r'C:\Program Files',r'C:\Program Files (x86)']:
		test=pf+r'\internet Explorer\iexplore.exe'
		if os.path.isfile(test):
			found.append(enquote(test))
	# check HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Capabilities\ApplicationDescription
	# NOTE: this is a string in the exe's stringtable, so rsplit(',',1)[0])
	return found


def findDefault():
	"""
	Get the system default browser.

	returns (family,app) or None
	"""
	path=getOpenerCommandForFile('x.html')
	if path is None or path=='':
		return None
	if path[0]=='"':
		path=path.split('"',2)[1]
	else:
		path=path.split(' ',1)[0]
	return (filenameToFamily(path),enquote(path))


def findAll():
	"""
	Find all browsers on the system

	returns [(family,app)]
	"""
	ret={} # this dict is {path,family}
	for app in findChrome():
		ret[app]='webkit'
	for app in findFirefox():
		ret[app]='mozilla'
	for app in findIexplore():
		ret[app]='ie'
	family,app=findDefault()
	if app!=None:
		ret[app]=family
	return [(kv[1],kv[0]) for kv in ret.items()]


def embedSysWindow(putThisWindow,intoThisWindow):
	"""
	Moves a given window to a child of another window.

	On Windows, each window can be:
		integer hwnd
		string hwnd "0x" for hex or just a regular int

	TODO: this should be made to work on any os

	See also:
		https://stackoverflow.com/questions/170800/embedding-hwnd-into-external-process-using-setparent#335724
	"""
	import win32gui
	import win32con
	# make sure we have hwnds
	childHwnd=putThisWindow
	parentHwnd=intoThisWindow
	# Remove WS_POPUP style and add WS_CHILD style
	style=win32gui.GetWindowLong(childHwnd,win32con.GWL_STYLE)
	style &= ~(win32con.WS_POPUP)
	style |= win32con.WS_CHILD
	win32gui.SetWindowLong(childHwnd,win32con.GWL_STYLE,style)
	# set it
	win32gui.SetParent(childHwnd,parentHwnd)
	# make sure it behaves properly
	#;;win32gui.AttachThreadInput(childHwnd,parentHwnd)


class classproperty(property):
	"""
	combine both @classmethod and @property
	"""
	def __get__(self, cls, owner):
		return classmethod(self.fget).__get__(None, owner)()


class StandaloneBrowser(Browser):
	"""
	A full-fledged standalone browser application.

	There may be many different kinds on an os.  This
	should represent any of the major ones.
	"""
	canRunJS=True
	family=None
	app=None

	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,
		headless=False,transparent=False,embedIn=None):
		Browser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
		self._url=None
		self.browser=Popen(self.app)

	def __del__(self):
		"""
		Clean stuff up on object delete
		"""
		self.close()

	def runJS(self,js):
		"""
		Execute some javascript code
		"""
		self.url='javascript:'+urllib.quote(js+'\n;void(0);')

	@property
	def url(self):
		"""
		get/set the current url
		"""
		return self._url
	@url.setter
	def setUrl(self,url):
		"""
		get/set the current url
		"""
		self._url=url
		raise NotImplementedError() # TODO: Can I do this somehow??

	@classproperty
	def name(cls):
		"""
		determine and return the name of the browser application

		Developers take note:  This uses class-generator trickery
		which will be sure to cause all kinds of pylint errors.
		"""
		cmd=cls.app
		if cmd[0]=='"':
			cmd=cmd.split('"',2)[1]
		else:
			cmd=cmd.split(' ',1)[0]
		cmd=cmd.rsplit(os.sep,1)[-1].split('.',1)[0].lower()
		return 'standalone '+cmd

	def close(self):
		"""
		close this browser
		"""
		result=None
		if self.browser is not None:
			try:
				# windows kill process (either way works)
				import win32api
				if False:
					# use the api
					PROCESS_TERMINATE = 1
					handle=win32api.OpenProcess(PROCESS_TERMINATE,False,self.browser.pid)
					win32api.TerminateProcess(handle,-1)
					win32api.CloseHandle(handle)
				else:
					# use the command line
					cmd='taskkill /PID '+str(self.browser.pid)+' /T'
					result=Popen(cmd,stdout=PIPE).communicate()[0]
			except ImportError:
				# posix kill process
				os.kill(self.browser.pid,signal.SIGTERM)
				waitcycles=10
				while self.browser.poll()<0:
					time.sleep(0.1)
					waitcycles=waitcycles-1
					if waitcycles<=0:
						os.kill(self.browser.pid,-9)
					self.browser.poll()
					break
		self.browser=None
		return result

	def wait(self):
		"""
		Wait for the browser to close and return the exit code
		"""
		result=self.browser.wait()
		print '*** browser process completed'
		return result


# automatically search the system and figure everything out
i=0
for family,app in findAll():
	app=app.replace('\\','\\\\')
	exec("""
class StandaloneBrowser"""+str(i)+"""(StandaloneBrowser):
	family=r'"""+family+"""'
	app='"""+app+"""'
	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,headless=False,transparent=False,embedIn=None):
		StandaloneBrowser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
BROWSER_LIST.append(StandaloneBrowser"""+str(i)+""")
""")
	i=i+1
