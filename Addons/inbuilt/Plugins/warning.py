from .__important.PluginInterface import PluginInterface

class warning(PluginInterface):
    load = True
    types = {"message":3}
    type_types = {"source":{"type":"text", "description":"please enter the message", "optional":True}, "__Name":"Warning"}
    done = True

    callname = "warning"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self,message) -> bool:
        if message in ("", None):
            self.logger.warning("no message given, default used")
            message = "Are you sure you want to Proceed?"
        res = self.Popups.yesno(message, "Warning", "no" )
        print(res)
        return res

        

