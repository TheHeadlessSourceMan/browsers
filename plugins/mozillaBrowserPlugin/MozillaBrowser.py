#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Open up a mozilla browser using gtkmozembed
"""
import typing
import threading
from paths import Url,UrlCompatible
from browsers import Browser

try:
    import urllib
    import gtkmozembed
    import gtk
    import gobject
    hasMozillaEmbedded=True
except ImportError:
    hasMozillaEmbedded=False


class MozillaBrowser(Browser):
    """
    Open up a mozilla browser using gtkmozembed
    """
    canRunJS=True

    name='MozillaBrowser'
    family='mozilla'

    @classmethod
    def isAvailable(cls)->bool:
        return hasMozillaEmbedded

    def __init__(self,
        url:typing.Optional[UrlCompatible]=None,
        w:int=800,h:int=600,
        title:str="",
        fullscreen:bool=False,
        headless:bool=False,
        transparent:bool=False,
        embedIn:typing.Optional[typing.Any]=None):
        """ """
        Browser.__init__(self,
            url,w,h,title,fullscreen,headless,transparent,embedIn)
        self._url:typing.Optional[Url]=None
        self.browser=gtkmozembed.MozEmbed()
        # Fun with GTK
        window=gtk.ScrolledWindow()
        box=gtk.VBox(homogeneous=False,spacing=0)
        window.add(box)
        box.pack_start(self.browser,expand=True,fill=True,padding=0)
        window.set_default_size(w,h)
        window.show_all()
        gtk.gdk.threads_init()
        threading.Thread(target=gtk.main).start()
        if url is not None:
            self.url=url

    def __del__(self):
        """
        Clean stuff up on object delete
        """
        self.close()

    def runJS(self,js:str):
        """
        Execute some javascript code
        """
        self.url='javascript:'+urllib.quote(js+'\n;void(0);')

    @property
    def url(self)->typing.Optional[Url]:
        """
        get/set the current url
        """
        return self._url
    @url.setter
    def url(self,url:UrlCompatible):
        """
        get/set the current url
        """
        self._url=Url(url)
        self.browser.load_url(str(self._url))

    def close(self):
        """
        close this browser
        """
        asynchronous_gtk_message(gtk.main_quit)()

