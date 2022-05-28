import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from functools import partial
from fileSys import FileDir, FileItem
from cairosvg import svg2png
from PIL import ImageTk, Image, ImageOps
# Stuff for cross platform dark mode.
import io
import subprocess
import platform


def isText(dir: "FileItem"):
    # If this is a text file or human readable text.
    ext = dir.fileExt
    if ext == ".txt":
        return 1
    elif ext == ".py":
        return 2
    elif ext == ".json":
        return 3
    elif ext == ".xml":
        return 4
    elif ext == ".yaml":
        return 5
    elif ext == ".css":
        return 6
    else:
        return 0

# if this is an image file.


def isImage(dir: "FileItem"):
    # For some function things...
    return (dir.fileExt == ".png" or dir.fileExt == ".jpg" or dir.fileExt == ".dds")


def countItems(dir: "FileDir"):
    count = dir.itemCount
    for subDir in dir.children:
        count += countItems(subDir)
    dir.totalItems = count
    return count


def invert(image: Image):
    # Inverts our RGBA SVG renders.
    r, g, b, a = image.split()
    rgb_image = Image.merge('RGB', (r, g, b))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()
    return Image.merge('RGBA', (r2, g2, b2, a))


def windowsDark():
    # Stolen from stack overflow: https://stackoverflow.com/questions/65294987/detect-os-dark-mode-in-python
    try:
        import winreg
    except ImportError:
        return False
    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
    try:
        reg_key = winreg.OpenKey(registry, reg_keypath)
    except FileNotFoundError:
        return False
    for i in range(1024):
        try:
            value_name, value, _ = winreg.EnumValue(reg_key, i)
            if value_name == 'AppsUseLightTheme':
                return value == 0
        except OSError:
            break
    return False


def loadImage(file: str, size: tuple[int, int]):
    # Loads the image so we can use it in preview.
    # UTILIZES THE TRUE PATH
    image = Image.open(file)
    x, y = image.size
    targetX, targetY = size
    ratio = min(targetX/x, targetY/y)
    image = image.resize((int(x * ratio) - 1, int(y * ratio) - 1), resample=Image.BICUBIC)
    # Adding transparent background.
    background = Image.new('RGBA', size, (255, 255, 255, 0))
    background.paste(image, (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2)))
    imageTk = ImageTk.PhotoImage(background)
    return imageTk


def loadText(file: str):
    with open(file) as text:
        return text.read()


def getSVG(file: str):
    # Gets our SVG, renders it, and returns an image type compatible with Tkinter.
    # Also inverts the colors if we're on darkmode.
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), file)
    image = svg2png(url=file, scale=.75, dpi=250)
    image = Image.open(io.BytesIO(image))
    # Resize by saving a temp image.

    if platform.system() == "Darwin":
        # See if we're in dark mode or not, only works on Apple
        cmd = 'defaults read -g AppleInterfaceStyle'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        if bool(p.communicate()[0]):
            image = invert(image)
    elif platform.system() == "Windows":
        if windowsDark():
            image = invert(image)
    # TODO: Add support for Linux darkmode... There are a lot of them so IDK if I'll be able to do so easily.

    # And now we export it as a ImageTk.
    image = ImageTk.PhotoImage(image)
    return image


# indexPath parser.
def parseIndex(root: tk.Tk, filePath: str, resPath: str, enabled: list = []):
    rootDir = FileDir(resPath=resPath, enabled=enabled)
    # Create loading bar.
    pop = tk.Toplevel(root)
    pop.title("Index Parse Progress")
    pop.minsize(250, 25)
    bar = ttk.Progressbar(pop, length=200, mode="determinate", orient=tk.HORIZONTAL)
    bar.pack(padx=10, pady=10)
    image = tk.Label(pop, text="Quad-Exporter", anchor=tk.CENTER, justify=tk.CENTER, font=("Arial", 30), compound="left")
    image.imagePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "/Images/Logo.png")
    image.image = loadImage(image.imagePath, (32, 32))
    image.configure(image=image.image)
    image.pack(anchor=tk.CENTER, expand=True, fill=tk.BOTH)
    max = os.path.getsize(filePath)
    current = 0
    currentLine = 0
    # Go through files and append them to our rootDir.
    with open(filePath, "r") as file:
        for line in file.readlines():
            data = line.split(",")
            # Add the current line to the root Directory.
            rootDir.add(data[0], data[1], int(data[3], base=10))
            # Updating the progress bar.
            current += len(line)
            currentLine += 1
            if currentLine - 2500 == 0:
                currentLine = 0
                bar["value"] = (100 * (current / max))
                pop.update()
        pop.destroy()
    countItems(rootDir)
    return rootDir


# Warning Pop-Up.
def warn(root: tk.Tk, info: str):
    pop = tk.Toplevel(root)
    pop.title("Warning!")
    ttk.Label(pop, text=info).pack(padx=10, pady=10)
    pop.minsize(150, 25)
    ttk.Button(pop, text="Okay", command=pop.destroy).pack()
    pop.wait_window()


# Cache Not Found Pop-Up.
def getCachePopUp(root: tk.Tk):
    pop = tk.Toplevel(root)
    pop.resPath = ""
    pop.title("Select Shared Cache [ResFiles]")
    pop.minsize(225, 25)
    ttk.Button(pop, text="Select Shared Cache", command=partial(getCacheBrowse, pop)).pack(padx=10, pady=10)
    ttk.Button(pop, text="Cancel", command=pop.destroy).pack()
    pop.wait_window()
    return pop.resPath


# Opens a file browser and gets the resPath.
def getCacheBrowse(pop: tk.Tk):
    pop.resPath = filedialog.askdirectory(parent=pop, initialdir="/", title="Please select the cache directory.", mustexist=True)
    pop.resPath = os.path.realpath(pop.resPath)
    pop.destroy()


# Res Index Not Found Pop-Up.
def getIndexPopUp(root: tk.Tk):
    pop = tk.Toplevel(root)
    pop.indexPath = ""
    pop.title("Select Res Index File [resfileindex.txt]")
    pop.minsize(225, 25)
    ttk.Button(pop, text="Select Res Index File", command=partial(getIndexBrowse, pop)).pack(padx=10, pady=10)
    ttk.Button(pop, text="Cancel", command=pop.destroy).pack()
    pop.wait_window()
    return pop.indexPath


# Opens a file browser and gets the resPath.
def getIndexBrowse(pop: tk.Tk):
    pop.indexPath = filedialog.askopenfilename(parent=pop, initialdir="/", title="Please select the Res File Index", defaultextension=".txt")
    pop.indexPath = os.path.realpath(pop.indexPath)
    pop.destroy()
