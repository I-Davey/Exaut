
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
    