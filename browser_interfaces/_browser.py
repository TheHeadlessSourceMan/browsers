#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
The base class of what a browser looks like and what it can do.
"""


BROWSER_LIST=[] # list of all available browsers


class Browser(object):
	"""
	The base class of what a browser looks like and what it can do.
	"""

	canRunJS=False # can run javascript code we send it
	canDoFullscreen=False # browser can go fullscreen (useful for screensavers and such)
	canSetHtml=False # you can set the html contents
	canDoHeadless=False # can be run hidden (for rendering a webpage to get data, yet without showing the user anything)
	canDoMouse=False # can simulate mouse events
	canDoKeyboard=False # can simulate keyboard events
	canEditDom=False # you can edit the html (your application should use canRunJS as a fallback)
	canGetScreenshot=False # you can get a screenshot image
	canDoTransparent=False # can be floating/transparent
	canEmbed=False # able to be embedded in a system window

	name=''
	family='other'

	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,
		headless=False,transparent=False,embedIn=None):
		pass

	def runJS(self,js):
		"""
		Execute some javascript code
		"""
		raise NotImplementedError()

	@property
	def url(self):
		"""
		get/set the current url
		"""
		raise NotImplementedError()
	@url.setter
	def setUrl(self,url):
		"""
		get/set the current url
		"""
		raise NotImplementedError()

	@property
	def html(self):
		"""
		get/set the current html
		"""
		raise NotImplementedError()
	@html.setter
	def setHtml(self,html):
		"""
		get/set the current html
		"""
		raise NotImplementedError()

	@property
	def text(self):
		"""
		get/set the current html via converting plain text
		"""
		# TODO: default this to html() and text-to-html conversion
		raise NotImplementedError()
	@text.setter
	def setText(self,text):
		"""
		get/set the current html via converting plain text
		"""
		# TODO: default this to html-to-text conversion and setHtml()
		raise NotImplementedError()

	def close(self):
		"""
		close this browser
		"""
		raise NotImplementedError()

	def wait(self):
		"""
		Wait for the browser to close and return the exit code
		"""
		raise NotImplementedError()

	def getScreenshot(self):
		"""
		return a screenshot as a pil image
		"""
		raise NotImplementedError()

	def __repr__(self):
		"""
		return a string representation of this browser
		"""
		return self.name