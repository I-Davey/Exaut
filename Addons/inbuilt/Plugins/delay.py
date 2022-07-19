from .__important.PluginInterface import PluginInterface
import time
class delay(PluginInterface):
    load = True
    types = {"folderpath":0}
    type_types = {"folderpath":{"type":"text", "description":"enter delay"}, "__Name":"Delay"}

    callname = "delay"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, folderpath, Popups) -> bool:
        print("startdel")
        time.sleep(int(folderpath))
        print("delay")