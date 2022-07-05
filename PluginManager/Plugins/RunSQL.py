from .__important.PluginInterface import PluginInterface

class RunSQL(PluginInterface):
    load = False
    types = {"command":3}
    callname = "runsql"
    hooks_handler = ["log"]
    hooks_method = ["WriteSQL"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, methods):
        self.WriteSQL = methods["WriteSQL"].main 


    def main(self, dir, command, Popups) -> bool: 
        #check if dir exists
        self.WriteSQL(command)
        return True