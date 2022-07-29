from .__important.PluginInterface import PluginInterface

class tabto(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1, "type_":2}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "tabto", "tablast"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, form, tab, type_, Popup) -> bool:
        if type_ == "tablast":
            Popup.tabto("")
        if not form:
            Popup.tabto(tab)
        else:
            Popup.tabto(tab, form)
        return True