import os


def _cleanPath(filepath: str):
    # I have no clue if this will work...
    # How do I handle Window's C:/?
    # illegalChars = "<>:\"|?*"
    # Okay here's the plan... We let individuals enter in bad filepaths, and treat that as user error and thereby avoidable.
    # I'll just focus on handling CCP's strange choice of using "res:"
    # for char in illegalChars:
    #     filepath = filepath.replace(char, "")
    return filepath.replace("res:", "res")


class FileDir:
    def __init__(self, resPath: str, parent: "FileDir" = None, directory: str = "", fullPath: str = "", enabled: list = []):
        self.resPath = resPath
        self.enabled = enabled
        self.fullPath = _cleanPath(fullPath)
        self.parent = parent
        self.directory = _cleanPath(directory)
        # Children directories.
        self.children = []
        # Children Files.
        self.files = []
        self.itemCount = 0
        self.size = 0
        self.totalItems = 0

    def add(self, child: str, truePath: str, size: int):
        # Take a fileSys item and add it to the current fileSys item.
        # Create new fileSys items if needed.
        child = _cleanPath(child)
        truePath = _cleanPath(truePath)
        if (child.startswith(self.directory)):
            dirs = child.removeprefix(self.directory).split('/')
            # Get the name of the file.
            childFile = dirs[-1]
            # Cut out the name of the file.
            dirs = dirs[0:-1]
            current = self
            # I could have done this recursively, but this works as well.
            fullDir = ""
            for dir in dirs:
                fullDir = os.path.join(fullDir, dir)
                current.size += size
                matches = list(filter(lambda x: x.directory == dir, current.children))
                # there should only be one, or zero, matches, however if there are more then we've done something wrong.
                childItem = None
                if len(matches) == 0:
                    # We need to create a new fileItem.
                    childItem = FileDir(self.resPath, current, dir, fullDir, self.enabled)
                    current.children.append(childItem)
                    pass
                elif len(matches) == 1:
                    # Update the current location on our fileItem tree.
                    childItem = matches[0]
                else:
                    raise Exception("Identical Directories Created. Please file a bug report.")
                current = childItem
            # We've gotten to the final item now.
            file = FileItem(childFile, os.path.join(self.resPath, truePath), fullDir, size)
            if len(self.enabled) == 0 or file.fileExt in self.enabled:
                current.itemCount += 1
                current.files.append(file)
        else:
            raise Exception("Child Directory not part of Parent Directory!")


class FileItem():
    def __init__(self, path: str, truePath: str, fullPath: str, size: int = 0):
        self.path = _cleanPath(path)
        self.truePath = _cleanPath(truePath)
        self.size = size
        self.fullPath = _cleanPath(fullPath)
        self.fileExt = os.path.splitext(self.path)[1]
