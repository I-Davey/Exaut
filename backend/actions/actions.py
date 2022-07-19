from sqlalchemy import select, update, insert, delete
from ..db.Exaut_sql import actions, actions_categories, pluginmap, buttons, batchsequence, buttonseries


class Actions_Handler:
    def __init__(self, logger, pmgr, readsql, writesql, read_mult, get_table_query):
        self.actions = []
        self.actions_categories = []
        self.readsql = readsql
        self.writesql = writesql
        self.logger = logger
        self.pmgr = pmgr
        self.read_mult = read_mult
        self.gquery = get_table_query
        self.load()
        self.test()

    def load(self):
        self.actions_data = self.gquery(actions)
        self.category_data = self.gquery(actions_categories)
        self.pluginmap_data = self.gquery(pluginmap)
    

########
    def plugin_to_action_dict(self):
        self.refresh()
        #sort actuibs)data by sequence
        self.actions_data.sort(key=lambda x: x["sequence"])
        #create dict with categories = {}
        p2ad = {}
        for action in self.actions_data:
            p2ad[action["plugin"]] = action["action"]
        return p2ad
    def return_actions_categories_dict(self):
        self.refresh()
        #sort actuibs)data by sequence
        self.actions_data.sort(key=lambda x: x["sequence"])
        #order categories by sequence
        self.category_data.sort(key=lambda x: x["sequence"])
        #create dict with categories = {}
        ca_dict = {x : {} for x in self.return_categories()}
        ca_dict[None] = {}
        for action in self.actions_data:
            if action["category"] in ca_dict:
                ca_dict[action["category"]][action["action"]] = action["plugin"]
            else:
                ca_dict[None][action["action"]] = action["plugin"]
        return(ca_dict)

    

    def return_plugins_type_map(self):
        ac_dict =  {}
        for action in self.actions_data:
            plugin = action["plugin"]
            plugin_type_types = self.pmgr.plugin_type_types[plugin].copy()

            if type(plugin_type_types) is list:
                plugin_type_types = plugin_type_types[0]
            if "__Name" in plugin_type_types:
                del plugin_type_types["__Name"]
            ac_dict[plugin] = plugin_type_types
            ac_dict[plugin] = plugin_type_types
        return(ac_dict)

    def return_pluginmap_data(self):
        return self.pluginmap_data

    def refresh(self): 
        self.load()



