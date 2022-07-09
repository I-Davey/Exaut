
"""
Here is an interface for Plugin classes.
"""
class TypeInterface:

    load = False
    params = None
    callname = None
    hooks = None
    data = None
    q_object = None
    callname = ""
    key = ""

    def getParams(self) -> tuple:
        return self.params

    def getData(self):
        return self.data
    