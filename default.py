import xbmc, xbmcgui, subprocess, os, time, sys, urllib, re
import xbmcplugin, xbmcaddon

  
__scriptname__ = "MakeMKV BluRay Watch Plugin"
__scriptID__      = "plugin.makemkvbluray"
__author__ = "Magnetism"
__url__ = "http://bultsblog.com/arne"
__credits__ = ""
__version__ = "0.1"
__addon__ = xbmcaddon.Addon(__scriptID__)

# Shared resources
BASE_RESOURCE_PATH = os.path.join( __addon__.getAddonInfo('path'), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = __addon__.getLocalizedString
_ = sys.modules[ "__main__" ].__language__

import settings, file, mkvparser, brlog, makemkv

_log = brlog.BrLog()

_log.info('Starting the BluRay script') 

class BluRayStarter:
  def __init__(self):
    _log.info('Staring') 
    self.settings = settings.BluRaySettings()
    self.makemkv = makemkv.MakeMkvInteraction()

  def killAndStart(self, mkvStart):
    if self.settings.local:
      _log.info('Running makemkvcon locally') 
      self.killMkv()
      # Determine if we're doing the disc or if we're browsing..
      _log.info(mkvStart) 
      return subprocess.Popen(mkvStart, shell=True)
    else:
      _log.info('connecting to remote stream, returning fake file browse class..') 
      return file.FakeFile()

  def killMkv(self):
    # Linux
    try :
      _log.info('attempting linux kill of makemkvcon') 
      subprocess.call('killall -9 makemkvcon', shell=True)
      _log.info('Linux call successful') 
    except:
      pass

    #Windows.
    try :
      _log.info('attempting windows kill of makemkvcon') 
      subprocess.call('taskkill /F /IM makemkvcon.exe', shell=True)
      _log.info('Windows call successful') 
    except:
      pass

  def browse(self, url) :
    _log.info('starting browser handler') 
    h = mkvparser.BrowseHandler()
    h.start(url)
    for k,v in h.titleMap.iteritems() : #@UnusedVariable
      self.addLink("%s %s, %s %s" %(_(50005), v['duration'], _(50006), v['chaptercount']),v['file'])


  def getMainFeatureTitle(self, url):
    h = mkvparser.BrowseHandler()
    h.start(url)
    # Play the longest feature on the disc:
    largest = 0
    largestTitle = ''
    for k,v in h.titleMap.iteritems() : #@UnusedVariable
      m = re.search('(\d+):(\d+):(\d+)', v['duration'])
      length = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
      if length > largest :
        largest = length
        largestTitle = v['file']
    _log.info('largest: %d, %s' %(largest,largestTitle))
    return largestTitle

  def handleListing(self):
    mode = self.settings.paramMode
    _log.info( 'mode: ' + str(mode))
    if mode ==None:
      _log.info('Showing categories')
      self.CATEGORIES()
      _log.info('Showing categories done')
      xbmcplugin.endOfDirectory(int(sys.argv[1]))
    if mode == 1 :
        _log.info( 'Entering Disc mode')
        self.process(self.makemkv.startStream(self.settings.disc))
    elif mode == 3 :
        _log.info( 'Entering Remote mode')
        mystarter = BluRayStarter()
        mystarter.process('')
    elif mode == 2:
      _log.info( 'Entering Browse mode')
      d = xbmcgui.Dialog() 
      choice = d.browse(1, 'Select folder', 'video', 'index.bdmv|.iso|.isoRenamedMeansSkip!|.MDS|.CUE|.CDI|.CCD', False, False, '')
      if choice <> '':
        self.process(self.makemkv.startFileStream(choice))
    
    if mode == 20:
      self.settings.showSettings()

  def process(self, ready):
    try :
      if ready:
        _log.info( 'Stream ready. ')
        # the Stream has started, start auto playback?
        if self.settings.autoPlay:
          _log.info( 'Autoplay selected')
          title = self.getMainFeatureTitle(self.settings.rootURL)
          _log.info( 'Main feature determined to be : ' + title)
          opener = urllib.URLopener()
          testfile = ''
          try:
            testfile = title
            opener.open(testfile)
          except IOError:
            testfile = ''

          del opener

          if testfile<>'':
              _log.info( 'Playing file ' + testfile)
              li = xbmcgui.ListItem(path = testfile)
              li.setProperty('IsPlayable', 'true')
              xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li) 
          else:
            self.message(_(50071))
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem()) 

        else:
          # Add the selections as selectable files.
          self.browse(self.settings.rootURL)
          xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    except :
        self.message(_(50072))
        self.pDialog.close()
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem()) 
        raise

  def CATEGORIES(self):
    # Disc
    if self.settings.enableDisc:
	  disclist = self.makemkv.discList()
	  for disc in disclist:
		self.addDir(_(50061) %(disc[0], disc[1]),1, True, disc[0], disc[1])
	  for disc in disclist:
		self.addDir(_(50062) %(disc[0], disc[1]),1, False, disc[0], disc[1])
    # Filelocation
    if self.settings.enableFile:
      self.addDir(_(50063),2, True)
      self.addDir(_(50064),2, False)
    self.addDir(_(50060),20, True, '0', 'settings', False)                     
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


  def addDir(self, name,mode, autoplay, disc = '0', disc_title ='idontknow', isPlayable = True):
    u=sys.argv[0]+"?mode="+str(mode)+"&autoplay="+urllib.quote_plus(str(autoplay)) + "&disc=" + disc
    _log.info(u)
    icon = "DefaultVideoPlaylists.png"
    if autoplay:
      icon= "DefaultVideo.png"
    liz=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage='')
    if autoplay and isPlayable:
      liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    _log.info(name)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder= not autoplay)
    
  
  def addLink(self, name,url):
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='') 
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty("IsPlayable" , "true")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz) 

  def message(self, messageText):
    dialog = xbmcgui.Dialog() 
    dialog.ok("Info", messageText)

_log.info("args")
for arg in sys.argv:
    _log.info(arg)
_log.info("done args")

mydisplay = BluRayStarter()
mydisplay.handleListing()
