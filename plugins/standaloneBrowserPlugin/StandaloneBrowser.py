#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A full-fledged standalone browser application.

There may be many different kinds on an os.  This
should locate and represent any of the major ones.
"""
import typing
import os
import signal
import time
from subprocess import Popen,PIPE
import urllib
from paths import FilePath,Url,UrlCompatible,asUrl,urlencode
from browsers import Browser,Browsers


HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep

def getOpenerCommandForFile(
    filename:UrlCompatible,
    operation:str='open',
    w:typing.Optional[int]=None,
    h:typing.Optional[int]=None
    )->typing.Optional[str]:
    """
    Returns the command line for opening a given file
    (currently only supports Windows)
    """
    filename=asUrl(filename)
    if filename.scheme!='file':
        return None
    key='.'+filename.ext
    reg_query="reg query HKCR\\"+key
    #print reg_query
    po=Popen(reg_query,stdout=PIPE,encoding='utf-8')
    text=po.communicate()[0].split("\n")
    for line in text:
        line=line.lstrip()
        if line and (line[0]=='<' or line[0]=='('):
            key=line.split()[2]
            break
    #print key
    reg_query="reg query HKCR\\"+key+"\\shell\\"+operation+"\\command"
    #print reg_query
    po=Popen(reg_query,stdout=PIPE,encoding='utf-8')
    text=po.communicate()[0].split("\n")
    command=None
    for line in text:
        line=line.lstrip()
        if line and (line[0]=='<' or line[0]=='('):
            command=' '.join(line.split()[2:])
            break
    if command is None:
        return command
    params=''
    if command.find('firefox')>=0:
        profile=HERE+'firefox_profile'
        # trick firefox into opening a new window/process
        params='-no-remote -profile "'+profile+'"'
        #params='-new-window'
        if w is not None:
            params=params+' -width '+str(w)
        if h is not None:
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
    if command.find('%1')<1:
        return f'{command} {filename}'
    return command.replace('%1',str(filename))


def setTransparency(hwnd:int,amount:int)->None:
    """
    This is how the method SetTransparent() is implemented
     on all MS Windows platforms.
    """
    try:
        import ctypes
        _winlib=ctypes.windll.user32
        style=_winlib.GetWindowLongA(hwnd,0xffffffec)
        style|=0x00080000
        _winlib.SetWindowLongA(hwnd,0xffffffec,style)
        _winlib.SetLayeredWindowAttributes(hwnd,0,amount,2)
    except ImportError:
        import win32api
        import win32con
        import winxpgui
        _winlib=win32api.LoadLibrary("user32") # type: ignore
        pSetLayeredWindowAttributes=win32api.GetProcAddress( # type: ignore
            _winlib,"SetLayeredWindowAttributes") # type: ignore
        if pSetLayeredWindowAttributes is None:
            return
        exstyle=win32api.GetWindowLong(hwnd,win32con.GWL_EXSTYLE)
        if (exstyle&0x80000)==0:
            win32api.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,exstyle|0x80000)
        winxpgui.SetLayeredWindowAttributes(hwnd,0,amount,2) # pylint: disable=no-member # type: ignore # noqa: E501


def enquote(path:str)->str:
    """
    enclose a windows path in quotes if necessary
    """
    if path.find(' ')>=0:
        return '"'+path+'"'
    return path


def filenameToFamily(name:str)->str:
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


def _which(appNames:typing.Iterable[str])->typing.Iterable[FilePath]:
    """
    find the full path of applications using the linux 'which' command
    """
    import subprocess
    for appName in appNames:
        cmd='which '+appName
        try:
            path=subprocess.check_output(cmd,shell=True).decode().strip()
            if path:
                yield FilePath(path)
        except subprocess.CalledProcessError:
            pass


def findChrome()->typing.Iterable[FilePath]:
    """
    find installed versions of google chrome

    returns []
    """
    if os.name=='nt':
        found:typing.Set[FilePath]=set()
        localAppdataDir=FilePath(os.environ['LOCALAPPDATA']).absolute()
        app=localAppdataDir/'Google'/'Chrome'/'Application'/'chrome.exe'
        if app.exists():
            found.add(app)
            yield app
        for pf in (r'C:\Program Files',r'C:\Program Files (x86)'):
            chrome=FilePath(pf)/'Google'/'Chrome'/'Application'/'chrome.exe'
            if chrome.exists() and chrome not in found:
                found.add(chrome)
                yield chrome
        # TODO: search registry HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\Application  # noqa: E501
        for pf in (r'C:\Program Files',r'C:\Program Files (x86)'):
            edge=FilePath(pf)/'Microsoft'/'Edge'/'Application'/'msedge.exe'
            if edge.exists() and edge not in found:
                found.add(edge)
                yield edge
    else:
        yield from _which(('chromium','chrome','safari'))


def findFirefox()->typing.Iterable[FilePath]:
    """
    Find firefox and variants

    returns []
    """
    if os.name=='nt':
        found:typing.Set[FilePath]=set()
        programFilesDirs=(
            FilePath(r'C:\Program Files'),
            FilePath(r'C:\Program Files (x86)'))
        for pf in programFilesDirs:
            test=pf/'BraveSoftware'/'Brave-Browser'/'Application'/'brave.exe'
            if test.exists():
                found.add(test)
                yield test
            test=pf/'Palemoon'/'palemoon.exe'
            if test.exists():
                found.add(test)
                yield test
            test=pf/'Mozilla Firefox/firefox.exe'
            if test.exists():
                found.add(test)
                yield test
        # TODO: check HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox\*\Main\PathToExe  # noqa: E501
    else:
        yield from _which(('brave','palemoon','firefox'))


def findIexplore()->typing.Iterable[FilePath]:
    """
    find installed internet explorer.
    (As if you would want to do that...)
    """
    if os.name=='nt':
        found:typing.Set[FilePath]=set()
        for pf in [r'C:\Program Files',r'C:\Program Files (x86)']:
            test=FilePath(pf)/'internet Explorer'/'iexplore.exe'
            if test.exists():
                found.add(test)
                yield test
        # check HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Capabilities/ApplicationDescription # noqa: E501
        # NOTE: this is a string in the exe's stringtable, so rsplit(',',1)[0])


def findDefault()->typing.Optional[typing.Tuple[str,str]]:
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


def findAll()->typing.Iterable[typing.Tuple[str,FilePath]]:
    """
    Find all browsers on the system

    returns [(family,app)]
    """
    # keyed by lowercase path because FilePath equality is broken in paths
    ret:typing.Dict[str,typing.Tuple[str,FilePath]]={}
    for app in findChrome():
        ret[str(app).lower()]=('webkit',app)
    for app in findFirefox():
        ret[str(app).lower()]=('mozilla',app)
    for app in findIexplore():
        ret[str(app).lower()]=('ie',app)
    default=findDefault()
    if default is not None:
        family,app=default
        app=FilePath(app.strip('"'))
        ret[str(app).lower()]=(family,app)
    return ret.values()


def embedSysWindow(putThisWindow:int,intoThisWindow:int)->bool:
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
    style=win32gui.GetWindowLong(childHwnd,win32con.GWL_STYLE)  # type: ignore
    style &= ~(win32con.WS_POPUP) # type: ignore
    style |= win32con.WS_CHILD # type: ignore
    win32gui.SetWindowLong(childHwnd,win32con.GWL_STYLE,style) # type: ignore
    # set it
    win32gui.SetParent(childHwnd,parentHwnd)
    # make sure it behaves properly
    #;;win32gui.AttachThreadInput(childHwnd,parentHwnd)
    return True

class classproperty(property):
    """
    combine both @classmethod and @property
    """
    def __get__(self, # type: ignore
        cls:typing.Type[typing.Any],owner:typing.Any)->typing.Any:
        return classmethod(self.fget).__get__(None,owner)() # type: ignore


class StandaloneBrowser(Browser):
    """
    A full-fledged standalone browser application.

    There may be many different kinds on an os.  This
    should represent any of the major ones.
    """
    canRunJS=True
    family='other'
    app:typing.Optional[str]=None

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
        self._url:typing.Optional[Url]=None
        self.browser:typing.Optional["Popen[bytes]"]=None
        if self.app is None:
            raise RuntimeError('No browser application associated with this class')  # noqa: E501
        cmd=[self.app]
        if url is not None:
            self._url=Url(url)
            cmd.append(str(self._url))
        self.browser=Popen(cmd)

    @classmethod
    def isAvailable(cls)->bool:
        """
        Determine if this browser application is available on the system.
        """
        return cls.app is not None

    @classmethod
    def variants(cls)->typing.Iterable[typing.Type[Browser]]:
        """
        One browser class for each browser application found on the system
        """
        if cls.app is not None:
            yield cls
            return
        yield from Browsers().all

    def __del__(self):
        """
        Clean stuff up on object delete
        """
        self.close()

    def runJS(self,js:str)->None:
        """
        Execute some javascript code
        """
        self.url='javascript:'+urlencode(js+'\n;void(0);')

    @property
    def url(self)->typing.Optional[Url]:
        """
        get/set the current url
        """
        return self._url
    @url.setter
    def url(self,url:typing.Optional[UrlCompatible])->None:
        """
        get/set the current url
        """
        self._url=Url(url)
        raise NotImplementedError() # TODO: Can I do this somehow??

    @classproperty
    def name(cls:StandaloneBrowser)->str: # pylint: disable=no-self-argument
        """
        determine and return the name of the browser application

        Developers take note:  This uses class-generator trickery
        which will be sure to cause all kinds of pylint errors.
        """
        cmd=str(cls.app)
        if cmd[0]=='"':
            cmd=cmd.split('"',2)[1]
        else:
            cmd=cmd.split(' ',1)[0]
        cmd=cmd.rsplit(os.sep,1)[-1].split('.',1)[0].lower()
        return 'standalone '+cmd

    def close(self)->None:
        """
        close this browser
        """
        result:typing.Optional[bytes]=None
        if self.browser is not None:
            try:
                # windows kill process (either way works)
                import win32api
                if False:
                    # use the api
                    PROCESS_TERMINATE = 1
                    handle=win32api.OpenProcess(
                        PROCESS_TERMINATE,False,self.browser.pid)
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
                while self.browser is not None and self.browser.poll()<0: # type: ignore
                    time.sleep(0.1)
                    waitcycles=waitcycles-1
                    if waitcycles<=0:
                        os.kill(self.browser.pid,-9)
                    self.browser.poll()
                    break
        self.browser=None
        _=result # return result

    def wait(self,timeoutSec:float=0.5)->int:
        """
        Wait for the browser to close and return the exit code.

        timeoutSec: the maximum time to wait for the browser to close
            in seconds.
        """
        result:int=-1
        if self.browser is not None:
            result=self.browser.wait(timeoutSec)
        print('*** browser process completed')
        return result


def _generateBrowserClasses()->typing.List[typing.Type[StandaloneBrowser]]:
    """
    Create a StandaloneBrowser subclass for every browser found by findAll(),
    and add each one to this module's namespace.
    """
    classes:typing.List[typing.Type[StandaloneBrowser]]=[]
    for family,app in findAll():
        appName=str(app).rsplit(os.sep,1)[-1].split('.',1)[0].lower()
        className=f'Standalone{appName.capitalize()}Browser'
        i=2
        while className in globals():
            className=f'Standalone{appName.capitalize()}Browser{i}'
            i+=1
        cls=type(className,(StandaloneBrowser,),{
            'name':'standalone '+appName,
            'family':family,
            'app':str(app),
            '__module__':__name__})
        globals()[className]=cls
        Browsers.registerBrowser(cls)
        classes.append(cls)
    return classes


for browserClass in _generateBrowserClasses():
    __dict__[browserClass.__name__]=browserClass
