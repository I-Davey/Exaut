
"""
Here is an interface for Plugin classes.
"""
class HandlerInterface:

    load = False
    types = {}
    vital = False
    
    def getTypes(self) -> list:
        return self.types