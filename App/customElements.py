# Some custom elements I've made for this application.
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import filedialog
from fileSys import *
from QEHelper import *
from collections import defaultdict
import json
from convert import convert
import platform

# All extensions
extensions = ("ALL FILES", ".gr2", ".black", ".static", ".fsdbinary", ".json", ".xml", ".yaml", ".prs", ".bnk", ".wem", ".jpg", ".dds", ".png", ".webm", ".txt", ".py", ".gsf", ".srt", ".pathdata", ".region", ".pickle", ".css", ".tri", ".mp4", ".mp3")
icons = ("files", "box", "file-digit", "file-digit", "file-digit", "file-code", "file-code", "file-code", "file-input", "music", "music", "image", "image", "image", "youtube", "file-text", "file-code", "file-code", "message-circle", "map", "map", "file-digit", "file-code", "box", "youtube", "music")


def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class ToolTip():
    # Thank you internet for this tooltip function.
    # https://stackoverflow.com/a/56749167
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, borderwidth=1, font=("Arial", "12"))
        label.pack(ipadx=0)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class ExportWindow(tk.Frame):
    def __init__(self, root: tk.Tk, **kwargs):
        super(ExportWindow, self).__init__(**kwargs)
        self.root = root
        self.pack_propagate(False)
        self.extensionSelection = ttk.Treeview(self, selectmode=tk.BROWSE)
        self.extensionSelection.pack_propagate(False)

        # Load images.
        self.imageDict = {}
        global extensions
        global icons
        zipped = zip(extensions[1:-1], icons[1:])
        zipped = sorted(zipped, key=lambda x: x[1])
        zipped.insert(0, (extensions[0], icons[0]))
        for ext, icon in zipped:
            self.imageDict[ext] = getSVG("Images/icons/" + icon + ".svg")
            # Also load Extension Selection.
            self.extensionSelection.insert("", "end", text=ext, open=True, image=self.imageDict[ext])
        self.extensionSelection.heading("#0", text="Export Options")
        # This is how we update the conversionSettings treeview.
        self.extensionSelection.selection_set(self.extensionSelection.get_children()[0])
        self.key = "ALL FILES"

        # Extensions Conversion Window
        self.extensionConversion = ttk.Treeview(self, selectmode=tk.BROWSE)
        self.extensionConversion.pack_propagate(False)
        # Load Settings
        self.settingsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pref/conversions.json")
        with open(self.settingsPath, "r") as file:
            self.conversionSettings = json.load(file)
        self.extensionConversion.heading("#0", text="Export To...")
        self.updateConversionState(None)

        # Update Bindings.
        self.extensionSelection.bind("<<TreeviewSelect>>", self.updateConversionView)
        self.extensionConversion.bind("<<TreeviewSelect>>", self.updateConversionState)

        # Load export options.
        self.keepHierarchy = tk.BooleanVar(value=True)
        self.childrenFiles = tk.BooleanVar(value=True)
        self.childrenDirectories = tk.BooleanVar(value=True)
        # Botton Frame.
        self.bottonFrame = ttk.Frame(self)

        # The actual bottons.
        self.heirBotton = ttk.Checkbutton(self.bottonFrame, text="Keep Folder Hierarchy", variable=self.keepHierarchy, onvalue=True, offvalue=False)
        self.heirMSG = """
        If enabled, the hierarchy of the files in the preview to the left will be respected.
        If a file is in /X/Y/Z/ and you have this enabled, you will export the entire /X/Y/Z chain.
        If disabled, only the file will be exported (and selected folders).
        """
        CreateToolTip(self.heirBotton, text=self.heirMSG)

        self.childFileBotton = ttk.Checkbutton(self.bottonFrame, text="Export Child Files", variable=self.childrenFiles, onvalue=True, offvalue=False)
        self.childFileMSG = """
        If enabled, the children files inside of selected folders will be exported.
        This does not include the children files inside of subdirectories.
        """
        CreateToolTip(self.childFileBotton, text=self.childFileMSG)

        self.childDirBotton = ttk.Checkbutton(self.bottonFrame, text="Export Subdirecotries", variable=self.childrenDirectories, onvalue=True, offvalue=False)
        self.childDirMSG = """
        If enabled, the subdirectories will be exported.
        This method is recursive.
        If you have this enabled, but not "Export Child Files" you will have many empty folders.
        It is recommended that if you have this enabled, all other options are enabled as well.
        If the "Keep Folder Hierarchy" is not enabled, you will end up with copies if you have multiple directories selected!
        """
        CreateToolTip(self.childDirBotton, text=self.childDirMSG)

        # Pack the frames.
        self.extensionSelection.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="NESW", padx=5, pady=5)
        self.extensionConversion.grid(column=1, row=0, columnspan=1, rowspan=1, sticky="NESW", padx=5, pady=5)
        self.bottonFrame.grid(column=2, row=0, columnspan=1, rowspan=1, sticky="NESW", padx=5, pady=5)

        # Grid configure.
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # TODO: Add more export bottons?
        self.exportBotton = ttk.Button(self.bottonFrame, text="Export Selected", command=self.export)

        # Pack the buttons in the botton frame.
        self.heirBotton.grid(column=0, row=0, sticky="W")
        self.childFileBotton.grid(column=0, row=1, sticky="W")
        self.childDirBotton.grid(column=0, row=2, sticky="W")
        self.exportBotton.grid(column=0, row=3, stick="W")


    def updateConversionView(self, event):
        self.extensionConversion.delete(*self.extensionConversion.get_children())
        self.key = self.extensionSelection.focus()
        self.key = self.extensionSelection.item(self.key)
        self.key = self.key["text"]
        if self.key == None or len(self.key) == 0:
            self.key = "ALL FILES"
        for option in self.conversionSettings[self.key]["Options"]:
            self.extensionConversion.insert("", "end", text=option)
        state = self.conversionSettings[self.key]["State"]
        stateIndex = self.conversionSettings[self.key]["Options"].index(state)
        self.extensionConversion.selection_set(self.extensionConversion.get_children()[stateIndex])

    def updateConversionState(self, event):
        state = self.extensionConversion.focus()
        state = self.extensionConversion.item(state)
        state = state["text"]
        if len(state) == 0:
            state = "As Is"

        # Error Handling
        if self.key == ".gr2" and state == ".obj":
            if platform.system() != "Windows":
                warn(self.root, "Exporting .gr2 files to .obj is currently only supported on Windows!")
                state = "As Is"

        # Save the settings into the json file.
        self.conversionSettings[self.key]["State"] = state
        with open(self.settingsPath, "w") as file:
            json.dump(self.conversionSettings, file, indent="     ")

    def export(self):
        self.exportPath = filedialog.askdirectory(parent=self, initialdir="/", title="Please select the export path.", mustexist=True)
        # Go through all of the selected items.
        for item in self.root.selected:
            itemPath = self.exportPath
            if self.keepHierarchy.get():
                itemPath += item.fullPath
            # Save the item.
            if isinstance(item, FileItem):
                # Add the file.
                self.exportFile(item, itemPath)
            else:
                self.exportFolder(item, itemPath)

    # TODO:
    # Add in all the export options.
    def exportFile(self, item, itemPath):
        print(f"Saving {item.path} to {itemPath}")
        if not os.path.exists(itemPath):
            os.makedirs(itemPath)
        fullItemPath = os.path.join(itemPath, item.path)
        # Call our convert.py function to handle file conversion.
        convert(item.truePath, fullItemPath, self.conversionSettings)

    def exportFolder(self, item, itemPath):
        itemPath = os.path.join(itemPath, item.directory)
        # See if we have to keep going down and exporting the file's children (and/or it's sub0directories).
        if self.childrenFiles.get():
            for child in item.files:
                self.exportFile(child, itemPath)
        if self.childrenDirectories.get():
            for child in item.children:
                self.exportFolder(child, itemPath)


