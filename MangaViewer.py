#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Tkinter import *
from mangaviewer import Model, View, FolderDialog, Info


class Controller():
    def __init__(self, root):
        self._root = root;
        self._model = Model()
        self._view = View(self._root)
        self._folderDialog = None #FolderDialog(self.view, filter=self.model.supported)

        self._view.on("prevImage", self.prevImage)
        self._view.on("nextImage", self.nextImage)
        self._view.on("newDirectory", self.newDirectory)
        self._view.on("sizeChange", self.sizeChange)

        self._model.on("currentImageChanged", self._view.showImage)


        self._root.update()
        #self._model.setImageSize(self._view.getCanvasSize())
        self._root.mainloop()

    def prevImage(self):
        if self._model.hasPrevImage():
            self._model.getPrevImage()
        else:
            self.newDirectory()
    
    def nextImage(self):
        if self._model.hasNextImage():
            self._model.getNextImage()
        else:
            self.newDirectory()
    
    def newDirectory(self):
        if self._folderDialog == None:
            self._folderDialog = FolderDialog(self._root, self._model.getCurrentDir(), fileFilter=self._model.supported)
            self._folderDialog.on('folderSelected', self.setNewDirectory)
            self._folderDialog.on('canceled', self.folderCanceled)
        else:
            self._folderDialog.show()
    
    def folderCanceled(self):
        '''Wrapping. If on last image and dialog cancel -> first, if first -> last'''
        if not self._model.hasNextImage() and self._model.hasFirstImage():
            self._model.getFirstImage()
        elif not self._model.hasPrevImage() and self._model.hasLastImage():
            self._model.getLastImage()

    def sizeChange(self, size):
        self._model.setImageSize(size)
        if self._model.hasCurrentImage():
            self._model.getCurrentImage()

    def setNewDirectory(self, dir):
        if not self._model.setCurrentDir(dir):
            self.folderCanceled() #if the new folder == old one, returned false
        else:
            if self._model.hasCurrentImage():
                self._model.getCurrentImage()


if __name__ == "__main__":
    root = Tk()
    print Info.name + " " + Info.version
    Controller(root)