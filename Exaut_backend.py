from asyncio.subprocess import PIPE
from re import sub
from textwrap import indent
from time import perf_counter
from psutil import Popen

from psycopg2 import OperationalError
from loguru import logger as temp_start_logger
from backend.Plugins_inbuilt import Plugins 
from backend.Plugins_ext import Plugins_Ext
import sys
import os
from backend.edit_button import Edit_Button
from backend.edit_sequence_data import Edit_Sequence
from backend.edit_tab import Edit_Tab
from backend.iniconfig import Parse
from backend.db.Exaut_sql import  *
from sqlalchemy import create_engine,select, update, insert, delete, or_, and_
from sqlalchemy.orm import sessionmaker
from threading import Thread
from backend.version import version
import backend.version

from random import randint
from backend.actions.actions import Actions_Handler
import time
import json

            
class ConfigHandler:
    def __init__(self, title=None):
        self.logger = temp_start_logger
        self.file_config = None
        self.form_name = None
        self.title = title
        self.db_location = None
        self.plugin_folder = None

        self.load_data()

    def load_data(self):
        current_filename =  os.path.basename(sys.argv[0]).split(".")[0].upper()
        try:
            os.chdir(os.path.dirname(sys.argv[0]))
        except:
            self.logger.error("Could not change directory to %s" % os.path.dirname(sys.argv[0]))

        if self.title:
            current_filename = self.title
        self.file_config = Parse(self.logger, current_filename).cfg
        self.logger.debug(f"filename: {current_filename} + filecfg_arr = {self.file_config}")
        if not self.file_config:
            self.logger.error(f"No [{current_filename}] header in config.ini")
            
            ###GUI_POPUP
            sys.exit()
        else:
            self.form_name = self.file_config["form"]
        
        db_config = Parse( self.logger,"SQLCONN").cfg
        connectionpath = db_config["connectionpath"]
        connection = db_config["connection"]
        self.db_location = f"{connectionpath}\\{connection}"
        self.plugin_folder = db_config["plugin_folder"]
        self.variable_loc = db_config["variable_loc"]
        
class PluginHandler:
    def __init__(self, plugin_folder):
        self.pmgr = None
        self.plugin_folder = plugin_folder
        self.load_data()
        self.logger = self.return_logger()
        self.load_external_plugins()


    def load_data(self):
        self.pmgr = Plugins()
        if self.pmgr.fail == True:
            print(f"Critical error, plugin manager failed to load")
            print(self.pmgr.error)
            sys.exit()



    def load_external_plugins(self):
        #if self.plugin_folder is empty
        if not self.plugin_folder:
            return
        if not os.path.exists(self.plugin_folder):
            self.logger.error(f"Plugin folder does not exist: {self.plugin_folder}")
            return
        if not os.path.isdir(self.plugin_folder):
            self.logger.error(f"Plugin folder is not a folder: {self.plugin_folder}")
            return
        #if self.plugin_folder is empty
        if not os.listdir(self.plugin_folder):
            return


        self.pmgr_ext = Plugins_Ext(self.pmgr, self.logger, self.plugin_folder)
        if self.pmgr_ext.fail == True:
            print(f"Critical error, plugin manager failed to load")
            print(self.pmgr_ext.error)
            sys.exit()
        self.pmgr.plugin_map.update(self.pmgr_ext.plugin_map)
        self.pmgr.plugins.update(self.pmgr_ext.plugins)
        self.pmgr.plugin_type_types.update(self.pmgr_ext.plugin_type_types)
        self.pmgr.plugin_loc.update(self.pmgr_ext.plugin_loc)


        

    def return_logger(self):
        x = self.pmgr.handlers["log"]["run"]
        return x

class QueryHandler():
    def __init__(self,logger, db_loc):
        self.logger = logger
        self.engine = create_engine(f'sqlite:///{db_loc}', echo=False, future=True)
        self.Session = sessionmaker(self.engine)
        self.check_tables_exist()

    def check_tables_exist(self):
        #if forms does not exist, create it
        for table in tables:
            if not  self.engine.dialect.has_table(self.engine.connect(), table):
                self.logger.debug(f"Table: {table} does not exist, creating")
                curtable = eval(table)
                curtable.metadata.create_all(self.engine)
                self.logger.success(f"Successfully created {table}")
        
    def readsql(self, query, one=False, log = False, timer = False):
        if log:
            self.logger.info(query.compile(dialect=self.engine.dialect))
        if timer:
            start = perf_counter()
        with self.Session.begin() as session:
            if one == True:
                data = session.execute(query).first()
            else:
                data = session.execute(query).all()
        if timer:
            end = perf_counter()
            self.logger.info(f"Query took {round((end-start),2)} seconds")

        return data
    
    def writesql(self, query, log = False):
        if log:
            self.logger.info(query.compile(dialect=self.engine.dialect))
        with self.Session.begin() as session:
            try:
                session.execute(query)
                return True
            except Exception as e:
                if e.__class__.__name__ == "IntegrityError":
                    #take text in e up to newline
                    e = e.__str__().split('\n')[0]
                    self.logger.error(f"{e.__class__.__name__}: {e}")
                else:
                    self.logger.error(f"Error: {e}")
                return False
            
    def get_table_query(self, tbl):
        info_arr = []
        session = self.Session()
        for row in session.query(tbl).all():
            row_dict = row.__dict__
            #remove the _sa_instance_state attribute
            del row_dict["_sa_instance_state"]
            info_arr.append(row_dict)
        session.close()
        return info_arr
            
    
    def read_mult(self, queries:list, log = False):
        with self.Session.begin() as session:
            for query in queries:
                if log:
                    self.logger.info(query.compile(dialect=self.engine.dialect))
                data = session.execute(query).all()
                yield data
    

