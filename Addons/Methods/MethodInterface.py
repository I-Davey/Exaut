
"""
Here is an interface for Plugin classes.
"""
class MethodInterface:

    load = False
    types = {}
    hooks = []
    
    def getTypes(self) -> dict:
        return self.types