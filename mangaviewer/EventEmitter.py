#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class EventEmitter():
    def __init__(self):
        self.__l = {} #listeners
        #self._max = 10 #max amt of listeners
        #self._i = 0 # num of listeners
        self.__debugMode = False
    

    def on(self, event, listener):
        self.addListener(event, listener)
        #return self #for chaining

    def addListener(self, event, listener):
        self.__debug("AddListener:", event, listener)
        if event not in self.__l:
            self.__l[event] = set()
        
        self.__l[event].add(listener)
        self.emit('newListener', listener)
        #self._i += 1

        #if self._i >= self._max:
        #    print "[WARNING] There are currently " + str(self._i) + " listeners"
    
    def once(self, event, listener):
        self.__debug("Once:",event, listener)
        self.addListener(event, self.__makeOnce(event, listener))
    
    def __makeOnce(self, event, listener):
        def callback(*args):
            self.removeListener(event, callback)
            listener(*args)
        return callback
    
    def removeListener(self, event, listener):
        self.__debug("Remove:",event, listener)
        if event not in self.__l:
            return
        if listener not in self.__l[event]:
            return
        self.__l[event].remove(listener)
        

    def removeAllListeners(self, event=None):
        if event == none:
            self.__l.clear()
            #self._i = 0
        elif event in self.__l:
            self.__l[event].clear()
            #self._i -= 1
    
    def listeners(self, event):
        if event in self.__l:
            return self.__l[event]
        return None
    
    def emit(self, event, *args):
        self.__debug("Emit:",event)
        if event in self.__l:
            copy = self.__l[event].copy()
            for listener in copy:
                listener(*args)
    
    def __debug(self, *s):
        if not self.__debugMode:
            return
        ss = ""
        for sss in s:
            ss = ss + " " + str(sss)
        print "[EventEmitter] " + ss
    
    def setDebug(self, d):
        self.__debugMode = d