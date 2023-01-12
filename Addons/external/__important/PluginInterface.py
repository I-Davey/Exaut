
"""
Here is an interface for Plugin classes.
"""
class PluginInterface:

    load = False
    types = {}
    type_types = {}
    hooks_handler = []
    hooks_method = []



    callname = ""
    def getTypes(self) -> dict:
        return self.types
    def getHooks(self) -> list:
        return [self.hooks_handler, self.hooks_method]

    def getTypeFunc(self, bseq, btn) -> dict:
        return(bseq, btn)
    

class Types():
    #types
    folderpath   = {"folderpath":0}
    filename     = {"filename":1}
    type_        = {"type_":2}
    source       = {"source":3}
    target       = {"target":4}
    databasepath = {"databasepath":5}
    databasename = {"databasename":6}
    keypath      = {"keypath":7}
    keyfile      = {"keyfile":8}
    runsequence  = {"runsequence":9}
    treepath     = {"treepath":10}
    buttonname   = {"buttonname":11}


