
from concurrent.futures import thread
from Addons.inbuilt.Plugins.__important.PluginInterface import PluginInterface
items = {"Handlers": [], "Methods": [], "Plugins": []}
beforedir = dir()
from Addons.inbuilt.Handlers import *
afterdir = dir()
for item in afterdir:
    if item not in beforedir and item not in  ("beforedir", "HandlerInterface"):
        items["Handlers"].append(item)
beforedir = dir()
from Addons.inbuilt.Methods import *
afterdir = dir()
for item in afterdir:
    if item not in beforedir and item not in ("beforedir", "MethodInterface"):
        items["Methods"].append(item)

from time import perf_counter
start_time = perf_counter()
beforedir = dir()
from Addons.inbuilt.Plugins import *
afterdir = dir()
end_time = perf_counter()
print("Plugins: " + str(end_time - start_time))

for item in afterdir:
    if item not in beforedir and item not in ("beforedir", "PluginInterface"):
        items["Plugins"].append(item)


from loguru import logger
from threading import Thread
from inspect import iscoroutinefunction


class PluginManager:
    	
    def __init__(self):
        # key is type class, value is true if on else false
        self.plugins = {}
        self.plugin_loc = {}
        self.plugin_map = {}


    
    def initialisePlugins(self, handlers, methods, plugin_type_types):
        for plugin in items["Plugins"]:
                try:
                    # by default, the type is not active.
                    current_item = eval(plugin + f".{plugin}()")
                    if current_item.load != True:
                        logger.warning("Plugin {} is not active".format(plugin))
                        continue
                    self.plugins.update({plugin : {"run" :current_item.main, "args" : current_item.types, "callname" : current_item.callname, "object" : current_item}})
                    self.plugin_map.update({plugin : current_item.callname})
                    #check if current_item.callname is a tuple, if it is add twice
                    if type(current_item.callname) == tuple:
                        for item in current_item.callname:
                            self.plugin_loc.update({item : plugin})
                    else:
                        self.plugin_loc.update({current_item.callname : plugin})

                    if current_item.hooks_handler != []:
                            hooks_dict = self.hook_handler(current_item.hooks_handler, handlers)
                            current_item.load_self(hooks_dict)
                    if current_item.hooks_method != []:
                            hooks_dict = self.hook_method(current_item.hooks_method, methods)
                            current_item.load_self_methods(hooks_dict) 
                    if current_item.type_types != {}:
                        #if is string
                        if isinstance(current_item.type_types, str):
                            plugin_type_types.update({plugin :[True, current_item.load_types,current_item.type_types]})        
                        elif isinstance(current_item.type_types, bool):  
                             plugin_type_types.update({plugin : [True, current_item.load_types]})
                       #if key "__Name exists in current_item.type_types"
                        elif "__Name" in current_item.type_types.keys():
                            plugin_type_types.update({plugin :[ current_item.type_types,current_item.type_types["__Name"]]})
                        else:
                            plugin_type_types.update({plugin : current_item.type_types})



                except Exception as e:
                    logger.error("There was an error when loading types. Make sure you follow the naming convention when writing your own types.")
                    logger.error(f"Error: {e} on type {plugin}")
                    return False
                
        logger.success(f"[Initializer]: Successfully loaded {len(self.plugins)} {'Plugins.' if len(self.plugins) > 1 else 'Plugin'}: {[*self.plugins]}")
        return self.plugins, self.plugin_loc, plugin_type_types


    def hook_handler(self, hooks, handlers):
        hook_dict = {}
        for item in hooks:
            for item2 in handlers:
                if item2 == item:
                    hook_dict.update({item : handlers[item2]["run"]})
        return hook_dict
    def hook_method(self, hooks, methods):
        hook_dict = {}
        for item in hooks:
            for item2 in methods:
                if item2 == item:
                    hook_dict.update({item : methods[item2]["run"]})
        return hook_dict
