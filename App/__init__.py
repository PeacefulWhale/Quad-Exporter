import os
import tkinter as tk
from tkinter import ttk
from functools import partial
from fileSys import *
from QEHelper import *
from customElements import *

resPath = ""
indexPath = ""
savedPaths = ""
# If enabled is empty, all files are utilized.
# Commenting lines out with # will cause them to be ignored as well.
enabled = []


def savePaths():
    global resPath, savedPaths, indexPath
    # Save the data.
    with open(savedPaths, "w") as file:
        file.write(resPath + "\n")
        file.write(indexPath + "\n")


def resMenu(root: tk.Tk):
    global resPath
    resPath = getCachePopUp(root)
    savePaths()


def indexMenu(root: tk.Tk):
    global indexPath
    indexPath = getIndexPopUp(root)
    savePaths()


def main():
    # Some variables for later
    global resPath, savedPaths, indexPath
    savedPaths = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pref", "savedPaths.txt")
    # Create the main window.
    root = tk.Tk()
    root.title("Quad-Exporter")
    root.minsize(800, 600)
    root.tk.call('tk', 'scaling', 2.0)
    # root.state("zoomed")
    # Load Preferences
    try:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pref", "enabled.txt")) as file:
            for line in file.readlines():
                line = line.strip()
                if len(line) > 0 and line[0] != "#":
                    enabled.append(line)
        print(f"Enabled File Types: {enabled}")
    except:
        warn(root, "Cannot open 'enabled' preference file")
    try:

        with open(savedPaths, "r") as file:
            resPath = file.readline().strip()
            indexPath = file.readline().strip()
    except:
        try:
            with open(savedPaths, "w") as file:
                warn(root, "Created new user [empty] preference file.")
        except:
            warn(root, "Cannot create new user preference file.\nWrite privleges may be needed.")
    # If we don't have a cache path yet, ask to get it.
    if resPath == "" or not os.path.isdir(resPath):
        resPath = getCachePopUp(root)
    if indexPath == "" or not os.path.isfile(indexPath):
        indexPath = getIndexPopUp(root)
    # Save the data.
    savePaths()
    # Check to see if we can open the folder.
    # Open the index file and create our folder.
    rootDir = parseIndex(root, indexPath, resPath, enabled)
    # The first rootDir is a true "root" and is empty, so let's go it its child.
    rootDir = rootDir.children[0]
    rootDir.directory = "ResFiles"
    print(f"Loaded {rootDir.size} bytes")
    root.rootDir = rootDir
    root.selected = []

    # Directory Window.
    dW = DirectoryWindow(root)
    dW.grid(column=0, row=0, rowspan=2, sticky="NSEW")
    dW.pack_propagate(False)

    # Preview Window.
    pW = PreviewWindow(root)
    pW.grid(column=1, row=0, sticky="NSEW")
    pW.pack_propagate(False)
    root.pwUpdate = pW.update

    # Export Window.
    eW = ExportWindow(root)
    eW.grid(column=1, row=1, sticky="NSEW")
    eW.pack_propagate(False)

    # Root gird configure.
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=5)
    root.rowconfigure(0, weight=5)
    root.rowconfigure(1, weight=1)

    # Menu Commands.
    top = root.winfo_toplevel()
    root.menuBar = tk.Menu(top)
    top['menu'] = root.menuBar

    root.subMenu = tk.Menu(root.menuBar)
    root.menuBar.add_cascade(label='Path Options', menu=root.subMenu)
    root.subMenu.add_command(label='Select Res Path', command=partial(resMenu, root))
    root.subMenu.add_command(label='Select Index Path', command=partial(indexMenu, root))

    # Finally call the mainloop.
    root.mainloop()


# In case we do multithreading / multiprocessing.
if __name__ == "__main__":
    main()