class UserInterfaceHandlerPyQT():
    def __init__(self, logger, db, pmgr, gui, formname, variable_loc):

        self.logger = logger
        self.readsql = db.readsql
        self.writesql = db.writesql
        self.read_mult = db.read_mult
        self.pmgr = pmgr
        self.initial = True
        self.formname = formname
        self.gui = gui
        self.very_original_formname = formname
        self.tab_buttons = {}
        self.tablist = []
        self.title = ""
        self.form_desc = ""
        self.version = version
        self.popups = self.Popups(self.gui, self.logger, self)
        self.variable_loc = variable_loc
        self.handle_plugins()
        #self.refresh(launch = True)
        self.actions = Actions_Handler(logger,pmgr, self.readsql, self.writesql, db.read_mult, db.get_table_query)
        self.edit_tab_handle()
        self.pmgr.handle_popups(self.popups)
        self.pmgr.handle_form(self.formname, self.variable_loc, self)

    def edit_tab_handle(self):
        self.edit_tab = Edit_Tab(self.writesql, self.logger, self.alert)


    def handle_vars(self):
        #where form is self.formname or form is "*"
        #q1 = self.readsql(select (variables.key, variables.value).where(variables.form == "*"))
        #q2 = self.readsql(select (variables.key, variables.value).where(variables.form == self.formname))
        #and:::
        #q3 = self.readsql(select (variables.key, variables.value).where(variables.loc == "*"))
        #q4 = self.readsql(select (variables.key, variables.value).where(variables.loc == self.variable_loc))

        #use or to combine the four queries
        q = self.readsql(select (variables.key, variables.value).where(or_(variables.form == "*", variables.form == self.formname)).where(or_(variables.loc == "*", variables.loc == self.variable_loc)))
        self.var_dict = {v.key : v.value for v in q}
        self.pmgr.refresh_vars(self.var_dict)
        self.pmgr.handle_form(self.formname, self.variable_loc, self)



    def addvar(self, key, value, overwrite = False, global_var = False, global_loc = False):
        self.refresh()
        form = "*" if global_var else self.formname
        loc = "*" if global_loc else self.variable_loc
        if key in self.var_dict:
            if overwrite:
                self.writesql(variables.update().where(variables.key == key, variables.form == form, variables.loc == loc, ).values(value = value))
            else:
                self.alert(f"Variable {key} already exists, not overwriting")
        else:
            self.writesql(insert(variables).values(key = key, value = value, form = form, loc = loc))
        
        #refresh the var_dict and refresh the main gui interface
        self.handle_vars()
        self.refresh()

