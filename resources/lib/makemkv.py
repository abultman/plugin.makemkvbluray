import subprocess, settings, brlog, tempfile, os, threading, xbmcgui, urllib, re, xbmc
from functools import partial

def killMkvOnPlaybackEnd(pid):
    dialog = xbmcgui.Dialog() #@UndefinedVariable
    dialog.ok("playback ended, about to kill %d"%(pid))


class MakeMkvInteraction:
    def __init__(self):
        self.settings = settings.BluRaySettings()
        self.progress = ProgressInfo()
        self.progress.start()
        self.log = brlog.BrLog('makemkvinteraction')
    
    def discList(self):
        # First stop any old one
        self.killMkv()
        tmpf = tempfile.NamedTemporaryFile(delete=True)
        progressFile = self.progress.startProgress()
        sp = os.system(r'%s -r --cache=1 --progress=%s --messages=%s info disc:10' %(self.settings.mkvLocation, progressFile, tmpf.name))

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
        # progressFile = self.progress.startProgress(times = 2)
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
            dialog = xbmcgui.Dialog() #@UndefinedVariable
            dialog.ok("Info", _(50073))
            return False
            
        return self.__runandregistershutdown('"%s" -r --cache=128 stream \'%s:%s\'' %(self.settings.mkvLocation, type, choice))
        

    def __runandregistershutdown(self, mkvStart):
        result = self.__runmkvstream(mkvStart)
        if result >= 0:
            xbmc.Player().onPlayBackStopped(partial(killMkvOnPlaybackEnd, result))
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
        self.log.info('attempting linux kill of makemkvcon') #@UndefinedVariable
        subprocess.call('killall -9 makemkvcon', shell=True)
        self.log.info('Linux call successful') #@UndefinedVariable
      except:
        pass

      #Windows.
      try :
        self.log.info('attempting windows kill of makemkvcon') #@UndefinedVariable
        subprocess.call('taskkill /F /IM makemkvcon.exe', shell=True)
        self.log.info('Windows call successful') #@UndefinedVariable
      except:
        pass
        

class ProgressInfo(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.progressFile = None
        self.showing = False
        self.dialog = None
    
    def run(self):
        while True:
            if self.showing:
                busy = True
                maxprg = 1000
                current = 0
        
                while self.showing:
                    line = self.progressFile.readline()
                    if line.startswith('PRGV:'):
                        progress = line[4:].split(',')
                        maxprg = int(progress[2])
                        current= int(progress[1])
                        self.dialog.update(int(float(current) / float(maxprg) * 1000.0) )
                        if current >= maxprg:
                            self.times = self.times - 1
                    
                        if self.times == 0:
                            self.dialog.close()
                            self.showing = False

    def startProgress(self, times = 1):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('XBMC', '', '')
        self.progressFile = tempfile.NamedTemporaryFile()
        self.times = times
        self.showing = True
        return self.progressFile.name

