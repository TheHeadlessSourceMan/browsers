#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Open up a webkit browser in QT
"""
import typing
from PIL import Image
from threading import Thread
from paths import Url,UrlCompatible,urlencode
from browsers import Browser
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4.QtWebKit import *
    from threading import Thread
    hasQTWebkit=True
except NotImplementedError:
    hasQTWebkit=False


class QTWebkitBrowser(Browser):
    """
    Open up a webkit browser in QT

    To install, go to:
        https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4

    For setting a system window as a parent:
        https://stackoverflow.com/questions/293774/how-to-create-a-qwidget-with-a-hwnd-as-parent

    TODO: need to set up mouse events something like:
        https://stackoverflow.com/questions/39559334/pysideqwebviews-mouse-move-and-mouse-press-events-freezing-html-document
    """
    canRunJS=True
    canGetScreenshot=True
    canDoTransparent=True # TODO: should be able to http://blog.qt.io/blog/2009/06/30/transparent-qwebview-or-qwebpage/
    canDoFullscreen=True

    name='QTWebkitBrowser'
    family='webkit'

    @classmethod
    def isAvailable(cls)->bool:
        return hasQTWebkit

    def __init__(self,
        url:typing.Optional[str]=None,
        w:int=800,h:int=600,
        title:str="",
        fullscreen:bool=False,
        headless:bool=False,
        transparent:bool=False,
        embedIn:typing.Optional[int]=None):
        """ """
        Browser.__init__(self,
            url,w,h,title,fullscreen,headless,transparent,embedIn)
        self.mpos=None
        self.thread=None
        #self.run(url,w,h,title,fullscreen,headless,transparent,embedIn)
        self.thread=Thread(target=self.run,args=(
            url,w,h,title,fullscreen,headless,transparent,embedIn))
        self.thread.start()

    def run(self,
        url:typing.Optional[str]=None,
        w:int=800,h:int=600,
        title:str="",
        fullscreen:bool=False,
        headless:bool=False,
        transparent:bool=False,
        embedIn:typing.Optional[int]=None):
        """
        Utility function to run the browser
        """
        self.mpos=None
        params:typing.List[str]=[]
        app=QApplication(params)
        self.browser=QWebView()
        print("QT Creating webkit version",qWebKitVersion())
        page=self.browser.page()
        if transparent:
            self.browser.setAttribute(Qt.WA_TranslucentBackground)
            self.browser.setAttribute(Qt.WA_OpaquePaintEvent,False)
            self.browser.setWindowFlags(Qt.FramelessWindowHint) # can't have window frame
            palette=page.palette()
            palette.setBrush(QPalette.Base,Qt.transparent)
            page.setPalette(palette)
        if fullscreen:
            self.browser.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.browser.setWindowFlags(Qt.FramelessWindowHint)
            qdw=QDesktopWidget()
            screen=qdw.screenGeometry(screen=1)
            self.browser.setGeometry(screen)
        else:
            self.browser.resize(w,h)
        self.browser.setWindowTitle(title)
        self.html='Loading...'
        if transparent:
            pass#self.browser.setStyleSheet("background:transparent;")
        self.browser.setMouseTracking(True)
        QObject.connect(self.browser,SIGNAL('mousePress()'),self.mousePressEvent)
        QObject.connect(self.browser,SIGNAL('mouseRelease()'),self.mouseReleaseEvent)
        QObject.connect(self.browser,SIGNAL('mouseMove(QMoveEvent)'),self.mouseMoveEvent)
        QObject.connect(self.browser,SIGNAL("loadFinished(bool)"),self.loadProgressEvent)
        QObject.connect(self.browser,SIGNAL("loadStarted()"),self.loadProgressEvent)
        QObject.connect(self.browser,SIGNAL("loadProgress(int )"),self.loadProgressEvent)
        self.browser.show()
        if url!=None:
            self.url=url
        app.exec_()

    def wait(self)->int:
        """
        Wait for the browser to completely go away
        """
        if self.thread is not None:
            self.thread.join()
        return 0

    #def resourceReceived(self,resource):
    #    print 'resource received: ' + resource.status + ' ' + resource.statusText + ' ' +    resource.contentType + ' ' + resource.url);

    def loadProgressEvent(self,event:typing.Union[None,int,bool]=None):
        """
        Notification callback for page loading
        """
        if event is None: # load started
            pass
        elif isinstance(event,int): # percent complete
            pass
        elif isinstance(event,bool): # completed (True=loaded)
            if event:
                print(self.url,'loaded')
            else:
                print(self.url,'failed')
                self.html=f'Unable to load: {self.url}'
        else:
            raise Exception()

    def mousePressEvent(self,event:QMouseEvent):
        """
        Callback for a mouse down event
        """
        self.mpos=event.pos()
        print("MOUSE PRESS",self.mpos)

    def mouseReleaseEvent(self,event:QMouseEvent):
        """
        Callback for a mouse up event
        """
        self.mpos=None

    def mouseMoveEvent(self,event:QMouseEvent):
        """
        Callback for a mouse movement event
        """
        if self.mpos!=None and event.buttons()&Qt.LeftButton>0:
            diff=QPoint(event.pos()-self.mpos)
            newpos=QPos(self.browser.pos()+diff)
            self.browser.move(newpos)
        print("MOUSE MOVE",self.mpos)

    def __del__(self):
        """
        Clean stuff up on object delete
        """
        pass#self.close()

    def runJS(self,js:str)->None:
        """
        Execute some javascript code
        """
        #self.url='javascript:'+urllib.quote(js+'\n;void(0);')
        self.browser.page().mainFrame().evaluateJavaScript(js)

    @property
    def html(self)->str:
        """
        get/set the current html
        """
        raise NotImplementedError()
    @html.setter
    def html(self,html:str)->None:
        """
        get/set the current html
        """
        self.browser.setHtml(html)

    @property
    def url(self)->Url:
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
        self.browser.load(QUrl(self._url))

    def click(self,x:int,y:int,button:int)->None:
        """
        Callback for a mouse click event
        """
        pos=(x,y)
        eventType=_
        evt=QMouseEvent(eventType,pos,QtCore.Qt.MiddleButton,event.buttons(),event.modifiers())
        self.app.sendEvent(self.app,evt)

    def close(self)->None:
        """
        close this browser
        """
        raise NotImplementedError() # TODO: implement quit

    def getScreenshot(self)->Image.Image:
        """
        return a screenshot as a pil image

        See also http://www.alexezell.com/code/webkit2png.txt
        """
        image=QImage(self._page.viewportSize(),QImage.Format_ARGB32)
        painter=QPainter(image)
        self._page.mainFrame().render(painter)
        painter.end()
        return image