class MethodManager:
    	
    def __init__(self):
        # key is type class, value is true if on else false
        self.methods = {}


    
    def initialiseMethods(self, handlers):
        for method in items["Methods"]:
                try:
                    # by default, the type is not active.
                    main_item = eval(method)
                    current_item = eval(method + f".{method}()")
                    if current_item.load != True:
                        logger.warning("Method {} is not active".format(method))
                        continue
                    self.methods.update({method : {"run" :current_item, "args" : current_item.types}})


                    if current_item.hooks != []:
                            hooks_dict = self.hook_handler(current_item.hooks, handlers)
                            current_item.load_self(hooks_dict)



                except Exception as e:
                    logger.error("There was an error when loading types. Make sure you follow the naming convention when writing your own types.")
                    logger.error(f"Error: {e} on type {method}")
                    return False
                
        logger.success(f"[Initializer]: Successfully loaded {len(self.methods)} {'Methods.' if len(self.methods) > 1 else 'Method'}: {[*self.methods]}")
        return self.methods

    def hook_handler(self, hooks, handlers):
        hook_dict = {}
        for item in hooks:
            for item2 in handlers:
                if item2 == item:
                    hook_dict.update({item : handlers[item2]["run"]})
        return hook_dict
class HandlerManager:
    	
    def __init__(self):
        # key is type class, value is true if on else false
        self.handlers = {}
        self.fail = False
        self.error = ""


    
    def initialiseHandler(self):
        for handler in items["Handlers"]:
            logger.trace(f"Loading {handler}")
            try:
                # by default, the type is not active.


                logger.trace(f"""running current_item as {handler}.{handler}() """)
                current_item = eval(handler + f".{handler}")
                logger.trace(f"current_item: {current_item}")
                current_item = current_item()
                logger.trace(f"{handler} loaded. as {current_item}")

                if current_item.load != True:
                    logger.warning("Handler {} is not active".format(handler))
                    continue
                

                self.handlers.update({handler : {"run" :current_item, "args" : current_item.types}})
            except Exception as e:
                logger.error("There was an error when loading types. Make sure you follow the naming convention when writing your own types.")
                logger.error(f"Error: {e} on type {handler}")
                self.error = e
                return False
            
        for item in self.handlers:
            try:
                state = self.handlers[item]["run"].initialise()
                if state != True:
                    logger.error(f"[Initializer]: Failed to initialise {item}")
                    #delete item
                    if self.handlers[item]["run"].vital == True:
                        logger.critical(f"{item} is vital, cannot continue: {state}")
                        self.fail = True
                        self.error = state
                        self.handlers[item] = None
                        return False
                    else:
                        logger.warning(f"{item} is not vital, continuing")
                        self.handlers[item] = None
            except Exception as e:
                logger.error(e)

        logger.success(f"[Initializer]: Successfully loaded {len(self.handlers)} {'Handlers.' if len(self.handlers) > 1 else 'Handler'}: {[*self.handlers]}")
        return self.handlers



class Plugins:
    def __init__(self):
        self.handlers = []
        self.methods = []
        self.plugins = []
        self.plugin_loc = {}
        self.plugin_type_types  = {}
        self.plugin_map = {}
        self.error = None
        self.fail = False
        self.plugininterface = PluginInterface
        
        
        global handlers
        global methods
        global plugins

        handlermanager = HandlerManager()
        self.handlers = handlermanager.initialiseHandler()
        if self.handlers == False:
            self.fail = True
            self.error = handlermanager.error
            return

        methodmanager = MethodManager()
        self.methods = methodmanager.initialiseMethods(self.handlers)

        pluginmanager = PluginManager()
        self.plugins, self.plugin_loc, self.plugin_type_types = pluginmanager.initialisePlugins(self.handlers, self.methods, self.plugin_type_types)
        self.plugin_map = pluginmanager.plugin_map

        #logger.success(f"handler dict: {self.handlers}")
        #logger.success(f"method dict: {self.methods}")
        #logger.success(f"plugin dict: {self.plugins}")
    def exists(self, name):
        
        if name in self.plugin_loc:
            return True
        else:
            return False

    def call(self, name, args, plugins = None):
        if name in self.plugin_loc:
            name = self.plugin_loc[name]
            logger.trace(f"Calling {name} with args {args}")
            #make this smaller using lambda
            arguments = self.plugins[name]["args"]
            newargs = []
            #use value
            typemap = ["folderpath","filename","type","source","target","databasepath","databasename","keypath","keyfile","runsequence","treepath","buttonname"]
            if type(args) != list:        
                for key, value in arguments.items():
                    newargs.append(args[typemap[value]])
                  
            else:
                for key, value in arguments.items():
                    newargs.append(args[value])
            newargs.append(plugins)
            #use newargs to call the function
            if iscoroutinefunction(self.plugins[name]["run"]):

                t = Thread(target=self.plugins[name]["run"], args=newargs)
                t.start()
            else:
                x = self.plugins[name]["run"](*newargs)
                return x




        else:
            logger.error(f"{name} is not a valid plugin")
            return False