#{"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    def call_plugin(self, type_call:str, **kwargs):
        #generate empty dict based on keys in batchsequence
        bseq = {k:None for k in batchsequence.__table__.columns.keys()}
        #replace type_ with type if in kwargs
        if "type_" in kwargs:
            kwargs["type"] = kwargs.pop("type_")
            
        
        #update with kwargs
        bseq.update(kwargs)


        function_, data = self.pmgr.call, (type_call, bseq)
        button_thread = Thread(target = function_, args = data)
        button_thread.start()
        
        


    def handle_plugins(self):
        plugin_map = self.pmgr.plugin_map
        for plugin, types in plugin_map.items():
            if type(types) == tuple:
                types = ",".join(types)
                plugin_map[plugin] = types
        
        try:
            ##from pluginmap db get all plugins and types
            data = self.readsql(select(pluginmap.plugin, pluginmap.types))
            for row in data:
                if "," in row.types:
                    self.writesql(delete(pluginmap).where(pluginmap.plugin == row.plugin).where(pluginmap.types == row.types))
        except OperationalError as e:
            self.logger.error(f"Error reading pluginmap, please add table to db")
            self.logger.error(f"{e}")
            input("Press enter to exit")
            sys.exit()
        #print all items in db
        map_in_db = {}
        for item in data:
            if item.plugin not in map_in_db:
                map_in_db[item.plugin] = item.types
            else:
                map_in_db[item.plugin] += "," + item.types
        
        for item, value in plugin_map.items():
                if item not in map_in_db:
                    for item2 in value.split(","):
                        self.logger.info(f"Adding plugin {value} to db")
                        self.writesql(insert(pluginmap).values(plugin=item, types=item2, generated = 1))
                else:
                    a = plugin_map[item].split(",")
                    b = map_in_db[item].split(",")
                    a.sort()
                    b.sort()
                    if a != b:
                        for item2 in b:
                            if item2 not in a:
                                self.logger.info(f"Removing plugin {item} with type: {item2}  from db")
                                self.writesql(delete(pluginmap).where(pluginmap.plugin == item).where(pluginmap.types == item2))
                        #add new plugins
                        for item2 in a:
                            if item2 not in b:
                                self.logger.info(f"Adding type {item2} to db")
                                self.writesql(insert(pluginmap).values(plugin=item, types=item2, generated = 1))
                                


        data = self.readsql(select(actions.plugin))
        action_arr = [action.plugin for action in data]
        for plugin, values in self.pmgr.plugin_type_types.items():
            if plugin not in action_arr:
                if len(values) == 1 or type(values) != list:
                    name = plugin
                else:
                    name = values[1]
                self.logger.info(f'Adding action "{name}" to db as plugin "{plugin}"')
                x = self.writesql(insert(actions).values(action=name,plugin=plugin, category=None, sequence = 0, generated=1 ))
                if not x:
                    self.logger.error(f"Error adding action {name} to db")
                    input("Press enter to continue")
                self.logger.success(f'Successfully added action "{name}" to db')     
        pluginmap_items = [item.plugin for item in self.readsql(select(pluginmap.plugin))]
        #values in pmgr.plugin_map
        #combine actions_all with action_arr without duplicates
        actions_all =[x for x in  self.pmgr.plugin_map]
        items_2_del = [item for item in pluginmap_items + action_arr if item not in actions_all and item not in (".", "assignseries", "tablast")]
        
        #delete from db
        for item in items_2_del:
            self.logger.info(f"Removing plugin {item} from db")
            self.writesql(delete(pluginmap).where(pluginmap.plugin == item))
            self.writesql(delete(actions).where(actions.plugin == item))
        if items_2_del != []:
            self.handle_plugins()



    class Popups:
        def __init__(self, gui, logger, parent_):
            self.parent_ = parent_
            self.gui =  gui
            self.logger = logger

        def random(self):
            while True:
                x = randint(0, 9999999999)
                if x not in self.gui.popup_msgs:
                    return x
                
        def alert(self, msg, title = None):
            self.parent_.gui.signal_alert.emit(str(msg), title)
            return True
            
        def yesno(self, message, title="", default="no"):
            return self.call(self.gui.signal_popup_yesno,(message, title, default))


        def data_entry(self, message, title="", default=""):
            return self.call(self.gui.signal_popup_data, (message, title, default))

        def select_file(self, title, folderloc=""):
            return self.call(self.gui.signal_select_file_popup, (title, folderloc))
        
        def select_folder(self, title, folderloc=""):
            return self.call(self.gui.signal_select_folder_popup, (title, folderloc))

        def custom(self, component, *args, nowait = False):
            if nowait:
                return self.call_nowait(self.gui.signal_popup_custom, ([component, args]))
            return self.call(self.gui.signal_popup_custom, ([component, args]))
        


        

       
            
        def call(self, signal, args):
            key = str(self.random())
            if type(args) != tuple: 
                args = (args,)
            signal.emit(key, *args)
            while key not in self.gui.popup_msgs:
                time.sleep(0.1)
            res = self.gui.popup_msgs[key]
            del self.gui.popup_msgs[key]
            return res

        def call_nowait(self, signal, args):
            key = str(self.random())
            if type(args) != tuple:
                args = (args,)
            print(*args)
            signal.emit(key, *args)
            return True

        def tabto(self, tab, form = None):
            return self.call(self.gui.signal_popup_tabto, (tab, form))

        def refresh(self):
            self.parent_.gui_refresh()
            return True



    def user_input(self, input_):
        return input(input_)

    def alert(self, message, title = None):
        self.logger.info(message)
        self.gui.alert(message, title)


    def gui_refresh(self):
        self.gui.signal_refresh.emit()

    def refresh(self, launch = False):
        self.handle_vars()
        tab_info, self.buttondata, types_, colors = self.read_mult([select('*').where(tabs.formname == self.formname).order_by(tabs.tabsequence.asc()), 
                                                                    select('*').where(buttons.formname == self.formname).order_by(buttons.buttonsequence.asc()), 
                                                                    select(batchsequence.type, batchsequence.tab, batchsequence.buttonname).where(batchsequence.formname == self.formname), 
                                                                    select(pluginmap.types, pluginmap.color)])

        

        newbuttondata = []

        types_ = [dict(item._mapping) for item in types_]
        colors = [list(dict(item._mapping).values()) for item in colors]
        colors_dict = {}
        for item in colors:
            if "," in item[0]:
                for item2 in item[0].split(","):
                    colors_dict[item2] = item[1]
            else:
                colors_dict[item[0]] = item[1]

        for button in self.buttondata:

            newbutton = button._asdict()
            found = False
            for type_ in types_:
                if type_ == None:
                    continue
                if newbutton["buttonname"] == type_["buttonname"] and newbutton["tab"] == type_["tab"]:
                    newbutton["type"] = type_["type"]
                    if type_["type"] in colors_dict:
                        newbutton["color"] = colors_dict[type_["type"]]
                    else:
                        self.logger.warning(f"Type: {type_['type']} not found in pluginmap.. adding placeholder as red")

                        self.writesql(insert(pluginmap).values(plugin=type_["type"], types=type_["type"], color="255,0,0,1", generated = 1))
                        colors_dict[type_["type"]] = "."
                        newbutton["color"] = "256,0,0,1"
                    found = True
            if not found:
                if launch:
                    self.logger.warning(f"Button '{newbutton['buttonname']}' on Tab '{newbutton['tab']}'  not found in batchsequence")
                newbutton["type"] = None
                newbutton["color"] = None
            newbuttondata.append(newbutton)


        buttons_data_ordered = newbuttondata.copy()

        buttons_tabs = {}
        for tab in tab_info:
            tab_name = tab.tab
            buttons_tabs[tab_name] = {}
            buttons_tabs[tab_name]["buttons"] = []
            buttons_tabs[tab_name].update(tab._asdict())
        #order buttons by item.columnum asc
        newbuttondata.sort(key=lambda button: int(button["columnnum"]) if button["columnnum"] not in ("", None) else -5)
        for button in buttons_data_ordered:
            if button["tab"] not in buttons_tabs:
                continue
                buttons_tabs[button["tab"]] = {}
                buttons_tabs[button["tab"]]["buttons"] = []
                [buttons_tabs[button["tab"]].update({column.key:None}) for column in tabs.__table__.columns]

            buttons_tabs[button["tab"]]["buttons"].append([button["buttonsequence"], button["buttonname"], button["columnnum"], button["buttondesc"], button["type"], button["color"]])
        self.tab_buttons = buttons_tabs
        self.tablist = [tab.tab for tab in tab_info]
        return(self.tablist, self.tab_buttons)

    def load(self):

        form_data = self.readsql(select(forms.formname, forms.formdesc).where(forms.formname == self.formname), one=True)
        form_title = form_data.formname if form_data else None
        form_desc = form_data.formdesc if form_data else None
        if form_title == None:
            self.logger.warning(f"No form with name {self.formname}")
            inpt = self.popups.yesno(f"No form with name {self.formname} found. Do you want to create it?", title = "Form not found")
            if inpt:
                inpt = self.popups.data_entry(f"Enter form Description", title = "Form Description")
                if inpt:
                    self.writesql(insert(forms).values(formname = self.formname, formdesc = inpt))
                    self.logger.info(f"Form {self.formname} created")
                    return self.load()
                else:
                    self.formname = self.title
                    form_title = self.title
                    form_desc = self.form_desc
            else:
                self.formname = self.title
                form_title = self.title
                form_desc = self.form_desc
        self.title = str(form_title) if form_title else self.formname
        self.form_desc = str(form_desc) if form_desc else  "Exaut"

        self.edit_sequence_load()
        self.load_edit_button()

        return(self.title, self.form_desc)

    def button_click(self, button_name,tab_name,button_obj,mode=1):
        batchsequence_data = self.readsql(select('*').where(batchsequence.formname == self.title).where(batchsequence.buttonname == button_name).where(batchsequence.tab == tab_name))
        if len(batchsequence_data) == 0:
            self.alert(f"No batchsequence data found for button: {button_name} on tab: {tab_name} in form: {self.title}")
        elif mode in (1, "sequence"):
            if len(batchsequence_data) > 1:
                mode = "sequence"
            for batchsequence_ in batchsequence_data:
                if batchsequence_.type == "assignseries":
                    if mode == "sequence":
                        res = self.assignseries_handler(self.logger, self.button_click, self.readsql,  button_name, tab_name, batchsequence_)
                        return res, "assignseries"
                    sequence_thread = Thread(target=self.assignseries_handler, args=(self.logger, self.button_click, self.readsql,  button_name, tab_name, batchsequence_))
                    sequence_thread.start()
                    return True, "assignseries"
                elif self.pmgr.exists(batchsequence_.type):
                    if mode == "sequence":
                        return self.pmgr.call(batchsequence_.type, batchsequence_._mapping), batchsequence_.type
                    function = self.pmgr.call, (batchsequence_.type, batchsequence_._mapping)
                    button_thread = Thread(target = self.single_button_handler, args=(button_name, tab_name, function))
                    button_thread.start()
        
    def single_button_handler(self, button_name, tab_name, function):
        res, type_ = self.button_click(button_name, tab_name, button_obj=None, mode="sequence")
        self.gui.signal_button_complete.emit(tab_name, button_name)

    def assignseries_handler(self,logger, button_click,readsql, button_name, tab_name, batchsequence_):
        original_button_name = button_name
        if batchsequence_.source ==  None:
            self.alert(F"No source specified for {button_name} on tab {tab_name} in form {self.title}")
            return
        series = readsql(select(buttonseries.formname, buttonseries.tab, buttonseries.buttonname).where(buttonseries.assignname == batchsequence_.source).where(buttonseries.formname == self.title).order_by(buttonseries.runsequence.asc()))
        if len(series) == 0:
            self.alert(F"No series found for {button_name} on tab {tab_name} in form {self.title} where assignname = {batchsequence_.source}")
            return
        ctime = perf_counter()
        for button in series:
            form_name = button.formname
            tab_name = button.tab
            button_name = button.buttonname
            res, type_ = button_click(button_name, tab_name, button_obj=None, mode="sequence")
            if not res:
                if type_ == "warning":
                    logger.warning("stopped sequence")
                    break

        endtime = perf_counter()
        self.gui.signal_button_complete.emit(tab_name,original_button_name)
        logger.success(f"completed button sequence {original_button_name} in {round((endtime-ctime),2)} seconds") 



    def actions_save(self,button_dict:dict, batchsequence_dict:dict,  action:str):
        self.actions.create_button(batchsequence_dict, button_dict, action)
        self.gui_refresh()
    def actions_update(self, old_batchsequence_dict:dict, old_button_dict:dict, new_batchsequence_dict:dict, new_button_dict:dict,action:str):
        self.actions.update_button(old_batchsequence_dict, old_button_dict, new_batchsequence_dict, new_button_dict, action)
        self.gui_refresh()
    def actions_delete(self,form:str, tab:str, button_name:str):
        self.actions.delete_button(tab, button_name, form)
        self.gui_refresh()
    def get_actions(self):
        return self.actions
    

    def get_init_data(self):
        return self.actions.initial_data()
    




