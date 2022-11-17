import os
import platform
import shutil
import tkinter as tk
from QEHelper import warn

def convert(truePath: str, fullItemPath: str, settings: dict, root: tk.Tk):
    itemPath, fileExt = os.path.splitext(fullItemPath)
    print(f"Exporting with: {truePath}, {fullItemPath}")

    if settings["ALL FILES"]["State"] == "As Is":
        if not os.path.exists(fullItemPath):
            _copy(truePath, fullItemPath)
    elif settings["ALL FILES"]["State"] == "Do Not Export":
        return 1
    elif settings["ALL FILES"]["State"] == "Follow Individual Options":
        # Follow each file's own settings
        if settings[fileExt]["State"] == "As Is":
            if not os.path.exists(fullItemPath):
                _copy(truePath, fullItemPath)
        elif settings[fileExt]["State"] == "Do Not Export":
            return 1
        elif fileExt == ".gr2":
            # Right now .gr2 only supports being exported to an OBJ file on Windows.
            state = settings[fileExt]["State"]
            fullItemPath = itemPath + state
            if state == ".obj":
                if platform.system() != "Windows":
                    # We shouldn't be able to get here... But just in case.
                    warn(root, "Exporting .gr2 files to .obj is currently only supported on Windows!")
                    return -1
                # Create the directories for the file
                if not os.path.exists(fullItemPath):
                    os.makedirs(fullItemPath)
                # Let's use Tamber's tool to convert our gr2 into an OBJ.
                tamberToolPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "TamberTool", "evegr2toobj.exe")
                try:
                    os.system(f"{tamberToolPath} \"{truePath}\" \"{fullItemPath}\"")
                    return 1
                except:
                    warn(root, "Issue with Tamber Tool... Ask Hoed for help.")
                    return -1

def _copy(truePath, fullItemPath):
    if not os.path.exists(fullItemPath):
        os.makedirs(fullItemPath)
    shutil.copy(truePath, fullItemPath)
    return 1