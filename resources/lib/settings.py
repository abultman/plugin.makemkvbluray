import xbmcplugin, xbmcaddon
import sys
import urllib
import brlog

__scriptID__   = sys.modules[ "__main__" ].__scriptID__


class BluRaySettings:
  def __init__(self):
    addon = xbmcaddon.Addon(__scriptID__)
    self.log = brlog.BrLog('settings')
    self.log.info('reading settings') 

    params = self.getParams()
    if len(sys.argv) >= 2:
        self.handle = int(sys.argv[1])
    self.paramUrl = self.getParam(params, 'url')
    self.paramName = self.getParam(params, "name")
    self.paramMode = self.getIntParam(params, "mode")
    self.autoPlay = self.getBoolParam(params, "autoplay")
    self.disc = self.getParam(params, "disc")
    self.local = True
    self.portNumber = addon.getSetting('port_number') 
    self.ipAddress = '127.0.0.1'

    self.mkvLocation = addon.getSetting('mkvlocation') 
    self.rootURL = 'http://%s:%s/' % (self.ipAddress, self.portNumber)
    self.waitTimeOut = int(addon.getSetting('wait_timeout')) 
    
    # Sections:
    self.enableDisc = addon.getSetting('support_disc') == "true" 
    self.enableFile = addon.getSetting('support_fileselect') == "true" 

  def getParam(self, params, name):
    try:
      result = params[name]
      result = urllib.unquote_plus(result)
      return result
    except:
      return None

  def getIntParam (self, params, name):
    try:
      param = self.getParam(params,name)
      self.log.debug(name + ' = ' + param)
      return int(param)
    except:
      return None
    
  def getBoolParam (self, params, name):
    try:
      param = self.getParam(params,name)
      self.log.debug(name + ' = ' + param)
      return 'True' == param
    except:
      return None
    
  def getParams(self):
    try:
        param=[]
        paramstring=sys.argv[2]
        self.log.info('raw param string: ' + paramstring)
        if len(paramstring)>=2:
          params=sys.argv[2]
          cleanedparams=params.replace('?','')
          if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
          pairsofparams=cleanedparams.split('&')
          param={}
          for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
              param[splitparams[0]]=splitparams[1]
        return param
    except:
        return []

  def showSettings(self):
    xbmcaddon.Addon(__scriptID__).openSettings(sys.argv[ 0 ])  