##Popup Functions#############################################################################################################

    def set_color(self, type_, color, fill):
        color = f"{color[0]},{color[1]},{color[2]},{color[3]}" if fill else f"{color[0]},{color[1]},{color[2]}"
        self.writesql(update(pluginmap).where(pluginmap.types == type_).values(color = color))
        self.load()
        self.gui_refresh()
    
    def remove_color(self, type_):
        self.writesql(update(pluginmap).where(pluginmap.types == type_).values(color = None))
        self.load()
        self.gui_refresh()

##Add Form or styuff##########################################################################################################
    def get_form_details(self, formname):
        return self.readsql(select('*').where(forms.formname == formname))


    def edit_form_update(self,  old_formname, new_formname, new_formdesc):
        x = self.readsql(select('*').where(forms.formname == old_formname))
        if len(x) == 0:
            self.alert(f"No form found with name: {old_formname}")
            return
        
        if new_formname != old_formname:
            x = self.readsql(select('*').where(forms.formname == new_formname))
            if len(x) > 0:
                self.alert(f"Form {new_formname} already exists")
                return
            x = self.writesql(update(forms).where(forms.formname == old_formname).values(formname=new_formname, formdesc=new_formdesc))

            #tabs, buttons, batchsequence, buttonseries
            x = self.writesql(update(buttonseries).where(buttonseries.formname == old_formname).values(formname=new_formname))
            x = self.writesql(update(batchsequence).where(batchsequence.formname == old_formname).values(formname=new_formname))
            x = self.writesql(update(buttons).where(buttons.formname == old_formname).values(formname=new_formname))
            x = self.writesql(update(tabs).where(tabs.formname == old_formname).values(formname=new_formname))
            x = self.writesql(update(batchsequence).where(batchsequence.type == "TabTo").where(batchsequence.folderpath == old_formname).values(folderpath=new_formname))

            
            
            self.title = new_formname
            self.formname = new_formname
        else:
            x = self.writesql(update(forms).where(forms.formname == old_formname).values( formdesc=new_formdesc))






        self.gui_refresh()

    def edit_form_delete(self, formname):
        
        self.writesql(delete(buttonseries).where(buttonseries.formname == formname))
        self.writesql(delete(batchsequence).where(batchsequence.formname == formname))
        self.writesql(delete(buttons).where(buttons.formname == formname))
        self.writesql(delete(tabs).where(tabs.formname == formname))
        self.writesql(delete(forms).where(forms.formname == formname))
        if self.very_original_formname == formname or self.very_original_formname == None:
            self.very_original_formname = None
            first_item_in_forms = self.readsql(select(forms.formname).order_by(forms.formname.asc()).limit(1))
            if len(first_item_in_forms) > 0:
                self.very_original_formname = first_item_in_forms[0].formname
        self.formname = self.very_original_formname
        self.title = self.very_original_formname
        self.gui_refresh()

