from __important.PluginInterface import PluginInterface
import os
import random
import string

class Compile_Pyinstaller(PluginInterface):
    load = True
    types = {"folderpath":0, "icon":3, "target":4}
    type_types = {"folderpath":{"type":"drag_drop_file", "description":"Select Python file"},"target":{"type":"drag_drop_folder", "description":"Select Compilation Location", "Optional":True}, "__Name":"Compile Exe"}

    callname = "compilexe"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, py_app, icon, save_loc ) -> bool:
        random_32_char_string_num_let = "".join( [random.choice(string.ascii_letters + string.digits) for n in range(32)] )
        py_app = py_app.replace("\\", "/")
        main_code = f"py -m PyInstaller -F  {py_app} --key {random_32_char_string_num_let}"
        if icon != "":
            icon = icon.replace("\\", "/")
            main_code += f" --icon={icon}"

        if save_loc != "":
            save_loc = save_loc.replace("\\", "/")

            main_code += f" --distpath={save_loc}"
        os.system(main_code)
        app_end_name = py_app.split("\\")[-1].split(".")[0] + ".exe"
        app_end_loc = "\\".join(py_app.split("/")[:-1]) + "\\" + "dist" + "\\" + app_end_name
        self.logger.success(f"application: {app_end_name} compiled successfully, loc: {app_end_loc}")
        return True
