from __important.PluginInterface import PluginInterface
import os 
import json
class runbat(PluginInterface):
    load = True
    types = {"source":3}
    type_types = {"source":["drag_drop_file", "Please select Executable"], "__Name":"Run EXE -> Bat"}

    callname = "exebat"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, folder = "C:\\Users\\idave\\Dropbox (Personal)\\pipeline") -> bool: 
        folder = folder.replace("/", "\\")
        #for file in folder
        filelist = []
        for file in os.listdir(folder):
            if file.endswith(".json"):
                file = json.loads(open(folder + "\\" + file, "r").read())
                filelist.append(file)
        print(filelist)


        