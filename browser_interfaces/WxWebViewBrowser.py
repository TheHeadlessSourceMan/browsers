#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Use a web browser based on a wxWebView control
"""
import os
from _browser import *

try:
	import wx
	import wx.html
	import wx.html2
	hasWxWebview=True
except:
	hasWxWebview=False


class WxWebViewBrowser(Browser,wx.Frame):
	"""
	Use a web browser based on a wxWebView control
	"""
	canRunJS=True
	canDoFullscreen=True
	canSetHtml=True
	canEmbed=True
	canDoTransparent=True

	name='WxWebViewBrowser'
	family='webkit' # TODO: I think this may be different on different oses

	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,
		headless=False,transparent=False,embedIn=None):
		"""
		To embed a wxWindow in a system window:
			https://forums.wxwidgets.org/viewtopic.php?t=4982

		TODO: scroll area not sizing right
			https://stackoverflow.com/questions/10838956/wxpython-scrolledwindow-too-small
			https://stackoverflow.com/questions/3392631/creating-scrolledwindow-in-wxpython
		"""
		Browser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
		if url is None:
			url=''
		if title is None:
			title=url
		self.app=wx.App(False)
		if transparent:
			style=wx.TRANSPARENT_WINDOW
		else:
			style=0
		# call parent constructor
		wxId=wx.ID_ANY
		wx.Frame.__init__(self,None,wxId,title,wx.DefaultPosition,style=wx.DEFAULT_FRAME_STYLE)
		self.panel=wx.ScrolledWindow(self,wx.ID_ANY)
		self.panel.SetScrollbars(1,1,1,1)
		self.panel.EnableScrolling(True,True)
		# create the browser
		backend=wx.html2.WebViewBackendDefault#wx.html2.WebViewBackendWebKit
		print 'Opening',url
		self.browser=wx.html2.WebView.New(self,-1,url,backend=backend,pos=(0,0),size=(w,h),style=style)
		# For debugging:
		#print dir(self.browser)
		self.Bind(wx.EVT_ERASE_BACKGROUND,lambda event: None)
		self.browser.Bind(wx.EVT_ERASE_BACKGROUND,lambda event: None)
		if transparent:
			self.SetTransparent(128)
			self.browser.SetTransparent(64)
			self.panel.SetTransparent(64)
		if fullscreen:
			self.ShowFullScreen(True)
		if embedIn!=None:
			self.app.GetHandle()
		self.Show(True)
		self.app.MainLoop()

	@property
	def hwnd(self):
		"""
		get the system window handle
		"""
		return self.app.GetHandle()

	def __del__(self):
		"""
		Clean stuff up on object delete
		"""
		pass#self.close()

	@property
	def url(self):
		"""
		get/set the current url
		"""
		return self.browser.GetCurrentURL()
	@url.setter
	def setUrl(self,url):
		"""
		get/set the current url
		"""
		self.go(url)
	def go(self,url):
		"""
		go to a specific url
		"""
		if url.find('://')<1:
			if os.sep!='/':
				url=url.replace('/',os.sep)
			url='file://'+os.path.abspath(url)
		self.browser.LoadURL(url)

	@property
	def html(self):
		"""
		get/set the current html
		"""
		return self.browser.GetPageSource()
	@html.setter
	def setHtml(self,html):
		"""
		get/set the current html
		"""
		self.browser.SetPage(html=html)

	@property
	def text(self):
		"""
		get/set the current html via converting plain text
		"""
		return self.browser.GetPageText(self)

	def runJS(self,js):
		"""
		Execute some javascript code
		"""
		self.browser.RunScript(js)

	def close(self):
		"""
		close this browser
		"""
		raise NotImplementedError() # TODO: implement window close

if hasWxWebview:
	BROWSER_LIST.append(WxWebViewBrowser)