class PreviewWindow(tk.Frame):
    # This is the preview window.
    # Todo:
    # A whole lot more preview windows...
    def __init__(self, root: tk.Tk, **kwargs):
        super(PreviewWindow, self).__init__(**kwargs)
        self.root = root
        self.defaultLabel()

    def defaultLabel(self):
        self.mainFrame = ttk.Label(self, text="Preview Window\nDouble Click to Preview Item", anchor=tk.CENTER, compound="top")
        self.mainFrame.imagePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Images/Logo.png")
        self.mainFrame.image = loadImage(self.mainFrame.imagePath, (256, 256))
        self.mainFrame.configure(image=self.mainFrame.image)
        self.mainFrame.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)

    def defaultPreview(self):
        frame = ttk.Label(self.mainFrame, text=f"Name: {self.selected.path}\nSize: {(self.selected.size / 1000000):.2f} MB", anchor=tk.CENTER, justify=tk.LEFT, font=("Arial", 15))
        frame.name = self.selected.path
        return frame

    def imagePreview(self):
        # TODO: Image transforms like pan, zoom, etc.
        x = self.winfo_width() - 50
        y = self.winfo_height() - 50
        frame = tk.Canvas(self.mainFrame)
        frame.pImage = loadImage(self.selected.truePath, (x, y))
        frame.create_image(x / 2, y / 2, anchor=tk.CENTER, image=frame.pImage)
        frame.name = self.selected.path
        return frame

    def textPreview(self, type: int):
        # TODO: Syntax highlighting and stuff.
        frame = scrolledtext.ScrolledText(self.mainFrame, font=("Arial", 12))
        frame.text = loadText(self.selected.truePath)
        frame.insert(tk.INSERT, frame.text)
        frame.name = self.selected.path
        frame.configure(state=tk.DISABLED)
        return frame

    def folderPreview(self):
        frame = ttk.Label(self.mainFrame, text=f"Folder: {self.selected.directory}\nLocal Items: {self.selected.itemCount}\nTotal Items: {self.selected.totalItems}", anchor=tk.CENTER, justify=tk.LEFT, font=("Arial", 15))
        frame.name = self.selected.directory
        return frame

    def update(self):
        # Take the selected items and display them.
        if (len(self.root.selected) >= 1):
            # For now this only supports single element previews.
            if self.mainFrame is not None:
                self.mainFrame.destroy()
            for child in self.winfo_children():
                child.destroy()
            self.mainFrame = ttk.Notebook(self)
            self.mainFrame.pack(expand=True, fill=tk.BOTH)
            self.frames = []
            for self.selected in self.root.selected:
                if isinstance(self.selected, FileItem):
                    # Image Preview.
                    if isImage(self.selected):
                        self.frames.append(self.imagePreview())
                    # Text preview.
                    # TODO: Add syntax highlighting.
                    elif isText(self.selected):
                        self.frames.append(self.textPreview(isText(self.selected)))
                    # Default (Just display file characteristics).
                    else:
                        self.frames.append(self.defaultPreview())
                else:
                    # Display the statistics of the folder.
                    self.frames.append(self.folderPreview())
            for frame in self.frames:
                frame.pack(fill=tk.BOTH, expand=True)
                self.mainFrame.add(frame, text=frame.name)
        else:
            self.defaultLabel()


