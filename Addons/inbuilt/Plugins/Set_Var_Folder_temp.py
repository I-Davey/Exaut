from .__important.PluginInterface import PluginInterface


class Set_Var_Folder_temp(PluginInterface):
    load = True
    types = {"target":4}
    type_types = {"target":["text", "Variable_Name (without $$)"],
     "__Name":"Set Temporary Variable -> Folderpath"}

    callname = "temp_var_folder"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, variable) -> bool:
        folderpath = self.Popups.select_folder("Select Folder",)
        folderpath = folderpath.replace("\\", "/")
        if variable in self.variables:
            self.logger.debug(f"variable {variable} already exists")
            if self.variables[variable] == folderpath:
                self.logger.success(f"variable {variable} already has the correct value")
                return True
            else:
                self.logger.debug(f"variable {variable} has a different value")
                self.variables[variable] = folderpath
                self.logger.success(f"variable {variable} has been updated")
                return True
        else:
            self.logger.debug(f"variable {variable} does not exist")
            self.variables[variable] = folderpath
            self.logger.success(f"variable {variable} has been created")
            return True
    
