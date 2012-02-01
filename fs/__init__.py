import os
import sys
import shutil
import glob
import zipfile
import tempfile
import urllib2
import re as regex

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

def here(*paths):
    return os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), *paths))

def path(path_or_file):
    if isinstance(path_or_file, File):
        return path_or_file.path
    elif isinstance(path_or_file, basestring):
        return path_or_file
    else:
        raise Exception()

# a dummy regular expression class, so we can distinguish between glob strings and
# true regular expressions
class re(object):
    def __init__(self, pattern):
        self.pattern = pattern
    
    def __str__(self):
        return self.pattern

class File(object):
    def __init__(self, path, strict=False, explicit=False):
        self._path = path
        self.obj = None
        self.explicit = explicit
    
    @classmethod
    def temp(cls, *vargs, **kwargs):
        # tempfile.TemporaryFile(*vargs, **kwargs)
        return cls.__init__(None)
    
    @property
    def path(self):
        return self._path
    
    @property
    def abspath(self):
        return os.path.abspath(self._path)

    @property
    def name(self):
        end = len(self.basename) - len(self.extension)
        return self.basename[:end]
    
    @property
    def basename(self):
        return os.path.basename(self._path).decode('utf8')
    
    @property
    def filename(self):
        return self.basename
        
    @property
    def dirname(self):
        return os.path.dirname(self._path)
    
    @property
    def extension(self):
        return os.path.splitext(self._path)[1]
    
    @property
    def path(self):
        return self.abspath
    
    @property
    def relpath(self):
        return self._path
    
    @property
    def exists(self):
        return os.path.isfile(self._path)

    # may change Link and Mount into proper classes
    @property
    def is_link(self):
        return os.path.islink(self._path)
    
    @property
    def is_mount(self):
        return os.path.ismount(self._path)

    @property
    def mode(self):
        pass
    
    @property
    def stat(self):
        pass
        
    @property
    def archived(self):
        pass

    @property
    def siblings(self):
        files = Directory(self.dirname).files
        return [file for file in files if file.path != self.path]

    @property
    def siblings_and_me(self):
        return self.siblings + [self]
    
    # explicit mode
    def open(self, mode='r'):
        self.obj = open(self._path, mode)
        
    def close(self):
        self.obj.close()
    
    def read(self, mode='r'):
        if self.explicit:
            return self.obj.read()
        else:
            self.open(mode)
            content = self.obj.read()
            self.close()
            return content
    
    def write(self, content, mode='w'):
        if self.explicit:
            self.obj.write(content)
        else:
            self.open(mode)
            self.obj.write(content)
            self.close()
            
    def copy(self, dest, preserve=False):
        dest = path(dest)
        if preserve:
            shutil.copy2(self._path, dest)        
        else:
            shutil.copy(self._path, dest)
    
    def save(self, dest):
        return self.copy(dest)
    
    def move(self, dest):
        os.rename(self._path, path(dest))
        
    def rename(self, dest):
        self.move(self, dest)
    
    def remove(self):
        os.remove(self._path)
        
    def archive(self):
        pass
    
    def link(self, link_name):
        return Link(link_name).to(self._path)
        
    def __cmp__(self, comparison):
        return os.path.samefile(self._path, path(comparison))

# online file (a url)
class VirtualFile(File):
    def __init__(self, path, strict=False, explicit=False):
        pass

class Link(File):
    def __init__(self, path):
        self.defined = False
    
    def to(self, file_or_path):
        # create link
        self.defined = True

class Directory(File):
    def __init__(self, *fragments):
        self._path = os.path.join(*fragments)
        self._strict = False

    @property
    def name(self):
        return self.basename
    
    def copy(self, dest):
        shutil.copytree(self._path, path(dest))
    
    def remove(self, recursive=False, force=False):
        if recursive:
            shutil.rmtree(self._path)
        else:
            os.rmdir(self._path)

    @property
    def parent(self):
        root = os.path.dirname(self.path)
        return Directory(root)

    @property
    def files(self):
        files = os.listdir(self.path)
        paths = map(lambda file: os.path.join(self.path, file), files)

        return [File(path) for path in paths if os.path.isfile(path)]

    @property
    def directories(self):
        files = os.listdir(self.path)
        paths = map(lambda file: os.path.join(self.path, file), files)
    
        return [Directory(path) for path in paths if os.path.isdir(path)]

    @property
    def siblings(self):
        return [Directory(dir) for dir in self.parent.directories if dir.path != self.path]

    @property
    def siblings_and_me(self):
        return self.siblings + [self]

    @property
    def is_root(self):
        return self.path == '/'

    @property
    def is_leaf(self):
        return len(self.directories) == 0

    def find(self, pattern='*', recursive=False, flatten=True):
        # TODO: support for trees and recursive searches
        if isinstance(pattern, basestring):
            paths = glob.iglob(self._path + '/' + pattern)
        elif isinstance(pattern, re):
            paths = [file for file in self.files if re.match(pattern, file.basename)]
        else:
            raise Exception()

        return map(File, paths)
    
    # shallow comparison
    def __cmp__(self, comparison):
        return filecmp.cmp(self._path, comparison)
    
# Directory.home = Directory(os.environ['home'])