##EXPORT FUNCTIONS############################################################################################################

    def export_tab(self, tabname, export_loc):
        start_time = perf_counter()
        button_arr = []
        batchsequence_arr = []


        self.refresh()
        self.logger.info(f"Exporting tab {tabname}")
        tab = self.tab_buttons[tabname].copy()
        if export_loc not in self.var_dict:
            self.alert(f"Pipeline path not set in variables, please set it")
            return
        path = self.var_dict[export_loc] + "/db_tabs"
        if not os.path.exists(path):
            self.alert(f"Pipeline path {path} does not exist")
            return
        if not os.path.isdir(path):
            self.alert(f"Pipeline path {path} is not a directory")
            return
        if not os.access(path, os.W_OK):
            self.alert(f"Pipeline path {path} is not writable")
            return
        if not os.access(path, os.R_OK):
            self.alert(f"Pipeline path {path} is not readable")
            return

        #strip special symbols frin tab["formname"] an  tab["tab"] to be able to use as filename

        fnametab = tab["formname"]

        tab_clean = "".join(c for c in tab["tab"] if c.isalnum() or c in ("_", "-"))
        
        filename = "".join(e for e in fnametab if e.isalnum() or e in ("_","-")) + "__" + tab_clean + ".json"


        for i, button in enumerate(tab["buttons"]):
            if button[4] == "assignseries":
                self.logger.warning(f"assignseries button {button[1]} on tab {tab['tab']} in form {tab['formname']} not exported")
                continue
            formname = tab["formname"]
            tabname = tab["tab"]
            buttonname = button[1]
            button_q = self.readsql(select("*").where(buttons.formname == formname).where(buttons.tab == tabname).where(buttons.buttonname == buttonname), one=True)
            if len(button_q) == 0: 
                self.logger.warning(f"button {buttonname} on tab {tabname} in form {formname} not exported")
                continue
            batchsequence_q = self.readsql(select("*").where(batchsequence.formname == formname).where(batchsequence.tab == tabname).where(batchsequence.buttonname == buttonname), one=True)
            if len(batchsequence_q) == 0:
                self.logger.warning(f"batchsequence {buttonname} on tab {tabname} in form {formname} not exported")
                continue
            button_dict = dict(button_q._mapping)
            batchsequence_dict = dict(batchsequence_q._mapping)

            button_arr.append(button_dict)
            batchsequence_arr.append(batchsequence_dict)
        
        tab.pop("buttons")

        final_dict = {"tabs":tab, "buttons":button_arr, "batchsequence":batchsequence_arr}


        with open(path + "/" + filename, "w") as f:
            json.dump(final_dict, f, indent=4)
        end_time = perf_counter()
        self.logger.success(f"Exported tab {tabname} to {path}/{filename} in {round((end_time-start_time),2)} seconds")

    def export_form_json(self, formname, export_loc):
        start_time = perf_counter()
        button_arr = []
        batchsequence_arr = []


        self.refresh()
        self.logger.info(f"Exporting form {formname}")
        if export_loc not in self.var_dict:
            self.alert(f"Pipeline path not set in variables, please set it")
            return
        path = self.var_dict[export_loc] + "/db_forms"
        if not os.path.exists(path):
            self.alert(f"Pipeline path {path} does not exist")
            return
        if not os.path.isdir(path):
            self.alert(f"Pipeline path {path} is not a directory")
            return
        if not os.access(path, os.W_OK):
            self.alert(f"Pipeline path {path} is not writable")
            return
        if not os.access(path, os.R_OK):
            self.alert(f"Pipeline path {path} is not readable")
            return

        #strip special symbols frin tab["formname"] an  tab["tab"] to be able to use as filename


        form_clean = "".join(c for c in formname if c.isalnum() or c in ("_", "-"))
        
        filename = form_clean + ".json"


       
        
        forms_q = self.readsql(select("*").where(forms.formname == formname), one=True)
        forms_dict = dict(forms_q._mapping)

        tabs_q = self.readsql(select("*").where(tabs.formname == formname))
        tabs_dict = [dict(tab._mapping) for tab in tabs_q]

        buttons_q = self.readsql(select("*").where(buttons.formname == formname))
        buttons_dict = [dict(button._mapping) for button in buttons_q]

        batchsequence_q = self.readsql(select("*").where(batchsequence.formname == formname))
        batchsequence_dict = [dict(batchseq._mapping) for batchseq in batchsequence_q]

        buttonseries_q = self.readsql(select("*").where(buttonseries.formname == formname))
        buttonseries_dict = [dict(buttonseries._mapping) for buttonseries in buttonseries_q]
        
        

        final_dict = {"forms":forms_dict, "tabs":tabs_dict, "buttons":buttons_dict, "batchsequence":batchsequence_dict, "buttonseries":buttonseries_dict}


        with open(path + "/" + filename, "w") as f:
            json.dump(final_dict, f, indent=4)
        end_time = perf_counter()
        self.logger.success(f"Exported form {formname} to {path}/{filename} in {round((end_time-start_time),2)} seconds")


