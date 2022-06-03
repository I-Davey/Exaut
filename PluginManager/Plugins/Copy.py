from .__important.PluginInterface import PluginInterface
import os
import ctypes
import shutil


class Copy(PluginInterface):
    load = True
    #types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    types = {"batch_name":2, "file_name":1, "file_source":3,"file_destination":4,"run_sequence":9,"new_name":6}
    type_types = {"path_exe":["drag_drop", "Select File to copy"], "target":["drag_drop_folder", "Select File destination"],  "databasename":["text", "New name"], "__Name":"Copy File"}
    callname = "copy"
    hooks_handler = ["log"]


    def getTypeFunc(self, bseq) -> dict:
        new_file = bseq["path_exe"]
        new_file = new_file.replace("/","\\")
        #delete path_exe
        del bseq["path_exe"]
        print(new_file)
        idir = os.path.dirname(new_file)
        if idir[-1:]!="\\": #this is redundant as he is using os.path.dirname.
            idir = idir+"\\"
        bseq["filename"] = os.path.basename(new_file)
        bseq["source"] = idir
        return bseq

    def main(self, batch_name,file_name,file_source,file_destination,run_sequence,new_name) -> bool: 
        if not new_name:
            new_name = file_name
        full_file_source = file_source+"\\"+file_name 
        full_file_destination = file_destination+"\\"+new_name
        fail_handler = "Failed copy: "+batch_name+"! \\"+str(run_sequence)
        
        if not os.path.exists(full_file_source):
            ctypes.windll.user32.MessageBoxW(0,full_file_source+" source does not exist?",fail_handler,0)
            return False
        if not os.path.exists(file_destination): 
            os.system("mkdir \""+file_destination+"\"") 
            if os.path.exists(file_destination)==False: 
                ctypes.windll.user32.MessageBoxW(0,file_destination+" target does not exist?",fail_handler,0) 
                return False
        try:
            shutil.copy2(full_file_source,full_file_destination) #copy file
            #self.logger.success("copied",file,"from",path,"to",bname,"as",specfile_1)
            self.logger.success(f"copied {file_name} from {file_source} to {file_destination} as {new_name}")
            return True
        except:
            if not os.path.exists(full_file_destination): 
                ctypes.windll.user32.MessageBoxW(0,f"Problem copying {full_file_source} to {full_file_destination}?",fail_handler,0)  
                return False
            else: 
                ctypes.windll.user32.MessageBoxW(0,f"Problem copying {full_file_source} to {full_file_destination}. Check if file is open.",fail_handler,0) 
                return False
    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True