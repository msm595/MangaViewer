#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from mangaviewer import EventEmitter, Info
from Tkinter import *
from ttk import *
import os



"""
FolderDialog View Class

Dialog that asks the user to select a folder. Emit's 'folderSelected' when a folder is selected, 'canceled' when canceled

"""
class FolderDialog(EventEmitter, Toplevel):
    def __init__(self, parent, dir="./", fileFilter=None):
        EventEmitter.__init__(self)
        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title("Browse Folders")
        self.parent = parent
        self.dir = StringVar()
        self.fileFilter = fileFilter

        if os.path.exists(dir) and os.path.isdir(dir):
            self.dir.set(os.path.abspath(dir))
        else:
            self.dir.set(os.path.abspath("./"))

        self.body = Frame(self)
        self.body.grid(row=0,column=0,padx=5,pady=5, sticky=(N,S,E,W))

        Label(self.body, text="Please select a folder").grid(row=0,column=0, sticky=(N,S,W), pady=3)
        Label(self.body, text="You are in folder:").grid(row=1,column=0, sticky=(N,S,W))
        Entry(self.body, textvariable=self.dir, state="readonly").grid(row=2,column=0,sticky=(N,S,E,W),columnspan=2)
        self.treeview = Treeview(self.body, columns=("dir", "imgs"), show="headings")
        self.treeview.grid(row=3,column=0,sticky=(N,S,E,W),rowspan=3,pady=5,padx=(0,5))

        self.treeview.column("imgs", width=30, anchor=E)
        self.treeview.heading("dir", text="Select a Folder:", anchor=W)
        self.treeview.heading("imgs", text="Image Count", anchor=E)

        ok = Button(self.body, text="Use Folder")
        ok.grid(row=3,column=1,sticky=(N,E,W), pady=5)

        cancel = Button(self.body, text="Cancel")
        cancel.grid(row=4,column=1,sticky=(N,E,W), pady=5)        

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", self.cancel)
        cancel.bind("<Button-1>", self.cancel)
        ok.bind("<Button-1>", self.selectFolder)
        self.treeview.bind("<Left>", self.newFolder)
        self.treeview.bind("<Right>", self.newFolder)
        self.treeview.bind("<Return>", self.selectFolder)
        self.treeview.bind("<Up>", self.onUpDown)
        self.treeview.bind("<Down>", self.onUpDown)
        self.treeview.bind("<<TreeviewSelect>>", self.onChange)

        self.updateListing()
        self.resizable(0,0)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(5, weight=1)

        self.update()
        self.show()

    def newFolder(self, event):
        '''Called when user presses <Left> or <Right>, changes folder up or down.'''
        newDir = self.dir.get()
        if event.keysym == "Left":
            self.upFolder()
            return
        else:
            selected = self.getSelected()
            
            if selected == ".":
                #special super cool stuff here
                self.selectFolder()
                return
            elif selected == "..":
                self.upFolder()
                return
            else:
                newDir = os.path.join(newDir, selected)
        
        self.dir.set(os.path.abspath(newDir))
        self.updateListing()

    def upFolder(self):
        '''Moves up a directory in the FolderDialog.'''
        cur = os.path.split(self.dir.get())
        newDir = cur[0]
        cur = cur[1]

        self.dir.set(os.path.abspath(newDir))
        self.updateListing()

        children = self.treeview.get_children()
        for child in children:
            if self.treeview.item(child, "text") == cur:
                self.treeview.selection_set(child)
                self.treeview.focus(child)
                self.treeview.see(child)
                return

    def setFolder(self, dir):
        '''Explicitly sets the current directory of the FolderDialog.'''
        if os.path.exists(dir) and os.path.isdir(dir):
            self.dir.set(os.path.abspath(dir))
            self.updateListing()
    
    def onChange(self, event=None):
        '''Called when the selection changes, if the item count has not been computed, compute it.'''
        sel = self.treeview.focus()
        if sel == '':
            return #not possible, but just in case
        
        if self.treeview.item(sel, "values")[1] == "?":
            self.fileCount()
    
    def fileCount(self):
        '''Compute the file count for the selected item and set it.'''
        folder = os.path.join(self.dir.get(), self.getSelected())
        folder = os.path.abspath(folder)

        count = 0

        dirList = os.listdir(folder)
        for fname in dirList:
            if self.fileFilter == None:
                count = count + 1
            else:
                ext = os.path.splitext(fname)[1].lower()[1:]
                try:
                    self.fileFilter.index(ext)
                    count = count + 1
                except:
                    pass #isn't in the filter

        sel = self.treeview.focus()  
        newV = (self.treeview.item(sel, "values")[0], str(count))
        self.treeview.item(sel, value=newV)


    def onUpDown(self, event):
        '''Called on <Up> or <Down>, wrap around the selection top->bottom/bottom->top when applicable.'''
        sel = self.treeview.selection()
        if len(sel) == 0:
            return
        active = self.treeview.index(sel[0])
        children = self.treeview.get_children()
        length = len(children)
        toSelect = 0
        if event.keysym == "Up" and active == 0:
            toSelect = length - 1
        elif event.keysym == "Down" and active == length-1:
            toSelect = 0
        else:
            return
        
        toSelect = children[toSelect]
        self.treeview.selection_set(toSelect)
        self.treeview.focus(toSelect)
        self.treeview.see(toSelect)
        return 'break' #stop the event from bubbling (going to the default handler)


    def updateListing(self, event=None):
        '''Update the treeview with the current directory'''
        folder = self.dir.get()
        children = self.treeview.get_children()
        for child in children:
            self.treeview.delete(child)
        #self.treeview.set_children("", '')
        dirList = os.listdir(folder)

        first = self.treeview.insert("", END, text=".", values=("(.) - Current Folder", "?"))
        self.treeview.selection_set(first)
        self.treeview.focus(first)

        self.treeview.insert("", END, text="..", values=("(..)", "?"))
        #self.listbox.insert(END, "(.) - Current Folder")
        #self.listbox.insert(END, "(..)")
        for fname in dirList:
            if os.path.isdir(os.path.join(folder, fname)):
                #self.listbox.insert(END,fname+"/")
                self.treeview.insert("", END, values=(fname+"/", "?"), text=fname)
        self.treeview.update()

    def selectFolder(self, event=None):
        '''Get the abs path to the selected folder, emit "folderSelected" and hide self'''
        selected = os.path.join(self.dir.get(), self.getSelected())
        selected = os.path.abspath(selected)
        self.emit('folderSelected', selected)
        self.hide()
    
    def getSelected(self):
        '''Return the selected folder(string)'''
        selected = self.treeview.selection()

        if len(selected) == 0:
            selected = self.treeview.identify_row(0)
        else:
            selected = selected[0]

        return self.treeview.item(selected, "text")
    
    def show(self):
        '''Show the DolderDialog'''
        self.geometry("%dx%d+%d+%d" % (450, 400,
            self.parent.winfo_rootx()+int(self.parent.winfo_width()/2 - 200),
            self.parent.winfo_rooty()+int(self.parent.winfo_height()/2 - 150)
        ))
        self.deiconify()
        self.grab_set()
        #self.wait_visibility()
        self.treeview.focus_set()
        self.update()

    def hide(self):
        '''Hide the FolderDialog. Synonym:fd.cancel()'''
        self.cancel(hide=True)

    def cancel(self, event=None, hide=False):
        '''Hide/cancel the FolderDialog'''
        self.parent.focus_set()
        #self.destroy()
        self.withdraw()
        self.grab_release()
        if not hide:
            self.emit('canceled')



