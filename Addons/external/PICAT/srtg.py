from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *
import shutil
import os
class srtg(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "srtg"
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
        if os.path.exists(str(folderpath)+"\\$Srtg.bat")==True:
            os.system("rm "+str(folderpath)+"\\$Srtg.bat")
        if os.path.exists(str(folderpath)+"\\"+str(filename))==True:
            txt = open(str(folderpath)+"\\"+str(filename)).read()
            txt = txt.replace("%Source%",str(source))
            txt = txt.replace("%Target%",str(target))
            os.system("type NUL > "+str(folderpath)+"\\$Srtg.bat")
            if os.path.exists(str(folderpath)+"\\$Srtg.bat")==True:
                newtxt = open(str(folderpath)+"\\$Srtg.bat",'w')
                newtxt.write(txt)
                newtxt.close()
                os.system(str(folderpath)+"\\$Srtg.bat")
            else:
                self.Popups.alert("Failed srtg: "+buttonname+"! \\"+str(runsequence))
        else:
            self.Popups.alert("Failed srtg: "+buttonname+"! \\"+str(runsequence))