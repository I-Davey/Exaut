
from __important.PluginInterface import PluginInterface
import os

class Run_Executable_Loc(PluginInterface):
    load = True
    #types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    types = { "folderpath":0, "filename":1,"source":3, "target":4}
    callname = "exeloc"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    def isNumeric(self,n):
        try:
            float(n)
        except:
            return(False)
        else:
            return(True)
    
    def main(self,path,filename,param, target, Popups) -> bool:
        self.Popups = Popups

        if filename == None:
            filename = ""

        if not os.path.exists(path+"\\"+filename):
            actualpath = path+"\\"+filename
            self.logger.error(f"Program not found at location {actualpath}")
            return False

        if param == None and target == None:
            res = self.tryrun(path, filename)
            return res     
        elif param == None and target != None:
            if not os.path.exists(target):
                self.logger.error(f"path not found at location {target}")
                Popups.alert(f"path not found at location {target}", f"Failed exe 1!")
                return False
            res = self.tryrunpath(path, filename, target)
            return res

        elif param != None and target == None:
            res = self.tryrun(path, filename, param)
            return res
        else:
            if not os.path.exists(target):
                self.logger.error(f"path not found at location {target}")
                Popups.alert(f"path not found at location {target}", f"Failed exe 2!")
                return False

            self.tryrunpath(path, filename,target, param)


    def tryrun(self,path,filename,param = ""):
        try:
            if param == "":
                os.startfile("\""+path+"\\"+filename+"\"")
            else:
                self.logger.debug(f'{param} "{path}\\{filename}"')
                os.system(f'{param} "{path}\\{filename}"')
            self.logger.success(f"run exe {path}\\{filename} {param}")
            return True
        except Exception as e:
            self.logger.error(e)
            self.Popups.alert(f"Failed exe 3!", f"Failed exe 3!")
            return False

    def tryrunpath(self,path,filename, target, param = ""):
        try:
            curdir = os.getcwd()
            os.chdir(target)
            if param == "":
                self.logger.debug("param is  null")
                os.startfile("\""+path+"\\"+filename+"\"")
            else:
                #start the path\\filename in a command prompt
                self.logger.debug(f'{param} "{path}\\{filename}"')
                os.system(f'{param} "{path}\\{filename}"')
            os.chdir(curdir)
            self.logger.success(f"run exe {param} {path}\\{filename} ")
            return True
        except Exception as e:
            self.logger.error(e)
            self.Popups.alert(str(e), f"Failed exe 4!")
            return False