##other functions#############################################################################################################

    def get_forms(self):
        return self.readsql(select(forms.formname, forms.formdesc).order_by(forms.formname.asc()))
        

    def add_form(self, form_name, curtab, curform):
        x = self.writesql(insert(forms).values(formname = form_name, formdesc = ""))
        if not x:
            self.alert(f"Form {form_name} already exists")
            return False
        #add button called open {form} 



        x = self.writesql(insert(tabs).values(formname = form_name, tab = form_name))
        if not x:
            self.alert("Error adding tab")
            return False

        x = self.writesql(insert(buttons).values(formname = curform, tab = curtab, buttonname = form_name))
        if not x:
            self.alert(f"Button {'open form' + form_name} already exists")
            return False
        x = self.writesql(insert(batchsequence).values(formname = curform, tab = curtab, buttonname =form_name, type = "tabto", runsequence=0, folderpath=form_name, filename=form_name))

        if not x:
            self.alert("Error adding batchsequence")
            return False

        self.gui_refresh()

    def add_tabto(self,  tabto, form, tab_name, old_form):
        buttonname = f"{form}|{tabto}"
        q = self.writesql(insert(buttons).values(formname = old_form, tab = tab_name, buttonname = buttonname,  buttondesc=f"tabto form:{form} | tab:{tabto}", columnnum = 0, buttonsequence = 0))
        if not q:
            self.alert(f"Error adding button {tabto} to {tab_name} in {form}")
            return
        q = self.writesql(insert(batchsequence).values(formname = old_form, tab = tab_name, buttonname = buttonname,  folderpath = form, runsequence=0, filename=tabto, type = "tabto"))
        if not q:
            self.alert(f"Error adding batchsequence {tabto} to {tab_name} in {form}")
            return
        self.gui_refresh()

    def add_tablast(self, tablast, tab_name, form):
        q = self.writesql(insert(buttons).values(formname = form, tab = tab_name, buttonname = tablast, columnnum = 0, buttonsequence = 0))
        if not q:
            self.alert(f"Error adding button {tablast} to {tab_name} in {form}")
            return
        q = self.writesql(insert(batchsequence).values(formname = form, tab = tab_name, buttonname = tablast, runsequence=0, filename=tablast, type = "tablast"))
        if not q:
            self.alert(f"Error adding batchsequence {tablast} to {tab_name} in {form}")
            return
        self.gui_refresh()

    
    def add_tab_url(self, tab_name, url, form):
        if url == None:
            return
        q = self.writesql(update(tabs).where(tabs.tab == tab_name).where(tabs.formname == form).values(taburl = url))
        if not q:
            self.writesql(insert(tabs).values(taburl = url, tab = tab_name, formname = form))
        self.gui_refresh()
    
    def add_tab_folder(self, tab_name, folder, form):
        if folder == None:
            return
        q = self.writesql(update(tabs).where(tabs.tab == tab_name).where(tabs.formname == form).values(treepath = folder))
        if not q:
            self.writesql(insert(tabs).values(treepath = folder, tab = tab_name, formname = form))
            return
        self.gui_refresh()

    def add_tab(self, tab_name, form):
        q = self.writesql(insert(tabs).values(tab = tab_name, formname = form))
        if not q:
            self.alert(f"Error adding tab {tab_name} to form {form}")
            return
        self.gui_refresh()
    
    def button_map(self):
        form_data = self.readsql(select(forms.formname).order_by(forms.formname.asc()))
        
        tab_data, button_data = self.read_mult( [select(tabs.formname, tabs.tab).where(tabs.formname.in_([form.formname for form in form_data])).order_by(tabs.formname.asc(), tabs.tabsequence.asc()),
                                    select(buttons.formname, buttons.tab, buttons.buttonname).where(buttons.formname.in_([form.formname for form in form_data])).order_by(buttons.formname.asc(), buttons.tab.asc())])

        dict_struct = {}
        dict_struct["button_data"]        = [dict(item._mapping) for item in button_data]
        dict_struct["form_data"]          = [dict(item._mapping) for item in form_data]
        dict_struct["tab_data"]           = [dict(item._mapping) for item in tab_data]

        layered_dict = {}
        for form in dict_struct["form_data"]:
            layered_dict[form["formname"]] = {}
            for tab in dict_struct["tab_data"]:
                if tab["formname"] == form["formname"]:
                    layered_dict[form["formname"]][tab["tab"]] = {}
                    for button in dict_struct["button_data"]:
                        if button["formname"] == form["formname"] and button["tab"] == tab["tab"]:
                            layered_dict[form["formname"]][tab["tab"]][button["buttonname"]] = button
        return(layered_dict)

    def add_description(self, description, tab):
        curtab = tab
        buttonname = str(description)
        buttonseq = "0"
        columnum = "0"
        #write to buttons table
        button_insert_dict = {"formname": self.title, "tab": curtab, "buttonname": buttonname, "buttonsequence": buttonseq, "columnnum": columnum}
        batchsequence_insert_dict = {"formname": self.title, "tab": curtab, "buttonname": buttonname, "type": "."}
        q = self.writesql(insert(buttons).values(**button_insert_dict))
        if not q:
            self.alert(f"Error adding button {buttonname} to tab {curtab} in form {self.title}")
            return

        q = self.writesql(insert(batchsequence).values(**batchsequence_insert_dict))
        if not q:
            self.alert(f"Error adding batchsequence {buttonname} to tab {curtab} in form {self.title}")
            return
        self.gui_refresh()

    def update_tab_size(self, tab, width, height):
        size = f"{width},{height}"
        form = self.title
        q = self.writesql(update(tabs).where(tabs.formname == form).where(tabs.tab == tab).values(**{"tabsize": size}))
        if not q:
            self.alert(f"Error updating tab size for tab {tab} in form {form}")
            return
        self.gui_refresh()

##edit button Functions#######################################################################################################

    def load_edit_button(self):
        self.edit_button = Edit_Button( self.readsql, self.writesql, self.logger,  self.alert, self.title, self.edit_sequence.edit_sequence_data)


    def edit_button_data(self, button_name, tab_name):
        return self.edit_button.edit_button_data(button_name, tab_name)

    def edit_button_update(self, original_data : dict, batchsequence_new : dict, button_new : dict):
        tab, buttonname = self.edit_button.edit_button_update(original_data, batchsequence_new, button_new)
        self.gui_refresh()
        self.gui.signal_button_complete.emit(tab, buttonname )

    def edit_button_delete(self, data : dict):
        self.edit_button.edit_button_delete(data)
        self.gui_refresh()

##edit tab Functions########################################################################################################
    def edit_tab_delete(self,  tab_name, form_name):
        self.edit_tab.edit_tab_delete(tab_name, form_name)
        self.gui_refresh()

    def edit_tab_update(self, tab_name, form_name, data, overwrite = False):
        self.edit_tab.edit_tab_update(tab_name, form_name, data, overwrite)
        self.gui_refresh()

