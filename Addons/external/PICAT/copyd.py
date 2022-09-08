from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *
import shutil
import os
class copyd(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "copy"
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
        if os.path.exists(source+"\\"+folderpath)==False:
            self.Popups.alert(source+"\\"+folderpath+" source does not exist?","Failed copyd: "+buttonname+"! \\"+str(runsequence))
        elif os.path.exists(target)==False:
            os.system("mkdir \""+target+"\"")
            if os.path.exists(target)==False:
                self.Popups.alert(target+" target does not exist?","Failed copyd: "+buttonname+"! \\"+str(runsequence))
            else:
                if os.path.exists(target+"\\"+folderpath)==False:
                    try:
                        shutil.copy2(source+"\\"+folderpath,target)
                    except:
                        self.Popups.alert("Problem copying "+source+"\\"+folderpath+" to "+target+"?","Failed copyd: "+buttonname+"! \\"+str(runsequence))
                else:
                    if os.stat(source+"\\"+folderpath).st_mtime-os.stat(target+"\\"+folderpath).st_mtime>=1:
                        try:
                            shutil.copy2(source+"\\"+folderpath,target+"\\"+folderpath)
                        except:
                            self.Popups.alert("Problem copying "+source+"\\"+folderpath+" to "+target+"\\"+folderpath+"?","Failed copyd: "+buttonname+"! \\"+str(runsequence))
        else:
            if os.path.exists(target+"\\"+folderpath)==False:
                try:
                    shutil.copy2(source+"\\"+folderpath,target)
                except:
                    self.Popups.alert("Problem copying "+source+"\\"+folderpath+" to "+target+"?","Failed copyd: "+buttonname+"! \\"+str(runsequence))
            else:
                if os.stat(source+"\\"+folderpath).st_mtime-os.stat(target+"\\"+folderpath).st_mtime>=1:
                    try:
                        shutil.copy2(source+"\\"+folderpath,target+"\\"+folderpath)
                    except:
                        self.Popups.alert("Problem copying "+source+"\\"+folderpath+" to "+target+"\\"+folderpath+"?","Failed copyd: "+buttonname+"! \\"+str(runsequence))
    # Copies all files in a folder of a specific extension somewhere