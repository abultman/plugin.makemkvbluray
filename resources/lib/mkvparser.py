import urllib, re, elementtree.ElementTree as ET

class BrowseHandler:
  def __init__(self) :
    self.catchCharData = False
    self.keyColumn = False
    self.map = {}
    self.lastKey = ''
    self.lastVal = ''
    self.titleMap = {}
  
  def start(self, url, title = 'none'):
    # Initialize all locals
    self.catchCharData = False
    self.keyColumn = False
    self.map[url] = {}
    self.currMap = self.map[url]
    self.lastKey = ''
    self.lastVal = ''
    filename, headers = urllib.urlretrieve(url)
    del headers

    XML = ET.parse(filename)
    elems = XML.getiterator(tag='{http://www.w3.org/1999/xhtml}td')
    for each in elems:
      self.keyColumn = not self.keyColumn
      if self.keyColumn:
        self.lastKey = each.text
      else:
        txt = ''
        # Check for href:
        refs = each.getiterator(tag='{http://www.w3.org/1999/xhtml}a')
        for ref in refs:
          txt = ref.get('href')

        if txt == '' :
          txt = each.text

        self.currMap[self.lastKey] = txt

    # Now do some processing:
    for k, v in self.map[url].iteritems() :
      if k == 'titles':
        # go straight ahead and parse some more:
        self.start(v)
      if re.search('title\d+', k) :
        self.titleMap[k] = {}
        self.start(v, k)
      if title != 'none':
        if k == 'duration':
          self.titleMap[title]['duration'] = v
        elif k == 'file0':
          self.titleMap[title]['file'] = v
        elif k == 'chaptercount':
          self.titleMap[title]['chaptercount'] = v

