from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *

import os
class sqlinput(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "sqlinput"
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
        if os.path.exists(databasepath+"\\"+str(databasename))==False:
            self.Popups.alert(databasepath+"\\"+str(databasename)+" does not exist?","Failed sql: "+buttonname+"! runseq: \\"+str(runsequence))
            return
        if os.path.exists(str(folderpath)+"\\"+str(filename))==False:
            self.Popups.alert(str(folderpath)+"\\"+str(filename)+" does not exist?","Failed sql: "+buttonname+"! runseq: \\"+str(runsequence))
            return
        if variables==None or variables=="":
            self.Popups.alert("No variables specified in source?","Failed sql: "+buttonname+"! runseq: \\"+str(runsequence))
            return
        eng = engine.create_engine("sqlite:///"+self.addSlash(databasepath)+"\\"+databasename)
        variables = variables.split('|')
        txt = open(f"{folderpath}\\{filename}","r").read()
        for i, var in enumerate(variables):
            txt = txt.replace(f"%var{i+1}%",var)
        tempfilepath = f"{folderpath}\\%%%{filename}"
        with open(tempfilepath,"w") as f:
            self.logger.debug(txt)
            f.write(txt)
        try:
            with eng.connect() as con:
                con.execute(txt)
                os.remove(tempfilepath)
        except Exception as e:
            self.logger.error(e)
            self.Popups.alert(str(e),"Failed sql: "+buttonname+"! runseq: \\"+str(runsequence))
            os.remove(tempfilepath)
            return
        




  