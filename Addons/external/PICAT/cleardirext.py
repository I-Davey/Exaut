from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *
import shutil
import os
from time import perf_counter
class cleardirext(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}
    #filename, soruce
    type_types = {"filename":{"type":"text", "description":"please enter the file extension / name to delete (*.*)"},"source":{"type":"drag_drop_folder", "description":"please select the Source Folder"}}

    callname = "cleardirext"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main
        self.file_del_count = 0
        self.fullsize = 0



    def main(self, folderpath,filename,type_,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname) -> bool:    
        start = perf_counter()
        if not self.Popups.yesno("Are you sure you want to delete all files with extension "+filename+" in "+source+"?","Are you sure you want to delete all files with extension "+filename+" in "+source+"?"):
            return(False)
        if os.path.exists(source)==False:
            self.Popups.alert(source+" source does not exist?","Failed cleardirext: "+buttonname+"! \\"+str(runsequence))
        else:
            ext = filename
            if ext==None or ext=="":
                ext = "*.*"
            self.deleteExt(source,ext,buttonname,runsequence)
            end = perf_counter()
            #self.Popups.alert("Deleted "+str(self.file_del_count)+" files with extension "+ext+" in "+source, "cleardirext: "+buttonname+"! \\"+str(runsequence))
            size_mb = self.fullsize / 1024 / 1024
            time_2_dec = round(end - start, 2)
            msg = f"Deleted {self.file_del_count} files with extension {ext} in {source} in {time_2_dec} seconds. Total size {size_mb} MB"
            self.Popups.alert(msg, f"cleardirext: {buttonname}")

    def deleteExt(self, path,ext,buttonname,row):
        if os.path.isdir(path):
            files = os.listdir(path)
            for f in files:
                newpath = os.path.join(path,f)
                self.deleteExt(newpath,ext,buttonname,row)
        else:
            if self.getExt(path,ext)==True:
                try:
                    #get size of file
                    size = os.path.getsize(path)
                    self.fullsize +=  size

                    os.remove(path)
                    self.file_del_count += 1
                except:
                    self.Popups.alert("Problem deleting "+path+"?","Failed cleardirext: "+buttonname+"! \\"+str(row))

    def getExt(self, baseN,fileN):
        usebase = os.path.basename(baseN)
        #more than two asterisks
        if fileN.count('*')>2:
            return(False)
        #two asterisks no dot sandwich
        elif fileN.count('*')==2 and fileN.find("*.*")==-1:
            return(False)
        #pure "*.*"
        if fileN=="*.*":
            return(True)
        #no asterisk, pure string search
        elif fileN.find("*")==-1 and usebase.find(fileN)>=0:
            return(True)
        #asterisk(s)
        elif fileN.find("*")>=0:
            # some.something*
            if fileN.endswith("*")==True and usebase.startswith(fileN[:-1])==True:
                return(True)
            # *some.something
            elif fileN.startswith("*")==True and usebase.endswith(fileN[1:])==True:
                return(True)
            #incomplete *.*
            elif fileN.endswith("*.")==True:
                fileN = fileN+"*"
            elif fileN.startswith(".*")==True:
                fileN = "*"+fileN
            #uses *.*
            if fileN.find("*.*")>=0:
                #any name & partial extension
                if fileN.startswith("*.*")==True:
                    return(usebase.endswith(fileN[3:]))
                #partial name & any extension
                elif fileN.endswith("*.*")==True:
                    return(usebase.startswith(fileN[0:-3]))
                #partial name & partial extension
                else:
                    arr = fileN.split('*.*')
                    return(usebase.startswith(arr[0]) and usebase.endswith(arr[1]))
            #uses *.
            elif fileN.find("*.")>=0:
                arr = fileN.split('*.')
                return(usebase.startswith(arr[0]) and usebase.endswith("."+arr[1]))
            #uses .*
            elif fileN.find(".*")>=0:
                arr = fileN.split('.*')
                return(usebase.startswith(arr[0]+".") and usebase.endswith(arr[1]))
            #no other scenario
            else:
                return(False)
        #no other scenario
        else:
            return(False)