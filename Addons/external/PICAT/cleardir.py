from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *
import shutil
import os
class cleardir(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "cleardir"
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
        if os.path.exists(source)==True:
            for root, dirs, files in os.walk(source):
                for f in files:
                    try:
                        os.remove(source+"\\"+f)
                    except:
                        self.Popups.alert("Problem removing "+source+"\\"+f,"Warning: cleardir: "+buttonname+"! \\"+str(runsequence))
                    #os.unlink(os.path.join(root,f))
                for d in dirs:
                    try:
                        shutil.rmtree(source+"\\"+d)
                    except:
                        self.Popups.alert("Problem removing "+source+"\\"+d,"Warning: cleardir: "+buttonname+"! \\"+str(runsequence))
                    #shutil.rmtree(os.path.join(root,d))
        else:
            self.Popups.alert(source+" source does not exist?","Failed cleardir: "+buttonname+"! \\"+str(runsequence))