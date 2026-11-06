#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use a web browser based on a wxWebView control
"""
import typing
from paths import asUrl,UrlCompatible,Url
from browsers import Browser

try:
    import wx
    import wx.html
    import wx.html2
    hasWxWebview=True
except ImportError:
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

    @classmethod
    def isAvailable(cls)->bool:
        return hasWxWebview

    def __init__(self,
        url:typing.Optional[UrlCompatible]=None,
        w:int=800,h:int=600,
        title:str="",
        fullscreen:bool=False,
        headless:bool=False,
        transparent:bool=False,
        embedIn:typing.Optional[typing.Any]=None):
        """
        To embed a wxWindow in a system window:
            https://forums.wxwidgets.org/viewtopic.php?t=4982

        TODO: scroll area not sizing right
            https://stackoverflow.com/questions/10838956/wxpython-scrolledwindow-too-small
            https://stackoverflow.com/questions/3392631/creating-scrolledwindow-in-wxpython
        """
        Browser.__init__(self,
            url,w,h,title,fullscreen,headless,transparent,embedIn)
        if url is None:
            url=''
        if title is None or title=='': # type: ignore
            title=url
        self.app=wx.App(False)
        if transparent:
            style=wx.TRANSPARENT_WINDOW
        else:
            style=0
        # call parent constructor
        wxId=wx.ID_ANY
        wx.Frame.__init__(self,
            None,wxId,title,wx.DefaultPosition,style=wx.DEFAULT_FRAME_STYLE)
        self.panel=wx.ScrolledWindow(self,wx.ID_ANY)
        self.panel.SetScrollbars(1,1,1,1)
        self.panel.EnableScrolling(True,True)
        # create the browser
        backend=wx.html2.WebViewBackendDefault#wx.html2.WebViewBackendWebKit
        print('Opening',url)
        self.browser=wx.html2.WebView.New(
            self,-1,url,backend=backend,pos=(0,0),size=(w,h),style=style)
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
        if embedIn is not None:
            self.app.GetHandle()
        self.Show(True)
        self.app.MainLoop()

    @property
    def hwnd(self)->int:
        """
        get the system window handle
        """
        return self.app.GetHandle()

    def __del__(self):
        """
        Clean stuff up on object delete
        """
        #self.close()

    @property
    def url(self)->Url:
        """
        get/set the current url
        """
        return asUrl(self.browser.GetCurrentURL())
    @url.setter
    def setUrl(self,url:UrlCompatible):
        """
        get/set the current url
        """
        self.go(url)
    def go(self,url:UrlCompatible):
        """
        go to a specific url

        :param url: the url to navigate to
        """
        self.browser.LoadURL(str(asUrl(url)))

    @property
    def html(self)->str:
        """
        get/set the current html
        """
        return self.browser.GetPageSource()
    @html.setter
    def setHtml(self,html:str):
        """
        get/set the current html
        """
        self.browser.SetPage(html=html)

    @property
    def text(self)->str:
        """
        get/set the current html via converting plain text
        """
        return self.browser.GetPageText(self)

    def runJS(self,js:str):
        """
        Execute some javascript code
        """
        self.browser.RunScript(js)

    def close(self)->None:
        """
        close this browser
        """
        raise NotImplementedError() # TODO: implement window close

