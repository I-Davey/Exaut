


from threading import Thread
from inspect import iscoroutinefunction
import os
import sys

#first course of action, check for python install location by running python -c "import sys; print(sys.prefix)"
#then find the python packages folder
found = False
python_starts = ["py", "python", "python3"]
for python_start in python_starts:
    stream = os.popen('python -c "import sys; print(sys.path)"')
    python_install_location = stream.read()
    python_install_location = python_install_location.strip()
    stream.close()
    print("python install location: " + python_install_location)
    #check if string can be converted to list
    try:
        python_install_location = eval(python_install_location)
        found = True
        break
    except:
        pass

if not found:
    print("Could not find python install location")
    sys.exit(1)
#check for DLLS, lib folders in the python install location
for path in python_install_location:
    if path not in sys.path:
        sys.path.append(path)






class PluginManager:
    	
    def __init__(self):
        # key is type class, value is true if on else false
        self.plugins = {}
        self.plugin_loc = {}
        self.plugin_map = {}


    
    def initialisePlugins(self,logger, handlers, methods, plugin_type_types, plugin_loc, plugin_folder):
        sys.path.append(plugin_folder)

        for plugin in os.listdir(plugin_folder):
            try:
                if plugin.endswith(".py"):
                    #plugininterface_object = plugininterface()
                    plugin = plugin[:-3]
                    exec(f"import {plugin}")
                    
                    current_item = eval(f"{plugin}.{plugin}()")
                    if current_item.load != True:
                        logger.warning(f"{plugin} is not active")
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
                return self.plugins, self.plugin_loc, plugin_type_types
            
        logger.success(f"[Initializer]: Successfully loaded {len(self.plugins)} external {'Plugins.' if len(self.plugins) > 1 else 'Plugin'}: {[*self.plugins]}")
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


class Plugins_Ext:
    def __init__(self, pmgr, logger, plugin_folder):
        self.pmgr = pmgr
        self.logger = logger

        self.handlers = pmgr.handlers
        self.methods = pmgr.methods
        self.plugininterface = pmgr.plugininterface
        self.plugins = []
        self.plugin_loc = {}
        self.plugin_type_types  = {}
        self.plugin_map = {}
        self.error = None
        self.fail = False
        
        

      

        pluginmanager = PluginManager()
        self.plugins, self.plugin_loc, self.plugin_type_types = pluginmanager.initialisePlugins(self.logger, self.handlers, self.methods, self.plugin_type_types, self.plugin_loc, plugin_folder)
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
            self.logger.trace(f"Calling {name} with args {args}")
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
            self.logger.error(f"{name} is not a valid plugin")
            return False


