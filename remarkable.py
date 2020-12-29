"""
This file contains a class and functions that give an easy abstraction
layer between me and rmapy. It's not perfect yet by any measure, but quite
convenient.
"""
import uuid
import zipfile
import os
import os.path
import shutil

import rmapy.api
import rmapy.document
import rmapy.folder

class ReMarkable():

    def __init__(self, templateZip):
        self.templateZip = templateZip
        self.rma = rmapy.api.Client()
        self.rma.renew_token()
        if not self.rma.is_auth():
            raise ConnectionError("Cannot connect to ReMarkable cloud, try"
                                         "manually re-registering this device." )
        self.discover_filesystem()

    def discover_filesystem(self):
        """Loads all remote files and folders"""
        self.collections = self.rma.get_meta_items()
        self.docs = [ d for d in self.collections if isinstance(d, rmapy.document.Document) ]
        self.dirs = [ d for d in self.collections if isinstance(d, rmapy.folder.Folder) ]

    def make_labjournal_subfolder(self, name):
        """
        Generate new folder in labjournal folder with given name.
        Args:
             name (str): Name for new folder
        """
        # first make new folder:
        new_folder = rmapy.folder.Folder( name )
        labjournal = self.find_labjournal_folder()
        result = self.rma.create_folder(new_folder)
        if not result:
            print("Warning, folder creation bad return.")
        new_folder.Parent = labjournal.ID
        self.rma.update_metadata(new_folder)
        self.discover_filesystem()

    def prepare_templateZip( self, name ):
        """
        Make a zipdoc for uploading based on a local template.
        It changes the UUID so no duplicates.
        Keeps the zip in memory for imediate uploading.
        Args:
            name (str): path to template file
        Returns:
            zipdoc (.zip file): new zip file
        """
        loc, newUUID = make_new_UUID( self.templateZip, name )
        zipdoc = rmapy.document.ZipDocument( _id= newUUID, file=loc )
        print("Created file " + str(newUUID))
        # and remove the generated zip...
        os.remove(loc)
        return zipdoc

    def empty_dir( self, path ):
        """
        Delete the contents of the entire directory. *Not* the dir itsself.

        Args:
            path (str): path to dir to empty.
        """
        dirID = self.path_to_ID(path)
        dirs = self.get_subfolders(dirID)
        if len(dirs) != 0:
            raise ValueError( "This folder has subdirs" )
        docs = self.get_subfiles( dirID )
        if len(docs) == 0:
            pass # should I add a warning or something?
        for d in docs:
            self.delete( self.ID_to_path(d) )

    def delete(self, doc):
        """
        Delete a file in the ReMarakabale cloud at path doc

        Args:
             doc (str): Path to file to delete.
        """
        self.discover_filesystem()
        splitdoc = splitall(doc)
        dirpath = listToPath(splitdoc[:-1])
        rawdir = self.path_to_ID( dirpath )
        filename = splitdoc[-1]
        try:
            doc = [ f for f in self.docs if (
                f.Parent == rawdir and
                f.VissibleName == filename and
                isinstance(f, rmapy.document.Document) )][0]
        except IndexError:
            raise ValueError( "{0} could not be deleted: not found in cloud.".format(doc) )
        self.rma.delete( doc )

    def upload( self, path_to_file, parentFolder ):
        """
        Upload the file at path_to_file to parentFolder in the
        ReMarkable cloud

        Args:
             path_to_file (str): path to file to upload, .pdf or .epub.
             parentFolder (str): path to folder in which to upload, '' is root.
        """
        rawDoc = rmapy.document.ZipDocument( doc=path_to_file )
        parentFolderID = self.path_to_ID( parentFolder )
        if parentFolderID != '':
            parentFolder = [ f for f in self.rma.get_meta_items() if f.ID == parentFolderID][0]
        else:
            parentfolder = ''
        self.rma.upload( rawDoc, parentFolder )
        self.discover_filesystem()

    def path_to_ID( self, path ):
        """
        Convert cloud path to actual id of the folder.

        Args:
            path (str): path to dir on rmcloud.

        Returns:
            ID (str): ID string.
        """
        self.discover_filesystem()
        if path == '':
            return '' # saves some pain probably.
        splitpath = splitall( path )
        splitpath = [''] + splitpath
        IDlist = ['']
        for di in range(len( splitpath )):
            if di == 0:
                continue
            pF = [ f for f in self.rma.get_meta_items() if (
                                isinstance(f, rmapy.folder.Folder) and
                                f.VissibleName == splitpath[di] and
                                f.Parent == IDlist[di-1] ) ] [0]
            IDlist.append(pF.ID)
        return IDlist[-1]

    def ID_to_path( self, ID ):
       """
       Recursive function that finds the human readable path for an ID.
       Args:
          ID (str): rmCloud ID of a folder or document.
       Returns:
          path (str): Human readable path to ID.
       """
       c = [ f for f in self.collections if f.ID = ID][0]
       if c.parent == ""
          return r"/{}".format( c.VissibleName )
       else:
          return self._walk(c.parent) + r"/{}".format( ID.VissibleName )

    def find_labjournal_folder( self ):
        return [ f for f in self.get_subfolders('') if f.VissibleName == "Labjournal"][0]

    def get_subfolders(self, parentfolder=""):
        self.discover_filesystem()
        return [ f for f in self.dirs if f.Parent == parentfolder ]

    def get_subfiles(self, parentfolder=""):
        self.discover_filesystem()
        return [ d for d in self.docs if d.Parent == parentfolder ]

    def listdir(self, parentfolder=r"/",filesorfolders=""):
        """
        List files and folder in parentfolder. Parentfolder is given as a path, NOT an ID.
        Using filesorfolders you can set to ony show either subfiles or subfolders.
        TODO: filesorfolders is not implemented yet!!
        Args:
            parentfolder (str): absolute path to folder of which to list content
            filesorfolders (str): can be "", "folder", "file", whether to look for files of folders or all.
        Returns:
            list with (ID, path) string pairs
        """
        self.discover_filesystem()
        ID = self.path_to_ID(parentfolder)
        files = self.get_subfiles(ID)
        dirs = self.get_subfolders(ID)
        result = list()
        for i in dirs+files:
            visname = self.ID_to_path(i)
            result.append( (i,visname) )
        return result

def make_new_UUID( zipLoc, newName ):
    """
    Rename ReMarkable zip file to another generated UUID so we can do auto-upload.

    Args:
        zipLoc (str): path to zip file
    Returns:
        str: path to new zipfile
     """
    newUUID = str(uuid.uuid4())
    basedir = os.path.dirname( zipLoc )
    directory_to_extract_to = os.path.join( basedir,
                                                         "temp" )
    with zipfile.ZipFile(zipLoc, 'r') as zip_ref:
         zip_ref.extractall(directory_to_extract_to)
    for fileName in os.listdir( directory_to_extract_to ):
        name, extension = os.path.splitext(fileName)
        newFileName = newUUID + extension
        os.rename(os.path.join(directory_to_extract_to, fileName),
                  os.path.join(directory_to_extract_to, newFileName))
    newPath = shutil.make_archive( newName, 'zip', directory_to_extract_to)
    shutil.rmtree( directory_to_extract_to )
    return newPath, newUUID

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def listToPath(l):
    path = ""
    for i in l:
        path = os.path.join(path,i)
    return path
