#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a replacement for the standard Python webbrowser module
(which, lets be honest, seems promising, but is neigh useless for anything).

Eventually goal is to let you perform standard browser functions on pretty much any
stand-alone or embedded browser.

 It is still in the process of being written, but current status is:
	* Stand-alone browsers: works fine on windows (though may never have as
		many features as embedded ones)
	* Webkit GTK: Written but untested
	* Webkit QT: Written but untested.  As an added bonus, should allow you
		to take screenshots.
	* GTK Mozilla Embedded: Written but untested
	* Registered ActiveX browser components: Not tested.
	* Supposedly there is a mozilla component called "HulaHop", but no web
		presence, so assumed to be abandoned.
"""
import os
from browser_interfaces._browser import BROWSER_LIST


class Browsers(object):
	"""
	A container class that allows searching of all browser implementaions
	currently available
	"""

	_all=None

	@property
	def all(self):
		"""
		A list of all available web browsers
		"""
		if self._all is None:
			# load all available browsers
			here=os.path.abspath(__file__).rsplit(os.sep,1)[0]
			if here.find('site-packages')>=0:
				here=here.rsplit(os.sep,1)[0]
			for inc in os.listdir(here+os.sep+'browser_interfaces'):
				if inc.endswith('.py') and inc[0]!='_':
					#last=len(BROWSER_LIST)
					#print 'Checking',inc,'...',
					exec('from browser_interfaces.'+inc[0:-3]+' import *')
					#if last==len(BROWSER_LIST):
					#	print 'NO'
					#else:
					#	print 'YES'
			self._all=BROWSER_LIST
		return self._all

	def _sort(self,browsers,preferences=None):
		"""
		sort a list of browsers in place, by preference

		preferences - [filter] (in order!) to sort all browsers in terms of preference

		filter - as used in preferences available filters are:
			familyName ('mozilla','webkit','ie')
			browserName ('chrome','firefox',etc)
			'canRunJS'
			'canDoFullscreen'
			'canSetHtml'
			'canDoHeadless'
			'canDoMouse'
			'canDoKeyboard'
			'canEditDom'
			'canGetScreenshot'
			'canEmbed'
			'canDoTransparent'

		NOTE: if you catch yourself doing _sort(self.all), you should probably
			be using get() instead!
		"""
		def _rank(browser):
			"""
			create a rank value for each available browser
			"""
			rank=0
			for pref in preferences:
				ipref=pref.lower()
				if ipref=='canrunjs':
					if browser.canRunJS:
						rank+=1
				elif ipref=='candofullscreen':
					if browser.canDoFullscreen:
						rank+=1
				elif ipref=='cansethtml':
					if browser.canSetHtml:
						rank+=1
				elif ipref=='candoheadless':
					if browser.canDoHeadless:
						rank+=1
				elif ipref=='candomouse':
					if browser.canDoMouse:
						rank+=1
				elif ipref=='candokeyboard':
					if browser.canDoKeyboard:
						rank+=1
				elif ipref=='caneditdom':
					if browser.canEditDom:
						rank+=1
				elif ipref=='cangetscreenshot':
					if browser.canGetScreenshot:
						rank+=1
				elif ipref=='canembed':
					if browser.canEmbed:
						rank+=1
				elif ipref=='candotransparent':
					if browser.canDoTransparent:
						rank+=1
				elif browser.name==pref or browser.family==ipref:
					rank+=1
				rank=rank<<1
		browsers.sort(key=_rank)

	def _filtered(self,browsers,requirements=None):
		"""
		create a filtered list of browsers by requirements

		requirements - [filter] filter out unsupported browsers

		filter - as used in requirements available filters are:
			familyName ('mozilla','webkit','ie')
			browserName ('chrome','firefox',etc)
			'canRunJS'
			'canDoFullscreen'
			'canSetHtml'
			'canDoHeadless'
			'canDoMouse'
			'canDoKeyboard'
			'canEditDom'
			'canGetScreenshot'
			'canEmbed'
			'canDoTransparent'

		NOTE: if you catch yourself doing _filtered(self.all), you should probably
			be using get() instead!
		"""
		ret=[]
		for browser in browsers:
			isOk=True
			for req in requirements:
				ireq=req.lower()
				if ireq=='canrunjs':
					if not browser.canRunJS:
						isOk=False
						break
				elif ireq=='candofullscreen':
					if not browser.canDoFullscreen:
						isOk=False
						break
				elif ireq=='cansethtml':
					if not browser.canSetHtml:
						isOk=False
						break
				elif ireq=='candoheadless':
					if not browser.canDoHeadless:
						isOk=False
						break
				elif ireq=='candomouse':
					if not browser.canDoMouse:
						isOk=False
						break
				elif ireq=='candokeyboard':
					if not browser.canDoKeyboard:
						isOk=False
						break
				elif ireq=='caneditdom':
					if not browser.canEditDom:
						isOk=False
						break
				elif ireq=='cangetscreenshot':
					if not browser.canGetScreenshot:
						isOk=False
						break
				elif ireq=='canembed':
					if not browser.canEmbed:
						isOk=False
						break
				elif ireq=='candotransparent':
					if not browser.canDoTransparent:
						isOk=False
						break
				elif browser.name!=req and browser.family!=ireq:
					isOk=False
					break
			if isOk:
				ret.append(browser)
		return ret

	def get(self,requirements=None,preferences=None):
		"""
		get available browsers with the desired features
		(default is to list everything)

		requirements - [filter] filter out unsupported browsers
		preferences - [filter] (in order!) to sort all browsers in terms of preference

		filter - as used in requirements or preferences available filters are:
			familyName ('mozilla','webkit','ie')
			browserName ('chrome','firefox',etc)
			'canRunJS'
			'canDoFullscreen'
			'canSetHtml'
			'canDoHeadless'
			'canDoMouse'
			'canDoKeyboard'
			'canEditDom'
			'canGetScreenshot'
			'canEmbed'
			'canDoTransparent'

		family is either 'webkit','mozilla','ie', or 'other'
		"""
		if requirements is not None and requirements:
			ret=self._filtered(self.all,requirements)
		else:
			ret=list(self.all)
		if preferences is not None and preferences:
			self._sort(preferences)
		return ret

	def create(self,url=None,w=800,h=600,title="",fullscreen=False,headless=False,
		transparent=False,embedIn=None,requirements=None,preferences=None):
		"""
		does a get(requirements,preferences)
		then creates the first browser in the list

		returns a browser object for you to enjoy
			(can return None, if there is no compatible browser available)
		"""
		if requirements is None:
			requirements=[]
		if preferences is None:
			preferences=[]
		if True: # can be disabled for testing new features
			if fullscreen and 'canDoFullscreen' not in requirements:
				requirements.append('canDoFullscreen')
			if headless and 'canDoHeadless' not in requirements:
				requirements.append('canDoHeadless')
			if transparent and 'canDoTransparent' not in requirements:
				requirements.append('canDoTransparent')
			if embedIn!=None and 'canEmbed' not in requirements:
				requirements.append('canEmbed')
		browsers=self.get(requirements,preferences)
		if len(browsers)<1:
			return None
		print 'Starting browser:',browsers[0].__class__.__name__,'-',browsers[0].name,'-',browsers[0].family
		return browsers[0](url,w,h,title,fullscreen,headless,transparent,embedIn)


if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		browsers=Browsers()
		w=800
		h=600
		title=""
		fullscreen=False
		headless=False
		transparent=False
		embedIn=None
		requirements=[]
		preferences=[]
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--list':
					for browser in browsers.get(requirements,preferences):
						print browser.name,'('+browser.family+')'
				elif arg[0]=='--create':
					url=None
					if len(arg)>1:
						url=arg[1]
					browser=browsers.create(url,w,h,title,fullscreen,headless,
						transparent,embedIn,requirements=requirements,
						preferences=preferences)
					if browser is None:
						print 'No browser matches given requirements!'
				elif arg[0]=='--requirements':
					requirements=[x.strip() for x in arg[1].replace("'",'').split(',')]
				elif arg[0]=='--preferences':
					preferences=[x.strip() for x in arg[1].replace("'",'').split(',')]
				elif arg[0]=='--w':
					if len(arg)>1:
						w=int(arg[1])
				elif arg[0]=='--h':
					if len(arg)>1:
						h=int(arg[1])
				elif arg[0]=='--title':
					if len(arg)>1:
						title=arg[1]
				elif arg[0]=='--fullscreen':
					if len(arg)>1:
						fullscreen=arg[1][0] in ['y','Y','1','t','T']
					else:
						fullscreen=True
				elif arg[0]=='--headless':
					if len(arg)>1:
						headless=arg[1][0] in ['y','Y','1','t','T']
					else:
						headless=True
				elif arg[0]=='--transparent':
					if len(arg)>1:
						transparent=arg[1][0] in ['y','Y','1','t','T']
					else:
						transparent=True
				elif arg[0]=='--embedIn':
					if len(arg)>1:
						embedIn=arg[1]
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  browsers.py [options]'
		print 'Options (evaluated IN ORDER!):'
		print '   --list ................... list all available browsers'
		print '   --create[=url] ........... create the best available browser'
		print '   --requirements=filters ... comma-separated list of filters to include (see below)'
		print '   --preferences=filters .... comma-separated list of preferences to order by (see below)'
		print '   --w=w .................... browser width (px)'
		print '   --h=h .................... browser height (px)'
		print '   --title=title ............ set the window title'
		print '   --fullscreen ............. make browser fullscreen'
		print '   --headless ............... make browser headless (not super useful at the moment)'
		print '   --transparent ............ make browser transparent'
		print '   --embedIn=hWnd ........... embed the browser in an existing system window'
		print 'Filters:'
		print "   familyName ('mozilla','webkit','ie')"
		print "   browserName ('chrome','firefox',etc)"
		print "   'canRunJS'"
		print "   'canDoFullscreen'"
		print "   'canSetHtml'"
		print "   'canDoHeadless'"
		print "   'canDoMouse'"
		print "   'canDoKeyboard'"
		print "   'canEditDom'"
		print "   'canGetScreenshot'"
		print "   'canEmbed'"
		print "   'canDoTransparent'"