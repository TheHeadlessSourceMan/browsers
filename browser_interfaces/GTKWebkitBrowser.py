#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pop up a webkit browser using GTK
"""
from threading import thread
from _browser import *

try:
	import webkit
	import gtk
	import gobject
	hasGTKWebkit=True
except:
	hasGTKWebkit=False


class GTKWebKitBrowser(Browser):
	"""
	Pop up a webkit browser using GTK
	"""
	canRunJS=True
	canDoTransparent=True # TODO: this is here https://gist.github.com/tassoevan/9768713
		# https://stackoverflow.com/questions/324923/is-it-possible-to-render-web-content-over-a-clear-background-using-webkit

	name='GTKWebKitBrowser'
	family='webkit'

	def __init__(self,url=None,w=800,h=600,title="",fullscreen=False,
		headless=False,transparent=False,embedIn=None):
		Browser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
		self.browser=webkit.WebView()
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
		self.browser.execute_script(js)

	@property
	def url(self):
		"""
		get/set the current url
		"""
		return Browser.url
	@url.setter
	def setUrl(self,url):
		"""
		get/set the current url
		"""
		self.browser.open(url)

	def close(self):
		"""
		close this browser
		"""
		asynchronous_gtk_message(gtk.main_quit)()


if hasGTKWebkit:
	BROWSER_LIST.append(GTKWebKitBrowser)