class DirectoryWindow(tk.Frame):
    # This is the directory window.
    # TODO:
    # Get horizontal scrolling working properly...
    # Add actual scroll bars?
    def __init__(self, root: tk.Tk, **kwargs):
        super(DirectoryWindow, self).__init__(**kwargs)
        # Min width until I get the horizontal scroll bar working all the way.
        self.configure(width=200)
        # A dictionary of our files, utilizes the same format that the treeView dictionary is, so we can just access them with the key of our elements.
        self.fileDict = {}
        # Dictionary of our directories.
        self.dirDict = {}
        # List of loaded subDirs.
        self.loaded = []
        # A directory of "empty" files to stand as place holders until we load other files.
        self.emptyDict = {}
        # Default icon is an alert-icon, please report it if you see it!
        self.imageDict = defaultdict(self.defaultDictValue)
        # These our all the extensions I currently have icons for, and their matching icons.
        global extensions
        global icons
        for ext, icon in zip(extensions, icons):
            self.imageDict[ext] = getSVG("Images/icons/" + icon + ".svg")
        # If you notice file formats I didn't please add them!
        # Feel free to suggest better icons and stuff too!
        self.root = root
        self.rootDir = root.rootDir
        self.tree = ttk.Treeview(self)
        self.openImg = getSVG("Images/icons/folder-open.svg")
        self.closeImg = getSVG("Images/icons/folder.svg")
        self.errorImg = self.defaultDictValue()
        self.tree.heading('#0', text=self.rootDir.directory, anchor='w')
        self.rootNode = self.tree.insert("", "end", text=self.rootDir.directory, open=True, image=self.openImg)
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.addChildren(self.rootNode, self.rootDir)
        self.addFiles(self.rootNode)
        self.tree.bind("<<TreeviewOpen>>", self.loadOpen)
        self.tree.bind("<<TreeviewClose>>", self.closeFolder)
        self.tree.bind("<<TreeviewSelect>>", self.updateSelected)
        self.tree.bind("<Double-1>", self.updatePreview)

    def addChildren(self, parent, parentDir: "FileDir"):
        self.fileDict[parent] = parentDir.files
        self.dirDict[parent] = parentDir
        if len(parentDir.children) == 0 or len(parentDir.files) == 0:
            newEmpty = self.tree.insert(parent, "end", open=False, image=self.errorImg, text="")
            self.emptyDict[parent] = newEmpty
        parentDir = sorted(parentDir.children, key=lambda x: x.directory)
        for dir in parentDir:
            # Add all sub directories.
            newParent = self.tree.insert(parent, "end", open=False, image=self.closeImg, text=dir.directory)
            self.addChildren(newParent, dir)

    def addFiles(self, parent):
        self.loaded.append(parent)
        if parent in self.emptyDict:
            self.tree.delete(self.emptyDict[parent])
        files = sorted(self.dirDict[parent].files, key=lambda x: x.path)
        for file in files:
            newNode = self.tree.insert(parent, "end", open=False, image=self.imageDict[file.fileExt], text=file.path)
            self.fileDict[newNode] = file

    def loadOpen(self, event):
        # Load files when we open the subfolders, so we don't take a while to load.
        self.tree.item(self.tree.focus(), image=self.openImg)

        # Only load files if we haven't loaded this yet.
        if self.tree.focus() not in self.loaded:
            self.addFiles(self.tree.focus())

    def closeFolder(self, event):
        self.tree.item(self.tree.focus(), image=self.closeImg)

    def defaultDictValue(self):
        return getSVG("Images/icons/alert-octagon.svg")

    def updatePreview(self, event):
        # This method updates the preview.
        self.updateSelected(event)
        self.root.pwUpdate()

    def updateSelected(self, event):
        # This method updates the selected items (for the export options mostly).
        self.root.selected = self.getSelected(self.tree.selection())

    def getSelected(self, selection):
        # Returns all FileDir and FileItem objects from the selected tuple.
        selectedObjects = []
        for selected in selection:
            if selected in self.dirDict:
                selectedObjects.append(self.dirDict[selected])
            elif selected in self.fileDict:
                selectedObjects.append(self.fileDict[selected])
        return selectedObjects