##############################################################
    def get_type_plugin_map(self):
        #for tems in  self.actions_data: 
        tpm_arr = {}
        for action in self.actions_data:
            p2ad = self.plugin_to_action_dict()
            
            action_name = p2ad[action["plugin"]]


            plugin = action["plugin"]
            plugin_type_types = self.pmgr.plugin_type_types[plugin]

            if type(plugin_type_types) is not list:
                if "__Name" in plugin_type_types:
                    tpm_arr[action_name] = plugin, plugin_type_types["__Name"]
                else:
                    tpm_arr[plugin] = plugin
            elif len(plugin_type_types) > 1:
                tpm_arr[action_name] = plugin, plugin_type_types[1]
            else:
                tpm_arr[action_name] = plugin, plugin
        return(tpm_arr)
                
                
    def initial_data(self):
        return self.return_actions_categories_dict(), self.return_plugins_type_map()

    def add_category(self, category:str):
        #select max cat sequence
        max_seq = self.readsql(select([actions_categories.sequence]).order_by(actions_categories.sequence.desc()).limit(1), one=True)[0]
        category_dict = {"category": category, "sequence": max_seq + 1}
        x = self.writesql(insert(actions_categories).values(category_dict))
        if not x:
            self.logger.error("Failed to add category: " + category)
            return(False)
        self.load()

    def reorder_categories(self, categories:list):
        for i, category in enumerate(categories):
            self.writesql(update(actions_categories).where(actions_categories.category == category).values(sequence=i))
        self.load()

    def edit_category(self, category:str, new_category:str):
        self.writesql(update(actions_categories).where(actions_categories.category == category).values(category=new_category))
        self.load()
    
    def delete_category(self, category:str):
        self.writesql(delete(actions_categories).where(actions_categories.category == category))
        self.load()

    def return_categories(self):
        #order categories by sequence
        self.category_data.sort(key=lambda x: x["sequence"])
        #create list with categories
        categories = [x["category"] for x in self.category_data]
        return(categories)

    def reorder_actions(self, actions_list:list):
        for i, action in enumerate(actions_list):
            self.writesql(update(actions).where(actions.action == action).values(sequence=i))
        self.load()


    def edit_action_name(self, action:str, new_action:str):
        self.writesql(update(actions).where(actions.action == action).values(action=new_action))
        self.load()

    def edit_action_category(self, action:str, new_category:str):
        self.writesql(update(actions).where(actions.action == action).values(category=new_category))
        self.load()  

    def create_button(self, batchsequence_dict:dict, button_dict:dict, action:str):

        #get plugin from action
        plugin = self.get_type_plugin_map()[action]
        if type(plugin) is tuple:
            plugin = plugin[0]

        batchsequence_dict, button_dict = self.pmgr.plugins[plugin]['object'].getTypeFunc(batchsequence_dict, button_dict) 
        if "type" not in batchsequence_dict:
            for key, value in self.pmgr.plugin_loc.items():
                if value == plugin:
                    batchsequence_dict["type"] = key
                    break

        x = self.writesql(insert(buttons).values(button_dict))
        if not x:
            self.logger.error("Failed to add button: " + str(button_dict))
            return(False)
        self.writesql(insert(batchsequence).values(batchsequence_dict))

        
        self.load()
        return True

    def update_button(self, old_batchsequence_dict:dict, old_button_dict:dict, new_batchsequence_dict:dict, new_button_dict:dict,action:str):
        #get plugin from action
        plugin = self.get_type_plugin_map()[action]
        if type(plugin) is tuple:
            plugin = plugin[0]
        new_batchsequence_dict, new_button_dict = self.pmgr.plugins[plugin]['object'].getTypeFunc(new_batchsequence_dict, new_button_dict) 
        if "type" not in new_batchsequence_dict:
            for key, value in self.pmgr.plugin_loc.items():
                if value == plugin:
                    new_batchsequence_dict["type"] = key
                    break

        self.writesql(update(batchsequence).where(batchsequence.buttonname == old_batchsequence_dict["buttonname"]).where(batchsequence.formname == old_batchsequence_dict["formname"]).where(batchsequence.tab == old_batchsequence_dict["tab"]).values(**new_batchsequence_dict))
        self.writesql(update(buttons).where(buttons.buttonname == old_button_dict["buttonname"]).where(buttons.formname == old_button_dict["formname"]).where(buttons.tab == old_button_dict["tab"]).values(**new_button_dict))
        self.load()
        return True
    
    def delete_button(self, tab:str, button_name:str, form:str):
        self.writesql(delete(batchsequence).where(batchsequence.formname == form).where(batchsequence.tab == tab).where(batchsequence.buttonname == button_name))
        self.writesql(delete(buttons).where(buttons.formname == form).where(buttons.tab == tab).where(buttons.buttonname == button_name))
        self.load()
        return True


    def test(self):
        b = self.return_actions_categories_dict()
        print(b)
        c = self.return_plugins_type_map()
        d = self.get_type_plugin_map()
        
        #category_dict = "people"
        #x = self.add_category(category_dict)


        #all_cats = self.return_categories()
        #all_cats.sort()
        #self.reorder_categories(all_cats)
        batchseq  = {'formname': 'IAN', 'tab': 'DBX', 'buttonname': 'test cmd', 'folderpath': 'Z:/Dev/exaut/backend/auth', 'source': 'echo Hello M8'}
        button = {'formname': 'IAN', 'tab': 'DBX', 'buttonname': 'test cmd', 'buttonsequence': '0', 'columnnum': '0', 'buttondesc': 'desc'}
        action = 'Run Command'

        a = self.plugin_to_action_dict()
        print(a)
        #self.create_button(batchseq, button, action)
  
