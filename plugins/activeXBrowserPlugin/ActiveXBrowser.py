#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Any browser registered with the windows ActiveX system.

Generally this means internet explorer or edge
"""
import typing
import urllib
from paths import UrlCompatible,Url
from browsers import Browser,BROWSER_LIST

try:
    import wx
    from wx import (wxFrame,wxLayoutConstraints,wxRight,wxLeft,wxTop,wxBottom,wxApp)
    from wx.lib.activexwrapper import MakeActiveXClass
    from win32com.client.gencache import EnsureModule
    hasActiveX=True

    print('TODO: ActiveX browser is present, but the code is not ready to use it.')
    print('Instead, just pretending like it doesn\'t exist.')
    hasActiveX=False
except ImportError as e:
    hasActiveX=False


class ActiveXBrowser(Browser):
    """
    Any browser registered with the windows ActiveX system.

    Generally this means internet explorer or edge
    """
    canRunJS=True

    name='ActiveXBrowser'
    family='ie'

    def __init__(self,
        url:typing.Optional[UrlCompatible]=None,
        w:int=800,h:int=600,
        title:str="",
        fullscreen:bool=False,
        headless:bool=False,
        transparent:bool=False,
        embedIn:typing.Optional[wx.Window]=None):
        """
        See http://wiki.wxpython.org/SynchronisingToInternetExplorer?highlight=(activex)

        https://www.codeproject.com/articles/3365/embed-an-html-control-in-your-own-window-using-pla
        """
        Browser.__init__(self,url,w,h,title,fullscreen,headless,transparent,embedIn)
        self._url:typing.Optional[Url]=None
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

    def runJS(self,js:str):
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
    def url(self,url:UrlCompatible):
        """
        get/set the current url
        """
        self._url=Url(url)
        self.browser.Navigate2(str(self._url))

    def close(self):
        """
        close this browser
        """
        raise NotImplementedError() # TODO:

    def wait(self)->int:
        """
        Wait for the browser to close and return the exit code
        """
        raise NotImplementedError() # TODO:


if hasActiveX:
    BROWSER_LIST.append(ActiveXBrowser)
