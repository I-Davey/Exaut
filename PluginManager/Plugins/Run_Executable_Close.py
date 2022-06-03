from asyncio.subprocess import PIPE
from .__important.PluginInterface import PluginInterface
import os
import subprocess
import ctypes
import win32api
import time
class Run_Executable_Close(PluginInterface):
    load = True
    #types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    types = {"ftype":2, "path":0, "file":1,"specfile_1":3,"specfile_2":4,"specfile_3":5, "bname":11, "otherval":9}
    callname = "execlose"
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

    def main(self,ftype,path,file,specfile_1,specfile_2,specfile_3, bname, otherval) -> bool:
        self.runapp(ftype,path,file,specfile_1,specfile_2,specfile_3, bname, otherval)
        os._exit(0)
    def runapp(self,ftype,path,file,specfile_1,specfile_2,specfile_3, bname, otherval) -> bool:
        if specfile_2!=None and str(specfile_2)!="":
            specfile = str(specfile_1)+"~"+str(specfile_2)
        else:
            specfile = str(specfile_1)
        if file == None:
            file = ""
        if os.path.exists(path+"\\"+file)==True:
            if ftype=="execlose":
                if specfile!=None and specfile!="" and specfile!="None":
                    param = specfile
                    specfile = specfile.split('~')
                    if self.isNumeric(specfile[0])==True:
                        try:
                            win32api.WinExec("\""+path+"\\"+file+"\" \""+param+"\"")
                        except:
                            ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\" \""+specfile[0]+"\"?","Failed exe: "+bname+"! \\"+str(otherval),0)

                    else:
                        if os.path.exists(specfile)==False:
                            
                            ctypes.windll.user32.MessageBoxW(0,str(specfile[0])+" does not exist?","Failed exe!",0)
                        else:
                            try:
                                win32api.WinExec("\""+path+"\\"+file+"\" \""+specfile[0]+"\"")
                            except Exception as e:
                                ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\" \""+specfile[0]+"\"?","Failed exe: "+bname+"! \\"+str(otherval),0)
                                self.logger.error(e)
                else:
                    try:
                        #run exe then close self
                        win32api.WinExec("cmd \""+path+"\\"+file+"\"")
                        time.sleep(5)
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\"?","Failed exe: "+bname+"! \\"+str(otherval),0)
                
                #log - copied {file} from x, to y, as {newname}
                # self.logger.success("exe run")
        else:
            actualpath = path+"\\"+file
            self.logger.error(f"Program not found at location {actualpath}")
        