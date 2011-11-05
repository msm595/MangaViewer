#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from mangaviewer import EventEmitter
import json, codecs, os, Image, ImageTk, math



"""
Settings class

Deals with the settings of the app, and also loading and setting the settings.

"""
class Settings:
    def __init__(self):
        self.settingsFile = u'settings.json'

        self.settings = {
            'currentDir': u'./',
            'fit': 'both', #both, x, y, neither
            'rgbResize': 'bicubic', #nearest, bilinear, bicubic, antialias, nearanti, cubanti, linanti
            'grayResize': 'antialias' #nearest, bilinear, bicubic, antialias
        }

        self.loadSettings()

    def loadSettings(self):
        if os.path.exists(self.settingsFile):
            sFile = codecs.open(self.settingsFile, encoding="utf-8", mode="r")
            tSettings = json.load(sFile, encoding='utf-8')
            sFile.close()

            for k in tSettings:
                if k in self.settings:
                    self.settings[k] = tSettings[k]

            if not os.path.exists(self.settings['currentDir']):
                self.settings['currentDir'] = u'./'
        else:
            self.saveSettings()

    def saveSettings(self):
        sFile = codecs.open(self.settingsFile, encoding="utf-8", mode="w")
        json.dump(self.settings, sFile, encoding="utf-8", indent=4)
        sFile.close()

_s = Settings()



"""
Model class

Handles data of the app.

"""
class Model(EventEmitter):
    def __init__(self):
        EventEmitter.__init__(self)

        self.images = []
        self.current = 0
        self.supported = ['png', 'gif', 'jpg', 'jpeg']

        self.imageSize = (0,0)

        self._s = _s # TODO: replace all self._s with _s
        self.updateFileList()

    def absPath(self, file):
        return os.path.join(self._s.settings['currentDir'], file)

    def getCurrentDir(self):
        return self._s.settings['currentDir']

    def setCurrentDir(self, dir):
        if not isinstance(dir, unicode):
            dir = unicode(dir)
        
        if dir != self.getCurrentDir():
            if len(self.images) > 0:
                self.images[self.current].unload()

            self._s.settings['currentDir'] = dir
            self._s.saveSettings()
            self.emit("currentDirChanged", dir)
            self.updateFileList()
            return True
        else:
            return False

    def updateFileList(self):
        dirList = os.listdir(self._s.settings['currentDir'])
        self.images = []

        for fname in dirList:
            ext = os.path.splitext(fname)[1].lower()[1:]
            try:
                self.supported.index(ext)
                self.images.append(Img(self.absPath(fname)))
                self.current = 0
            except:
                pass #isn't in the filter

    def hasFirstImage(self):
        return self.hasNumImage(0)
    
    def getFirstImage(self):
        self.getNumImage(0)
    
    def hasLastImage(self):
        return self.hasNumImage(len(self.images)-1)
    
    def getLastImage(self):
        self.getNumImage(len(self.images)-1)

    def hasNextImage(self):
        return self.hasNumImage(self.current+1)
    
    def getNextImage(self):
        self.getNumImage(self.current+1)
    
    def hasPrevImage(self):
        return self.hasNumImage(self.current-1)

    def getPrevImage(self):
        self.getNumImage(self.current-1)

    def hasCurrentImage(self):
        return len(self.images) > 0

    def getCurrentImage(self):
        self.getNumImage(self.current)

    def returnCurrentImage(self):
        return self.images[self.current]

    def hasNumImage(self, num):
        return num < len(self.images) and num >= 0
    
    def getNumImage(self, num):
        if self.hasCurrentImage():
            self.returnCurrentImage().unload()
        self.current = num
        self.returnCurrentImage().resizeTo(self.imageSize)
        self.emit("currentImageChanged", self.returnCurrentImage(), self.current, len(self.images))
        
    def setImageSize(self, size):
        self.imageSize = size


"""
Img Class

Stores path to img and manipulates (resizes).

"""
class Img:
    def __init__(self, path):
        self.path = path
        self.size = 0,0
        self.oSize = 0,0
        self.img = None
        self.tkpi = None

        split = os.path.split(self.path)
        self.folderName = os.path.split(split[0])[1]
        self.fileName = split[1]

    def stats(self):
        #self.img = Image.open(self.path)
        self.size = self.img.size
        self.oSize = self.img.size

    def load(self):
        self.img = Image.open(self.path)#.convert("RGB") #RGB for better resizing
        if self.oSize[0] == 0 or self.oSize[1] == 0:
            self.stats();
        #print self.img.mode
        if self.img.mode == "P":
            self.img = self.img.convert("L") #L scales much more nicely than P

    def unload(self):
        self.img = None
        self.tkpi = None
        self.size = self.oSize

    def fit(self, size):
        wRatio = 1.0 * size[0] / self.oSize[0]
        hRatio = 1.0 * size[1] / self.oSize[1]
        ratio = 1.0

        if _s.settings['fit'] == "both":
            ratio = min(wRatio, hRatio)
        elif _s.settings['fit'] == "x":
            ratio = wRatio
        elif _s.settings['fit'] == "y":
            ratio = hRatio

        ratio = min(ratio, 1.0)
        self.size = (int(self.oSize[0] * ratio), int(self.oSize[1] * ratio))
        return ratio

    def getResizeMethod(self):
        if self.img.mode == "L" or self.img.mode == "1": #grayscale
            prefix = "gray"
        else:
            prefix = "rgb"
        
        s = prefix + "Resize"

        resize = Image.ANTIALIAS

        if _s.settings[s] == "nearest":
            resize = Image.NEAREST

        elif _s.settings[s] == "bicubic":
            resize = Image.BICUBIC

        elif _s.settings[s] == "bilinear":
            resize = Image.BILINEAR

        elif _s.settings[s] == "cubanti":
            resize = "cubanti"

        elif _s.settings[s] == "linanti":
            resize = "linanti"

        elif _s.settings[s] == "nearanti":
            resize = "nearanti"
        
        return resize

    def stepanti(self,before,ratio,to):
        '''Resizes the image in a step. First do one method, then do antialias resize.'''
        hRatio = math.sqrt(ratio)
        hRatio = hRatio * math.sqrt(hRatio)
        hRatio = hRatio * math.sqrt(hRatio)
        if before == "nearanti":
            resize = Image.NEAREST
        elif before == "cubanti":
            resize = Image.BICUBIC
        else:
            resize = Image.BILINEAR

        self.size = (int(self.oSize[0] * hRatio), int(self.oSize[1] * hRatio))
        self.img = self.img.resize(self.size, resize)

        self.fit(to)

        return self.img.resize(self.size, Image.ANTIALIAS)

    def resizeTo(self, size):
        self.load()
        #start = time.clock()
        ratio = self.fit(size)
        if ratio == 1:
            self.tkpi = ImageTk.PhotoImage(self.img)
            return self.tkpi

        resize = self.getResizeMethod()

        if resize == "linanti" or resize == "cubanti" or resize == "nearanti":
            self.img = self.stepanti(resize, ratio, self.size)
        else: 
            self.img = self.img.resize(self.size, resize)
        
        #end = time.clock()
        #print "Resized using " + str(resize)
        #print "Took " + str(end-start)

        self.tkpi = ImageTk.PhotoImage(self.img)
        return self.tkpi

    # def quickResizeTo(self, size):
    #     if self.img == None:
    #         self.load()
    #     self.fit(size)
    #     self.img = self.img.resize(self.size)
    #     self.tkpi = ImageTk.PhotoImage(self.img)
    #     return self.tkpi