##edit sequence Functions####################################################################################################
    def edit_sequence_load(self):
        self.edit_sequence = Edit_Sequence( self.readsql, self.writesql, self.logger,  self.alert, self.title)

    def edit_sequence_data(self, button_name, tab_name, source):
        return self.edit_sequence.edit_sequence_data(button_name, tab_name, source)
        
    def edit_sequence_update(self, data, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):
        current_tab, current_name = self.edit_sequence.edit_sequence_update(data, buttons_table_dict, batchsequence_table_dict, button_series_table_dict)
        self.gui.signal_button_complete.emit(current_tab, current_name)
        self.gui_refresh()
        
    def edit_sequence_save(self, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):
        self.edit_sequence.edit_sequence_save(buttons_table_dict, batchsequence_table_dict, button_series_table_dict)
        self.gui_refresh()

    def edit_sequence_delete(self, data_dict):
        self.edit_sequence.edit_sequence_delete(data_dict)
        self.gui_refresh()

##edit layout Functions######################################################################################################      
    def edit_layout_save(self, data):
        self.logger.info(f'Saving layout data for form "{self.title}"')  #[button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc]
        for tab, tab_data in data.items():


            for button in tab_data["buttons"]:
                #update values buttons.buttonsequence  = button[0], buttons.columnnum = button[1]
                q = self.writesql(update(buttons).where(buttons.buttonname == button[1]).where(buttons.tab == tab).where(buttons.formname == self.title).values(buttonsequence = button[0], columnnum = button[2]))
                if not q:
                    self.alert(f"Error updating button on tab {tab} in form {self.title}")
                    return
            #delete buttons from tab_data
            tab_data_fresh = tab_data.copy()
            #get all keys from tabs
            tab_keys =[column.key for column in tabs.__table__.columns]
            #remove key from tab_data_fresh that are not tab_keys
            for key in tab_data_fresh.copy().keys():
                if key not in tab_keys:
                    del tab_data_fresh[key]

            
            #update values for tab
            q = self.writesql(update(tabs).where(tabs.tab == tab).where(tabs.formname == self.title).values(**tab_data_fresh))
            if not q:
                self.alert(f"Error updating tab {tab} in form {self.title}")

##Add Action Functions#######################################################################################################
    def create_process_insert(self, batchsequence_dict, buttons_dict):
        self.logger.info(f'Inserting process data for form "{self.title}"')
        batchsequence_dict["runsequence"] = 0
        q = self.writesql(insert(batchsequence).values(**batchsequence_dict))
        if not q:
            self.alert(f"Error inserting process on tab {batchsequence_dict['tab']} in form {batchsequence_dict['formname']}")
            return
        q = self.writesql(insert(buttons).values(**buttons_dict))
        if not q:
            self.alert(f"Error inserting process on tab {buttons_dict['tab']} in form {buttons_dict['formname']}")
            return


##Copy tab functions#########################################################################################################
    def copy_tab_data(self):
        tabs_data = self.readsql(select(tabs.formname, tabs.tab))
        forms_data = self.readsql(select(forms.formname))
        tabs_data = [dict(item._mapping) for item in tabs_data]
        forms_data = [dict(item._mapping) for item in forms_data]
        data = {}
        for items in forms_data:
            data[items["formname"]] = []

        for items in tabs_data:
            if items["formname"] in data:
                data[items["formname"]].append(items["tab"])
        forms_array = []
        for items in forms_data:
            forms_array.append(items["formname"])   
        return forms_array , data

    def copy_tab_insert(self, new_tab, new_form, old_tab, old_form):
        #readsql = self.readsql(select(tabs.formname, tabs.tab))
        #insert into tabs the current tab but with new formname and new tabname
        #tabs ddl: CREATE TABLE "tabs" ("formname" char (63),  "tab" char (63),  "tabsequence" INTEGER,  "grid" INTEGER,  "tabdesc" TEXT,  "treepath" CHAR (1023),  "tabgroup" CHAR (63),  "tabsize" INTEGER,  "taburl" TEXT,  PRIMARY KEY ("formname", "tab"));
        tab_cur = self.readsql(select("*").where(tabs.formname == old_form).where(tabs.tab == old_tab))[0]
        tab_cur = dict(tab_cur._mapping)
        tab_cur["formname"] = new_form
        tab_cur["tab"] = new_tab
        q = self.writesql(insert(tabs).values(**tab_cur))
        if not q:
            self.alert(f"Error inserting tab {new_tab} in form {new_form}")
            return

        button_cur = self.readsql(select("*").where(buttons.tab == old_tab).where(buttons.formname == old_form))
        button_cur = [dict(item._mapping) for item in button_cur]
        for button in button_cur:
            button["tab"] = new_tab
            button["formname"] = new_form
            q = self.writesql(insert(buttons).values(**button))
            if not q:
                self.alert(f"Error inserting button {button['buttonname']} in form {new_form}")
                return


        series_oldnew = []
        batchsequence_cur = self.readsql(select("*").where(batchsequence.tab == old_tab).where(batchsequence.formname == old_form))
        batchsequence_cur = [dict(item._mapping) for item in batchsequence_cur]
        for batchsequence_ in batchsequence_cur:
            batchsequence_["tab"] = new_tab
            batchsequence_["formname"] = new_form
            if batchsequence_["type"] == "assignseries":
                while True:
                    series = batchsequence_["source"]
                    new_series = series + "_" + str(randint(1000,10000))
                    if not self.readsql(select(buttonseries).where(buttonseries.assignname == new_series).where(buttonseries.formname == old_form)):
                        series_oldnew.append([series, new_series])
                        batchsequence_["source"] = new_series
                        break
            q = self.writesql(insert(batchsequence).values(**batchsequence_))
            if not q:
                self.alert(f"Error inserting batchsequence {batchsequence_['batchsequence']} in form {new_form}")
                return
        for series in series_oldnew:
            old_series = series[0]
            new_series = series[1] 
            #copy old series
            series_cur = self.readsql(select("*").where(buttonseries.assignname == old_series).where(buttonseries.formname == old_form))
            series_cur = [dict(item._mapping) for item in series_cur]
            for series_ in series_cur:
                series_["assignname"] = new_series
                series_["formname"] = new_form
                if series_["tab"] == old_tab:
                    series_["tab"] = new_tab
                q = self.writesql(insert(buttonseries).values(**series_))
                if not q:
                    self.alert(f"Error inserting series {series_['assignname']} in form {new_form}")
                    return
        if new_form == old_form:
            self.gui_refresh()

        
        """
        buttonseries_cur = self.readsql(select("*").where(buttonseries.formname == old_form).where(buttonseries.tab == old_tab))
        buttonseries_cur = [dict(item._mapping) for item in buttonseries_cur]
        for buttonseries_ in buttonseries_cur:
            buttonseries_["formname"] = new_form
            buttonseries_["tab"] = new_tab
            q = self.writesql(insert(buttonseries).values(**buttonseries_))
            if not q:
                self.alert(f"Error inserting buttonseries {buttonseries_['buttonseries']} in form {new_form}")
                return
        self.gui_refresh()
        """      

    def move_tab_insert(self, new_tab, new_form, old_tab, old_form):
        q = self.writesql(update(tabs).where(tabs.formname == old_form).where(tabs.tab == old_tab).values(formname = new_form, tab = new_tab))
        if not q:
            self.alert(f"Error moving tab {old_tab} in form {old_form}")
            return
        q = self.writesql(update(buttons).where(buttons.tab == old_tab).where(buttons.formname == old_form).values(tab = new_tab, formname = new_form))
        if not q:
            self.alert(f"Error moving button {old_tab} in form {old_form}")
            return
        q = self.writesql(update(batchsequence).where(batchsequence.tab == old_tab).where(batchsequence.formname == old_form).values(tab = new_tab, formname = new_form))
        if not q:
            self.alert(f"Error moving batchsequence {old_tab} in form {old_form}")
            return
        q = self.writesql(update(buttonseries).where(buttonseries.formname == old_form).where(buttonseries.tab == old_tab).values(tab = new_tab, formname = new_form))
        if not q:
            self.alert(f"Error moving buttonseries {old_tab} in form {old_form}")
            return
        self.gui_refresh()


