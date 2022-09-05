from __important.PluginInterface import PluginInterface

class sam(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1}
    type_types = {"folderpath":{"type":"text", "description":"enter number 1", "optional":True},"filename":{"type":"text", "description":"enter number 2", "optional":True}}

    callname = "sam"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, number1, number2) -> bool:
        n1 = int(number1)
        n2 = int(number2)
        self.logger.success(f"got number 1: {n1} and number 2: {n2}")
        self.Popups.alert(f"{n1 + n2}", f"{n1 + n2}")