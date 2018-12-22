#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Open up a mozilla browser using gtkmozembed
"""
from _browser import *

try:
	import urllib
	import gtkmozembed
	import gtk
	import gobject
	hasMozillaEmbedded=True
except:
	hasMozillaEmbedded=False


class MozillaBrowser(Browser):
	"""
	Open up a mozilla browser using gtkmozembed
	"""
	canRunJS=True

	name='MozillaBrowser'
	family='mozilla'

	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,
		headless=False,transparent=False,embedIn=None):
		Browser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
		self._url=None
		self.browser=gtkmozembed.MozEmbed()
		# Fun with GTK
		window=gtk.ScrolledWindow()
		box=gtk.VBox(homogeneous=False,spacing=0)
		window.add(box)
		box.pack_start(self.browser,expand=True,fill=True,padding=0)
		window.set_default_size(w,h)
		window.show_all()
		gtk.gdk.threads_init()
		thread.start_new_thread(gtk.main,())
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
		self.browser.load_url(url)

	def close(self):
		"""
		close this browser
		"""
		asynchronous_gtk_message(gtk.main_quit)()


if hasMozillaEmbedded:
	BROWSER_LIST.append(MozillaBrowser)
