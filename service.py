import xbmc, xbmcgui, subprocess, os, sys, urllib, re
import xbmcplugin, xbmcaddon


__scriptID__      = "plugin.makemkvbluray"
__addon__ = xbmcaddon.Addon(__scriptID__)

# Shared resources
BASE_RESOURCE_PATH = os.path.join( __addon__.getAddonInfo('path'), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import makemkv

__language__ = __addon__.getLocalizedString
_ = sys.modules[ "__main__" ].__language__

import settings, file, mkvparser, brlog, makemkv

_log = brlog.BrLog('tracker service')

_log.info('Starting the BluRay tracker service') 

class MyPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)
        self.makemkv = makemkv.MakeMkvInteraction()
    
    def onPlayBackStopped(self):
        _log.info('Playback stopped, trying to kill makemkv')
        self.makemkv.killMkv()

    def onPlayBackStarted(self):
        _log.info('Playback started')
        


myPlayer = MyPlayer()
xbmc.sleep(4)
if not makemkv.MakeMkvInteraction().makeMkvExists():
    imagePath =  os.path.join(__addon__.getAddonInfo('path'),'resources','images', 'alerticon.png')
    xbmc.executebuiltin('Notification("MakeMkv", "The MakeMKV bluray plugin cannot find MakeMkv. Please configure the plugin to point to it", "15000", "%s")' % (imagePath))

while (not xbmc.abortRequested):
    xbmc.sleep(4)
