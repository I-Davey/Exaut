from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
from backend.db.Exaut_sql import *

import os
class pg(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "pg","pginput"
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



    def main(self, folderpath,filename,type_,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname) -> bool:    
        if type_=="pg":
            if "pg_pass" not in self.variables:
                self.Popups.alert("pg_pass not in variables?","Failed pg: "+buttonname+"! \\"+str(runsequence))

            elif os.path.exists(str(folderpath)+"\\"+str(filename))==False:
                self.Popups.alert(str(folderpath)+"\\"+str(filename)+" does not exist?","Failed pg: "+buttonname+"! \\"+str(runsequence))
            else:
                try:
                    self.PG_Function(f"{folderpath}\\{filename}",target,"",str(runsequence),0)
                except OSError as e:
                    self.Popups.alert(f"{folderpath}\\{filename} error running .sql file, permission issue?"," \\"+str(runsequence))
        elif type_=="pginput":
            """
            if str(bseq[pf][4])=="" or str(bseq[pf][4])=="None":
                ctypes.windll.user32.MessageBoxW(0,"No Postgres credentials provided?","Failed pginput: "+bname+"! \\"+str(bseq[pf][9]),0)
            elif os.path.exists(str(bseq[pf][0])+"\\"+str(bseq[pf][1]))==False:
                ctypes.windll.user32.MessageBoxW(0,str(bseq[pf][0])+"\\"+str(bseq[pf][1])+" does not exist?","Failed pginput: "+bname+"! \\"+str(bseq[pf][9]),0)
            else:
                self.PG_Function(str(bseq[pf][0])+"\\"+str(bseq[pf][1]),str(bseq[pf][4]),str(bseq[pf][3]),str(bseq[pf][9]),1) 
            """
            if "pg_pass" not in self.variables:
                self.Popups.alert("pg_pass not in variables?","Failed pginput: "+buttonname+"! \\"+str(runsequence))
            elif os.path.exists(str(folderpath)+"\\"+str(filename))==False:
                self.Popups.alert(str(folderpath)+"\\"+str(filename)+" does not exist?","Failed pginput: "+buttonname+"! \\"+str(runsequence))
            else:
                try:
                    self.PG_Function(f"{folderpath}\\{filename}",str(target),str(source),str(runsequence),1)
                except OSError as e:
                    self.Popups.alert(f"{folderpath}\\{filename} error running .sql file, permission issue?"," \\"+str(runsequence))

    def PG_Function(self,runfile,pg_data,inputdata,err,mode):
        pg_data = pg_data.split('|')
        txt = open(runfile).read()
        if mode==0:
            eng = engine.create_engine("postgresql://"+str(pg_data[1])+":"+str(self.variables["pg_pass"])+"@"+str(pg_data[2])+":"+str(pg_data[3])+"/"+str(pg_data[0]))
            with eng.connect() as con:
                rs = con.execute(text(txt))
                for row in rs:
                    print(row)
        elif mode==1:
            if inputdata==None or inputdata=="":
                self.Popups.alert("No variables specified in source?","Failed sql: "+err)
            else:
                customfile = str(os.path.dirname(runfile))+"\\%%%"+str(os.path.basename(runfile))
                inputdata = inputdata.split('|')
                for i in range(len(inputdata)):
                    txt = txt.replace("%var"+str(i+1)+"%",inputdata[i])
                if os.path.exists(customfile)==True:
                    newtxt = open(customfile,'w')
                    newtxt.write(txt)
                    newtxt.close()
                try:
                    eng = engine.create_engine("postgresql://"+str(pg_data[1])+":"+str(self.variables["pg_pass"])+"@"+str(pg_data[2])+":"+str(pg_data[3])+"/"+str(pg_data[0]))
                    with eng.connect() as con:
                        rs = con.execute(text(txt))
                        for row in rs:
                            print(row)
                    os.remove(customfile)
                except OSError as e:
                    self.Popups.alert("Error removing "+customfile+", permission issue?","Failed sql: "+err)
  




  