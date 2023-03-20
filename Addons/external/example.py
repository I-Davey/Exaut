from __important.PluginInterface import PluginInterface
from __important.PluginInterface import Types as T

class example(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    types = T.folderpath | T.filename | T.type_ | T.source | T.target | T.databasepath | T.databasename | T.keypath | T.keyfile | T.runsequence | T.treepath | T.buttonname
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "test_showcase"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, folderpath,filename,type_,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname) -> bool:
       self.logger.success(f"folderpath: {folderpath}, filename: {filename}, type: {type_}, source: {source}, target: {target}, databasepath: {databasepath}, databasename: {databasename}, keypath: {keypath}, keyfile: {keyfile}, runsequence: {runsequence}, treepath: {treepath}, buttonname: {buttonname}")
       self.Popups.alert("test alert", "test title")