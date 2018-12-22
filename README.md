# browsers

This is intended to be a python wrapper around common web browser controls.

The idea is you specify what features you need, e.g:
 * transparency
 * javascript
 * screenshots
 * ability to directly set html
 * etc...
 
And then it locates the best available browser for your needs and gives you back a controllable object.


Supported searching:
-------
* by specific browser name
* by browser family (aka engine)
* by feature, including:
  * canRunJS
  * canDoFullscreen (useful for things like screensavers)
  * canSetHtml
  * canDoHeadless
  * canDoMouse
  * canDoKeyboard
  * canEditDom
  * canGetScreenshot
  * canEmbed (as a control in another window)
  * canDoTransparent


Supported browsers:
-------
* Browsers with an ActiveX control (probably just InternetExplorer and Edge are that crazy)
* [wxWebView](https://docs.wxwidgets.org/trunk/classwx_web_view.html) Control
* [QTWebkit](https://pythonspot.com/pyqt5-webkit-browser/) Control
* [GTKWebkit](https://stackoverflow.com/questions/3949060/python-webkit-gtk-on-windows) Control
* [gtkmozembed](https://wiki.mozilla.org/Gtkmozembed) Control (Mozilla)
* full standalone browsers including:
  * firefox
  * palemoon
  * internet explorer
  * microsoft edge
  * google chrome
  * and will also try the "default browser" whatever that happens to be
  
Status:
-------

* wxWebView: doing great!
* Stand-alone browsers: works fine, at least on windows (though may never have as many features as embedded ones)
* Webkit GTK: Written but untested due to gtk install issues
* Webkit QT: Written but only marginally tested.  As an added bonus, should allow you to take screenshots.
* GTK Mozilla Embedded: Written but untested due to gtk install issues
* Registered ActiveX browser components: Seems to work but has a crash, so disabled.
* Supposedly there is a mozilla component called "HulaHop", but no web
		presence, so assumed to be abandoned??
  
  
