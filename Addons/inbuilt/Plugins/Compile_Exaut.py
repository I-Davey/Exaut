from .__important.PluginInterface import PluginInterface
import os

class Compile_Exaut(PluginInterface):
    load = True
    types = {"folderpath":0}
    type_types = {"folderpath":{"type":"drag_drop_folder", "description":"Select Python Root Folder"}, "__Name":"Compile Exaut"}

    callname = "compile"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, folderpath, ) -> bool:
        main_code = "py -m PyInstaller -F  exaut_gui.py --key ***REMOVED*** --icon=./frontend/favicon.ico"
        hidden_imports = ['xml','xml.dom','xml.etree', 'email.mime', 'email.mime.multipart', 'email.mime.nonmultipart', "bs4"]
        for item in hidden_imports:
            main_code += " --hidden-import " + item

        curdir = os.getcwd()
        os.chdir(folderpath)
        os.system(main_code)
        os.chdir(curdir)
        self.logger.success("Exaut compiled successfully")
        return True
