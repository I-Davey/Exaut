from __important.PluginInterface import PluginInterface
import inspect
import sys
class stepcount(PluginInterface):
    load = True
    types = {"target":4}
    type_types = {"target":{"type":"text", "description":"please enter the number of steps", "optional":False}}

    callname = "stepcounter"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        self.all_steps = 0
        self.desired_steps = 0
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, target):
        #print code of sys.modules["backend.version"] to console
        self.backend_version = sys.modules["backend.version"]
        #use inspect to get the source code of the backend version
        self.backend_version_source = inspect.getsource(self.backend_version)
        print(self.backend_version_source)

