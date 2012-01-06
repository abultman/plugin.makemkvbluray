import subprocess, settings, brlog, tempfile, os, threading, xbmcgui, urllib, re, xbmc, xbmcplugin
from functools import partial

class MakeMkvInteraction:
    def __init__(self):
        self.settings = settings.BluRaySettings()
        self.log = brlog.BrLog('makemkvinteraction')
    
    def discList(self):
        # First stop any old one
        self.killMkv()
        tmpf = tempfile.NamedTemporaryFile(delete=True)
        sp = os.system(r'%s -r --cache=1 --messages=%s info disc:10' %(self.settings.mkvLocation, tmpf.name))

        tmpf = open(tmpf.name)
        content = tmpf.read()
        tmpf.close()
        disclist = [x for x in content.splitlines() if x.startswith('DRV:')]
        readableDiscs = list()
        for item in disclist:
            info = [x.replace('"','') for x in item[4:].split(',')]
            if len(info[5]) > 0:
                readableDiscs.append( (info[0],info[5]))
        return readableDiscs

    def startStream(self, disc):
        self.log.info("Starting stream on disc %s with local url %s" %(disc, self.settings.rootURL))
        # Then fork the makemkv process
        return self.__runandregistershutdown('%s -r --cache=128 stream disc:%s' %(self.settings.mkvLocation, disc))

    def startFileStream(self, choice):
        type = ''
        if re.search("BDMV.index.bdmv", choice) :
            # Treat as file
            type = 'file'
            choice = choice[:-15]
        elif re.search("BDMV.MovieObject.bdmv", choice) :
            # Treat as file
            type = 'file'
            choice = choice[:-21]
        else:
            # Treat as iso
            type = 'iso'
        
        # Check if the file is reachable through the filesystem, to prevent errors with smb:// shares etc.
        if not os.path.exists(choice) :
            dialog = xbmcgui.Dialog() 
            dialog.ok("Info", _(50073))
            return False
        
        return self.__runandregistershutdown('"%s" -r --cache=128 stream \'%s:%s\'' %(self.settings.mkvLocation, type, choice))
        

    def __runandregistershutdown(self, mkvStart):
        result = self.__runmkvstream(mkvStart)
        if result >= 0:
            return True
        else:
            return False
        

    def __runmkvstream(self, mkvStart):
        self.log.info('Starting %s' %(mkvStart))
        # First stop any old one
        self.killMkv()
        timeSlept = 0
        proc = subprocess.Popen(mkvStart, shell=True)
        # Then wait for the stream to come up
        while True:   
          try:
            urllib.urlretrieve(self.settings.rootURL)
            return proc.pid
          except IOError:
            pass
          if proc.poll() :
            if proc.proc != 0 :
              self.message(_(50070))
              return -1
          xbmc.sleep(1000)
          timeSlept = timeSlept + 1
          if timeSlept > self.settings.waitTimeOut :
            return -1
        

    def killMkv(self):
      # Linux
      try :
        self.log.info('attempting linux kill of makemkvcon') 
        subprocess.call('killall -9 makemkvcon', shell=True)
        self.log.info('Linux call successful') 
      except:
        pass

      #Windows.
      try :
        self.log.info('attempting windows kill of makemkvcon') 
        subprocess.call('taskkill /F /IM makemkvcon.exe', shell=True)
        self.log.info('Windows call successful') 
      except:
        pass
    
    def makeMkvExists(self):
        (fin, fout) = os.popen4('%s -r' %(self.settings.mkvLocation))
        result = fout.read()
        self.log.info('Make mkv check returned %s' % (result.splitlines()[0]))
        if result.splitlines()[0].startswith('Use: makemkvcon [switches] Command [Parameters]'):
            self.log.info("MakeMkvCon found!")
            return True
        else:
            self.log.info('MakeMkvcon seems not to be configured properly : %s' %(self.settings.mkvLocation))
            return False
        
        