from __important.PluginInterface import PluginInterface
import os 
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


    def main(self, exe, Popups) -> bool: 
        #check if dir exists



        #if exe exists:   
        if not os.path.exists(exe):         
            self.logger.error(f"{exe} does not exist")
            return False
        os.system(f'start CMD /K "{exe}"')
        self.logger.success(f"Successfully executed {exe}")
        return True