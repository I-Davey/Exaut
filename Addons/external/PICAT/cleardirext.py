from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *
import shutil
import os
class cleardirext(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

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



    def main(self, folderpath,filename,type_,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname) -> bool:    
        if os.path.exists(source)==False:
            self.Popups.alert(source+" source does not exist?","Failed cleardirext: "+buttonname+"! \\"+str(runsequence))
        else:
            ext = filename
            if ext==None or ext=="":
                ext = "*.*"
            self.deleteExt(source,ext,buttonname,runsequence)
    
    def deleteExt(self, path,ext,buttonname,row):
        if os.path.isdir(path):
            files = os.listdir(path)
            for f in files:
                newpath = os.path.join(path,f)
                self.deleteExt(newpath,ext,buttonname,row)
        else:
            if self.getExt(path,ext)==True:
                try:
                    os.remove(path)
                except:
                    self.Popups.alert("Problem deleting "+path+"?","Failed cleardirext: "+buttonname+"! \\"+str(row))

    def getExt(baseN,fileN):
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