##Button Copy Functions######################################################################################################

    def copy_button_insert(self, old_form, old_tab, old_button, new_form, new_tab, new_button):
        button_cur = self.readsql(select("*").where(buttons.formname == old_form).where(buttons.tab == old_tab).where(buttons.buttonname == old_button))[0]
        button_cur = dict(button_cur._mapping)
        button_cur["formname"] = new_form
        button_cur["tab"] = new_tab
        button_cur["buttonname"] = new_button
        q = self.writesql(insert(buttons).values(**button_cur))
        if not q:
            self.alert(f"Error inserting button {new_button} in form {new_form}")
            return
        batchsequence_cur = self.readsql(select("*").where(batchsequence.formname == old_form).where(batchsequence.tab == old_tab).where(batchsequence.buttonname == old_button))
        batchsequence_cur = [dict(item._mapping) for item in batchsequence_cur]
        for batchsequence_ in batchsequence_cur:
            batchsequence_["formname"] = new_form
            batchsequence_["tab"] = new_tab
            batchsequence_["buttonname"] = new_button
            q = self.writesql(insert(batchsequence).values(**batchsequence_))
            if not q:
                self.alert(f"Error inserting batchsequence {batchsequence_['batchsequence']} in form {new_form}")
                return
        if new_form == self.title:
            self.gui_refresh()

    def move_button_insert(self, old_form, old_tab, old_button, new_form, new_tab, new_button):
        q = self.writesql(update(buttons).where(buttons.formname == old_form).where(buttons.tab == old_tab).where(buttons.buttonname == old_button).values(formname = new_form, tab = new_tab, buttonname = new_button))
        if not q:
            self.alert(f"Error moving button {old_button} in form {old_form}")
            return
        q = self.writesql(update(batchsequence).where(batchsequence.formname == old_form).where(batchsequence.tab == old_tab).where(batchsequence.buttonname == old_button).values(formname = new_form, tab = new_tab, buttonname = new_button))
        if not q:
            self.alert(f"Error moving batchsequence {old_button} in form {old_form}")
            return
        if new_form == self.title:
            self.gui_refresh()


class Loader:
    def __init__(self, gui, form = None):
        self.config = ConfigHandler(form)

        self.pmgr = PluginHandler(self.config.plugin_folder)
        self.logger = self.pmgr.return_logger()
        self.db = QueryHandler(self.logger, self.config.db_location)
        self.ui = UserInterfaceHandlerPyQT(self.logger, self.db, self.pmgr.pmgr, gui, self.config.form_name, self.config.variable_loc)
        self.formname = None


class Test:
    def __init__(self):
        self.form_break = False
        None
    
    def input(self, input_):
        self.logger.debug(f"asked for input: {input_}")
        if input_ == "createform":
            self.logger.warning("form not found")
            self.form_break = True
            return "n"
     
if __name__ == "__main__":
    backend = Loader(None, "TEST")
    backend.ui.formname = "test"
    a = backend.ui.load()
    b = backend.ui.refresh()
    assert a == ("test", "Exaut")
    assert b == (['test'], {'test': {'buttons': [[1, 'test', 1, None]], 'grid': 2, 'description': None, 'size': None}})

    edit_button_test, state = backend.ui.edit_button_data("test", "test")
    edit_button_test["form_data"] = ["test"]
    edit_button_test["tab_data"] = ["test"]
    assert edit_button_test == {'button_data': {'formname': 'test', 'tab': 'test', 'buttonname': 'test', 'buttonsequence': 1, 'columnnum': 1, 'buttondesc': None, 'buttongroup': None, 'active': None, 'treepath': None}, 'batchsequence_data': [{'formname': 'test', 'tab': 'test', 'buttonname': 'test', 'runsequence': None, 'folderpath': None, 'filename': None, 'type': 'test', 'source': None, 'target': None, 'databasepath': None, 'databasename': None, 'keypath': None, 'keyfile': None, 'treepath': None}], 'form_data': ["test"], 'tab_data': ["test"]}


    print("tests passed")
    backend = None
