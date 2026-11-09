#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
The base class of what a browser looks like and what it can do.
"""
import typing
from paths import UrlCompatible,Url
from pluginTools import Plugin
if typing.TYPE_CHECKING:
    from PIL import Image

TypeOfBrowser=typing.Type["Browser"]


class Browser(Plugin):
    """
    The base class of what a browser looks like and what it can do.

    This is also the base class for all browsers plugins.
    To register one, add to your pyproject.toml:
        [project.entry-points."browsers.plugin"]
        myBrowser='myPackage:MyBrowser'
    """

    canRunJS=False # can run javascript code we send it
    canDoFullscreen=False # browser can go fullscreen (useful for screensavers and such) # noqa: E501 # pylint: disable line-too-long
    canSetHtml=False # you can set the html contents
    canDoHeadless=False # can be run hidden (for rendering a webpage to get data, yet without showing the user anything) # noqa: E501 # pylint: disable line-too-long
    canDoMouse=False # can simulate mouse events
    canDoKeyboard=False # can simulate keyboard events
    canEditDom=False # you can edit the html (your application should use canRunJS as a fallback) # noqa: E501 # pylint: disable line-too-long
    canGetScreenshot=False # you can get a screenshot image
    canDoTransparent=False # can be floating/transparent
    canEmbed=False # able to be embedded in a system window

    name=''
    family='other'

    def __init__(self,
        url:typing.Optional[UrlCompatible]=None,
        w:int=800,h:int=600,
        title:str="",
        fullscreen:bool=False,
        headless:bool=False,
        transparent:bool=False,
        embedIn:typing.Optional[typing.Any]=None):
        pass

    @classmethod
    def isAvailable(cls)->bool:
        """
        Can this browser be used on this system?
        """
        return True

    @classmethod
    def variants(cls)->typing.Iterable[typing.Type["Browser"]]:
        """
        The usable browser classes this plugin provides.

        Override if one plugin represents several browsers.
        """
        if cls.isAvailable():
            yield cls

    def runJS(self,js:str)->None:
        """
        Execute some javascript code
        """
        raise NotImplementedError()

    @property
    def url(self)->Url:
        """
        get/set the current url
        """
        raise NotImplementedError()
    @url.setter
    def url(self,url:UrlCompatible)->None:
        """
        get/set the current url
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    @property
    def text(self)->str:
        """
        get/set the current html via converting plain text
        """
        # TODO: default this to html() and text-to-html conversion
        raise NotImplementedError()
    @text.setter
    def text(self,text:str)->None:
        """
        get/set the current html via converting plain text
        """
        # TODO: default this to html-to-text conversion and setHtml()
        raise NotImplementedError()

    def close(self)->None:
        """
        close this browser
        """
        raise NotImplementedError()

    def wait(self)->int:
        """
        Wait for the browser to close and return the exit code
        """
        raise NotImplementedError()

    def getScreenshot(self)->'Image.Image':
        """
        return a screenshot as a pil image
        """
        raise NotImplementedError()

    def __repr__(self)->str:
        """
        return a string representation of this browser
        """
        return self.name