"""
View Class

Main window, displays the image and menu. Emit's several events.
"""
class View(EventEmitter):
    def __init__(self, root):
        EventEmitter.__init__(self)

        self.root = root

        self.frame = Frame(self.root)
        self.canvas = Canvas(self.frame,xscrollincrement=15,yscrollincrement=15,bg="#1f1f1f", highlightthickness=0)
        scrolly = Scrollbar(self.frame, orient=VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=scrolly.set)

        self.canvas.bind("<Configure>", self.onResize)
        #self.root.bind("<Configure>", self.onResize)
        self.root.bind("<Up>", self.onScroll)
        self.root.bind("<Down>", self.onScroll)
        self.root.bind("<Left>", lambda e: self.emit("prevImage"))
        self.root.bind("<Right>", lambda e: self.emit("nextImage"))
        self.root.bind("<d>", lambda e: self.emit("newDirectory"))
        self.root.bind("<f>", self.toggleFull)
        self.root.bind("<Motion>", self.onMouseMove)

        #Windows
        self.root.bind("<MouseWheel>", self.onMouseScroll)
        #Linux
        self.root.bind("<Button-4>", self.onMouseScroll)
        self.root.bind("<Button-5>", self.onMouseScroll)

        self.root.bind("<Escape>", lambda e: self.root.quit())

        self.frame.grid(column=0, row=0, sticky=(N,S,E,W))
        self.canvas.grid(column=0,row=0, sticky=(N,S,E,W))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.resizeTimeO = None
        self.mouseTimeO = self.root.after(1000, lambda x: x.frame.configure(cursor="none"), self)
        #self.lastDir = os.path.abspath("C:\Users\Alex\Media\manga") TODO: remove
        #self.img = None
        self.imgId = None
        self.fullscreen = False
        self.notFullSize = 0,0,0,0
        self.setTitle(Info.version)

    def toggleFull(self, event=None):
        '''Toggle fullscreen'''
        self.onResize()

        if self.fullscreen:
            self.root.geometry("%dx%d+%d+%d" % self.notFullSize)
            self.root.overrideredirect(0)
        else:
            self.root.overrideredirect(1)
            self.root.geometry("%dx%d+0+0" % (self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        
        self.fullscreen = not self.fullscreen
    
    def onResize(self, event=None):
        '''Resize the image after 200ms of not resizing. Also store what the window size was.'''
        if not self.fullscreen:
            self.notFullSize = self.root.winfo_width(), self.root.winfo_height(), self.root.winfo_x(), self.root.winfo_y()

        #if self.imgId != None:
        if self.resizeTimeO != None: #is this the best way to do this?
            self.root.after_cancel(self.resizeTimeO)
        #self.resizeTimeO = self.root.after(200, self.showImg, self.img)
        self.resizeTimeO = self.root.after(200, self.emit, "sizeChange", self.getCanvasSize())
    
    def setTitle(self, *titles):
        '''Set the title preluded by the name of the app'''
        titles = list(titles)
        titles.insert(0, Info.name)
        titles.insert(1, '-')
        self.setAbsTitle(*titles)
    
    def setAbsTitle(self, *titles):
        '''Set the title'''
        st = ""
        for title in titles:
            st = st + " " + unicode(title)
        self.root.title(st)
    
    def onMouseMove(self, event):
        '''Show mouse and setTimeout to hide mouse'''
        self.frame.configure(cursor="")
        if self.mouseTimeO != None:
            self.root.after_cancel(self.mouseTimeO)
        self.mouseTimeO = self.root.after(1000, lambda x: x.frame.configure(cursor="none"), self)
    
    def onMouseScroll(self, event):
        '''Scroll the canvas according to mouse wheel'''
        if event.num == 4 or event.delta == 120:
            self.canvas.yview("scroll", -3, "units")
        else:
            self.canvas.yview("scroll", 3, "units")
    
    def onScroll(self, event):
        '''Scroll the canvas according to the key pressed'''
        if event.keysym == "Down":
            self.canvas.yview("scroll", 1, "units")
        else:
            self.canvas.yview("scroll", -1, "units")
    
    def getCanvasSize(self):
        return (self.canvas.winfo_width(), self.canvas.winfo_height())
    
    def clearImage(self):
        if self.imgId != None:
            self.canvas.delete(self.imgId)
            self.imgId = None

    def showImage(self, img, num, total, pos="center"):
        #self.clearImage() # should be called?

        if img == None:
            return
        
        canvasSize = self.getCanvasSize();

        if pos == "center":
            x = (canvasSize[0] - img.size[0])/2
            y = (canvasSize[1] - img.size[1])/2
            #x = max(x, 0)
            #y = max(y, 0)
        else: #no other positioning features have been implemented
            x = 0
            y = 0
        
        self.imgId = self.canvas.create_image(x,y, image=img.tkpi, anchor="nw")
        bbox = self.canvas.bbox(ALL)
        nbbox = (0,0, bbox[2], max(bbox[3], canvasSize[1]))
        self.canvas.yview("moveto", 0.0)
        self.canvas.configure(scrollregion=nbbox)

        self.setTitle(img.folderName+"/"+img.fileName, "("+str(num+1)+"/"+str(total)+")")