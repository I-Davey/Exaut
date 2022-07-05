from array import array
from .__important.PluginInterface import PluginInterface
import os
import ctypes
import win32api


def exepy()-> list:
    return(["exe","py"])

class Run_Executable(PluginInterface):
    load = True
    #types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    types = {"ftype":2, "path":0, "file":1,"specfile_1":3,"specfile_2":4,"specfile_3":5, "bname":11, "otherval":9}
    type_types = {"path_exe":{"type":"drag_drop_file", "description":"please select the executable","args":"EXE Files (*.exe);;Excel Files (*.xlsx *.xlsm *.xlsb *.xls);;SQLite DB Files (*.db);;All Files (*.*)"}, "__Name":"Exe"}
    action_map = {""}
    callname = "exe","py"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    def getTypeFunc(self, bseq, btn) -> dict:
        new_file = bseq["path_exe"]
        new_file = new_file.replace("/","\\")
        #delete path_exe
        del bseq["path_exe"]
        print(new_file)
        idir = os.path.dirname(new_file)
        if idir[-1:]!="\\": #this is redundant as he is using os.path.dirname.
            idir = idir+"\\"
        bseq["filename"] = os.path.basename(new_file)
        bseq["folderpath"] = idir
        return bseq, btn

    def isNumeric(self,n):
        try:
            float(n)
        except:
            return(False)
        else:
            return(True)

    def main(self,ftype,path,file,specfile_1,specfile_2,specfile_3, bname, otherval, Popups) -> bool:
        #set cwd
        orig_dir = os.getcwd()
        try:
            os.chdir(path)
        except:
            self.logger.error("Could not change directory to: "+path)
        if specfile_2!=None and str(specfile_2)!="":
            specfile = str(specfile_1)+"~"+str(specfile_2)
        else:
            specfile = str(specfile_1)
        if file == None:
            file = ""
        if os.path.exists(path+"\\"+file)==True:
            if ftype=="exe":
                if specfile!=None and specfile!="" and specfile!="None":
                    param = specfile
                    specfile = specfile.split('~')
                    if self.isNumeric(specfile[0])==True:
                        try:
                            win32api.WinExec("\""+path+"\\"+file+"\" \""+param+"\"")
                        except:
                            ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\" \""+specfile[0]+"\"?","Failed exe: "+bname+"! \\"+str(otherval),0)
                    else:
                        #check if specfile is a list
                        
                        if not isinstance(specfile, list) and os.path.exists(specfile)==False:
                            ctypes.windll.user32.MessageBoxW(0,str(specfile[0])+" does not exist?","Failed exe!",0)
                        else:
                            try:
                                win32api.WinExec("\""+path+"\\"+file+"\" \""+specfile[0]+"\"")
                                os.chdir(orig_dir)
                                return True
                            except:
                                ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\" \""+specfile[0]+"\"?","Failed exe: "+bname+"! \\"+str(otherval),0)
                else:
                    try:
                        os.startfile("\""+path+"\\"+file+"\"")
                        os.chdir(orig_dir)
                        return True
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\"?","Failed exe: "+bname+"! \\"+str(otherval),0)
            elif ftype=="py":
                if specfile!=None and specfile!="" and specfile!="None":
                    param = specfile
                    specfile = specfile.split('~')
                    if self.isNumeric(specfile[0])==True:
                        try:
                            win32api.WinExec("python \""+path+"\\"+file+"\" \""+param+"\"")
                            os.chdir(orig_dir)
                            return True
                        except:
                            ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\" \""+specfile[0]+"\"?","Failed py: "+bname+"! \\"+str(otherval),0)
                    else:
                        if os.path.exists(specfile[0])==False:
                            ctypes.windll.user32.MessageBoxW(0,str(specfile[0])+" does not exist?","Failed py!",0)
                        else:
                            try:
                                win32api.WinExec("python \""+path+"\\"+file+"\" \""+specfile[0]+"\"")
                                os.chdir(orig_dir)
                                return True
                            except:
                                ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\" \""+specfile[0]+"\"?","Failed py: "+bname+"! \\"+str(otherval),0)
                else:
                    try:
                        win32api.WinExec("python \""+path+"\\"+file+"\"")
                        os.chdir(orig_dir)
                        return True
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem running \""+path+"\\"+file+"\"?","Failed py: "+bname+"! \\"+str(otherval),0)
        else:
            actualpath = path+"\\"+file
            self.logger.error(f"Program not found at location {actualpath}")
        os.chdir(orig_dir)
        return False

