#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Any browser registered with the windows ActiveX system.

Generally this means internet explorer or edge
"""
import urllib
from _browser import *

try:
	from wx import *
	from wx.lib.activexwrapper import MakeActiveXClass
	from win32com.client.gencache import EnsureModule
	hasActiveX=True

	print 'TODO: ActiveX browser is present, but the code is not ready to use it.'
	print 'Instead, just pretending like it doesn\'t exist.'
	hasActiveX=False

except Exception,e:
	hasActiveX=False


class ActiveXBrowser(Browser):
	"""
	Any browser registered with the windows ActiveX system.

	Generally this means internet explorer or edge
	"""
	canRunJS=True

	name='ActiveXBrowser'
	family='ie'

	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,
		headless=False,transparent=False,embedIn=None):
		"""
		See http://wiki.wxpython.org/SynchronisingToInternetExplorer?highlight=(activex)

		https://www.codeproject.com/articles/3365/embed-an-html-control-in-your-own-window-using-pla
		"""
		Browser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
		self._url=None
		clsid='{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}'
		module=EnsureModule(clsid,0,1,1)
		theClass=MakeActiveXClass(module.WebBrowser,eventObj=self)
		self.browser=theClass(self,-1)
		self.uiControl=wxFrame(None,-1,title)
		self.uiControl.SetAutoLayout(True)
		lc=wxLayoutConstraints()
		lc.right.SameAs(self.uiControl,wxRight)
		lc.left.SameAs(self.uiControl,wxLeft)
		lc.top.SameAs(self.uiControl,wxTop)
		lc.bottom.SameAs(self.uiControl,wxBottom)
		self.browser.SetConstraints(lc)
		app=wxApp()
		self.uiControl.Show(True)
		app.SetTopWindow(self.uiControl)
		if url is not None:
			self.url=url

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
		self.browser.Navigate2(url)

	def close(self):
		"""
		close this browser
		"""
		raise NotImplementedError() # TODO:

	def wait(self):
		"""
		Wait for the browser to close and return the exit code
		"""
		raise NotImplementedError() # TODO:


if hasActiveX:
	BROWSER_LIST.append(ActiveXBrowser)
