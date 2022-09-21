from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *

import os
class sql(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "sql"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    def addSlash(s, orig="\\"):
        prefix = s[0:2]
        suffix = s[2:]
        suffix = suffix.replace(orig, "\\\\")
        return prefix+suffix



    def main(self, folderpath,filename,type_,variables,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname) -> bool:    
        #path = str(eng[0][0])+" "+str(databasepath)+"\\"+str(bseq[pf][6])+" \".read '"+str(folderpath)+"\\\\"+str(bseq[pf][1])+"'\""
        if os.path.exists(databasepath+"\\"+str(databasename))==False:
            self.Popups.alert(databasepath+"\\"+str(databasename)+" does not exist?","Failed sql: "+buttonname+"! runseq: \\"+str(runsequence))
            return
        if os.path.exists(str(folderpath)+"\\"+str(filename))==False:
            self.Popups.alert(str(folderpath)+"\\"+str(filename)+" does not exist?","Failed sql: "+buttonname+"! runseq: \\"+str(runsequence))
            return
        eng = engine.create_engine("sqlite:///"+databasepath+"\\"+databasename)
        txt = open(f"{folderpath}\\{filename}","r").read()
        with eng.connect() as con:
            for line in txt.split(";"):
                if line.strip() != "":
                    con.execute(text(line))
        return True
 
        






  