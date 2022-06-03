





from loguru import logger
from graphlib import TopologicalSorter
import copy 
types = []
beforedir = dir()
from .Types import *
afterdir = dir()
for item in afterdir:
    if item not in beforedir and item not in  ("beforedir", "TypeInterface"):
        types.append(item)

class TypeManager:
    	
    def __init__(self):
        # key is type class, value is true if on else false
        self.types = {}
        self.type_loc = {}


    
    def initialiseTypes(self):
        for type_ in types:
                try:
                    # by default, the type is not active.
                    current_item = eval(type_ + f".{type_}()")
                    if current_item.load == True:
                        self.types.update({type_ : {"run" :current_item.main, "params" : current_item.params, "callname" : current_item.callname, "hooks" : current_item.hooks, "obj" : current_item}})
                        #check if current_item.callname is a tuple, if it is add twice
                        if type(current_item.callname) == tuple:
                            for item in current_item.callname:
                                self.type_loc.update({item : type_})
                        else:
                            self.type_loc.update({current_item.callname : type_})

                except Exception as e:
                    logger.error("There was an error when loading types. Make sure you follow the naming convention when writing your own types.")
                    logger.error(f"Error: {e} on type {type_}")
                    return False
        hooktoname = {}
        for type_, dict_data in self.types.items():
            if dict_data["hooks"] != None:
                hooktoname[type_] = set()
                for item in dict_data["hooks"]:
                    hooktoname[type_].add(item)
            else:
                hooktoname[type_] = set()
        #list of all items with their respective hooks
        #order so that each item that is reliant on another item is at the bottom
        #this is so that the items are loaded in the correct order
        for key, value in hooktoname.items():
            value.discard(key)
        
        sorter = TopologicalSorter(hooktoname)
        sorted = tuple(sorter.static_order())

        self.types = {key : self.types[key] for key in sorted}
        hooks = {}

        for item in self.types:
            if self.types[item]["hooks"] != None:
                self.types[item]["obj"].load_self(hooks)
            hooks[item] = self.types[item]["obj"].create_object

        logger.success(f"[Initializer]: Successfully loaded {len(self.types)} {'Types.' if len(self.types) > 1 else 'Types'}: {[*self.types]}")
        return self.types, self.type_loc






class Types:
    def __init__(self):
        self.types = {}
        self.type_loc = {}
        self.error = None
        self.fail = False
        
        global handlers
        global methods
        global plugins


        typemanager = TypeManager()
        self.types, self.type_loc = typemanager.initialiseTypes()

        #logger.success(f"handler dict: {self.handlers}")
        #logger.success(f"method dict: {self.methods}")
        #logger.success(f"plugin dict: {self.plugins}")

    def exists(self, name):
        
        if name in self.type_loc:
            return True
        else:
            return False

    def create(self, name, *params, db_key = None):
        if name in self.type_loc:
            item = copy.deepcopy(self.types[self.type_loc[name]]["obj"])
            item.key = db_key
            
            return item, item.main(*params)
        else:
            return None

    def getparams(self, name):
        if name in self.type_loc:
            return self.types[self.type_loc[name]]["params"]
        else:
            return None




