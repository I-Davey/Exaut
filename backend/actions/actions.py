from sqlalchemy import select, update, insert, delete
from ..db.Exaut_sql import actions, actions_categories, pluginmap


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
    
    def return_actions_categories_dict(self):
        #sort actuibs)data by sequence
        self.actions_data.sort(key=lambda x: x["sequence"])
        #order categories by sequence
        self.category_data.sort(key=lambda x: x["sequence"])
        #create dict with categories = {}
        ca_dict = {x : {} for x in self.return_categories()}
        ca_dict[None] = {}
        for action in self.actions_data:
            ca_dict[action["category"]][action["action"]] = action["plugin"]
        return(ca_dict)

    def return_plugins_type_map(self):
        ac_dict =  {}
        for action in self.actions_data:
            plugin = action["plugin"]
            plugin_type_types = self.pmgr.plugin_type_types[plugin]

   
            plugin_type_types.remove("__name") if "__name" in plugin_type_types else None
            ac_dict[plugin] = plugin_type_types
            ac_dict[plugin] = plugin_type_types
            


        return(ac_dict)

    def refresh(self): 
        self.load()

    def initial_data(self):
        return self.return_actions_categories_dict(), self.return_plugins_type_map

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



    def test(self):
        a = self.return_categories()
        b = self.return_actions_categories_dict()
        c = self.return_plugins_type_map()
        
        #category_dict = "people"
        #x = self.add_category(category_dict)

        cat_old = "people"
        cat_new = "people2"
        self.edit_category(cat_old, cat_new)

        #all_cats = self.return_categories()
        #all_cats.sort()
        #self.reorder_categories(all_cats)




        
