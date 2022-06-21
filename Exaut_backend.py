from time import perf_counter

from psycopg2 import OperationalError

from Plugins import Plugins 
import sys
import os
from iniconfig import Parse
from Components.db.Exaut_sql import  forms, tabs, buttons, batchsequence, buttonseries, pluginmap
from sqlalchemy import create_engine,select, update, insert, delete
from sqlalchemy.orm import sessionmaker
from threading import Thread
from version import version
from random import randint
import time

class ConfigHandler:
    def __init__(self, logger, title=None):
        self.logger = logger
        self.file_config = None
        self.form_name = None
        self.title = title
        self.db_location = None

        self.load_data()

    def load_data(self):
        current_filename =  os.path.basename(sys.argv[0]).split(".")[0].upper()
        try:
            os.chdir(os.path.dirname(sys.argv[0]))
        except:
            self.logger.error("Could not change directory to %s" % os.path.dirname(sys.argv[0]))


        self.file_config = Parse(self.logger, current_filename).cfg
        self.logger.debug(f"filename: {current_filename} + filecfg_arr = {self.file_config}")
        if not self.file_config:
            self.logger.error(f"No [{current_filename}] header in config.ini")
            input()
            ###GUI_POPUP
            sys.exit()
        else:
            self.form_name = self.file_config["form"]
        
        db_config = Parse( self.logger,"SQLCONN").cfg
        connectionpath = db_config["connectionpath"]
        connection = db_config["connection"]
        self.db_location = f"{connectionpath}\\{connection}"
        
class PluginHandler():
    def __init__(self):
        self.pmgr = None

        self.load_data()

    def load_data(self):
        self.pmgr = Plugins()
        if self.pmgr.fail == True:
            print(f"Critical error, plugin manager failed to load")
            print(self.pmgr.error)
            sys.exit()
    def return_logger(self):
        x = self.pmgr.handlers["log"]["run"]
        return x

class QueryHandler():
    def __init__(self,logger, db_loc):
        self.logger = logger
        self.engine = create_engine(f'sqlite:///{db_loc}', echo=False, future=True)
        self.Session = sessionmaker(self.engine)
        
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
            

    

class UserInterfaceHandlerPyQT():
    def __init__(self, logger, db, pmgr, gui, formname):

        self.logger = logger
        self.readsql = db.readsql
        self.writesql = db.writesql
        self.pmgr = pmgr
        self.initial = True
        self.formname = formname
        self.gui = gui

        self.tab_buttons = {}
        self.tablist = []
        self.title = ""
        self.form_desc = ""
        self.version = version
        self.popups = self.Popups(self.gui, self.logger, self)
        self.handle_plugins()
        self.refresh(launch = True)
    def handle_plugins(self):
        plugin_map = self.pmgr.plugin_map
        for plugin, types in plugin_map.items():
            if type(types) == tuple:
                types = ",".join(types)
                plugin_map[plugin] = types
        #from pluginmap db get all plugins and types
        try:
            data = self.readsql(select([pluginmap.plugin, pluginmap.types]))
        except OperationalError as e:
            self.logger.error(f"Error reading pluginmap, please add table to db")
            self.logger.error(f"{e}")
            input("Press enter to exit")
            sys.exit()
        #print all items in db
        map_in_db = {}
        for item in data:
            map_in_db[item.plugin] = item.types
        
        for item in plugin_map:
            if item not in map_in_db:
                self.logger.info(f"Adding plugin {item} to db")
                self.writesql(insert(pluginmap).values(plugin=item, types=plugin_map[item], generated = 1))
            else:
                if plugin_map[item] != map_in_db[item]:
                    self.logger.info(f"Updating plugin {item} in db")
                    self.writesql(update(pluginmap).where(plugin = item).values(types=plugin_map[item], generated = 1))

        
            
            

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
            self.parent_.gui.signal_alert.emit(msg, title)
            return True
            
        def yesno(self, message, title="", default="no"):
            return self.call(self.gui.signal_popup_yesno,(message, title, default))


        def data_entry(self, message, title=""):
            return self.call(self.gui.signal_popup_data, (message, title))

       
            
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

        def tabto(self, tab):
            return self.call(self.gui.signal_popup_tabto, (tab))

    def user_input(self, input_):
        return input(input_)

    def alert(self, message, title = None):
        self.logger.info(message)
        self.gui.alert(message, title)


    def gui_refresh(self):
        self.gui.signal_refresh.emit()

    def refresh(self, launch = False):

        tab_info = self.readsql(select('*').where(tabs.formname == self.formname).order_by(tabs.tabsequence.asc()))
        self.buttondata = self.readsql(select('*').where(buttons.formname == self.formname).order_by(buttons.buttonsequence.asc()))
        #select type for button in buttondata and append to buttondata
        newbuttondata = []
        types_ = self.readsql(select(batchsequence.type, batchsequence.tab, batchsequence.buttonname).where(batchsequence.formname == self.formname))
        types_ = [dict(item._mapping) for item in types_]

        colors = self.readsql(select(pluginmap.types, pluginmap.color))
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
                if newbutton["buttonname"] == type_["buttonname"] and newbutton["tab"] == type_["tab"]:
                    newbutton["type"] = type_["type"]
                    if type_["type"] in colors_dict:
                        newbutton["color"] = colors_dict[type_["type"]]
                    else:
                        self.logger.warning(f"Type: {type_['type']} not found in pluginmap.")
                        colors_dict[type_["type"]] = None
                        newbutton["color"] = None
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
            inpt = self.user_input("createform")
            if inpt == "y":
                inpt = self.user_input("createform_desc")
                if inpt:
                    self.writesql(insert(forms).values(forms.formdesc == inpt, forms.formname == self.formname))
                    form_desc = inpt
        self.title = str(form_title)
        self.form_desc = str(form_desc)
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
                    sequence_thread = Thread(target=self.assignseries_handler, args=(self.logger, self.button_click, self.readsql,  button_name, tab_name, batchsequence_))
                    sequence_thread.start()
                    return
                elif self.pmgr.exists(batchsequence_.type):
                    if mode == "sequence":
                        return self.pmgr.call(batchsequence_.type, batchsequence_._mapping, self.popups), batchsequence_.type
                    function = self.pmgr.call, (batchsequence_.type, batchsequence_._mapping, self.popups)
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







##Popup Functions#############################################################################################################

##other functions#############################################################################################################


    def add_tabto(self, tabto, tab_name, form):
        q = self.writesql(insert(buttons).values(formname = form, tab = tab_name, buttonname = tabto, columnnum = 0, buttonsequence = 0))
        if not q:
            self.alert(f"Error adding button {tabto} to {tab_name} in {form}")
            return
        q = self.writesql(insert(batchsequence).values(formname = form, tab = tab_name, buttonname = tabto, runsequence=0, filename=tabto, type = "tabto"))
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
        
        form_data = self.readsql(select(forms.formname).order_by(forms.formname.asc()), timer=True)

        tab_data = self.readsql(select(tabs.formname, tabs.tab).where(tabs.formname.in_([form.formname for form in form_data])).order_by(tabs.formname.asc(), tabs.tabsequence.asc()),timer=True)
        button_data = self.readsql(select(buttons.formname, buttons.tab, buttons.buttonname).where(buttons.formname.in_([form.formname for form in form_data])).order_by(buttons.formname.asc(), buttons.tab.asc()),timer=True)
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
    def edit_button_data(self, button_name, tab_name):
        self.logger.info(f"Constructing data for edit button {button_name} on tab {tab_name} in form {self.title}")
        button_data = self.readsql(select("*").where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == self.title), one=True)
        batchsequence_data = self.readsql(select("*").where(batchsequence.buttonname == button_name).where(batchsequence.tab == tab_name).where(batchsequence.formname == self.title))
        #if batchsequence_data None:
        form_data = self.readsql(select(forms.formname).order_by(forms.formname.asc()))
        tab_data = self.readsql(select(tabs.formname, tabs.tab).where(tabs.formname.in_([form.formname for form in form_data])).order_by(tabs.formname.asc(), tabs.tabsequence.asc()))

        dict_struct = {}
        dict_struct["button_data"]        = dict(button_data._mapping)
        dict_struct["batchsequence_data"] = [dict(item._mapping) for item in batchsequence_data] 
        dict_struct["form_data"]          = [dict(item._mapping) for item in form_data]
        dict_struct["tab_data"]           = [dict(item._mapping) for item in tab_data]

        if len(batchsequence_data) == 0:
            self.logger.warning(f"No batchsequence data found for button: {button_name} on tab: {tab_name} in form: {self.title}")
            return(dict_struct, False)
            
        if batchsequence_data[0].type == "assignseries":
            sequence_data, state = self.edit_sequence_data(button_name, tab_name, batchsequence_data[0].source)
            if not state:
                self.alert(F"No assignseries data found for {button_name} on tab {tab_name} in form {self.title}")
            sequence_data["current_batch"] = dict_struct["batchsequence_data"][0]
            dict_struct = {"edit": dict_struct, "sequence": sequence_data}
        else:
            state = "button"
        return(dict_struct, state)

    def edit_button_update(self, original_data : dict, batchsequence_new : dict, button_new : dict):
        if "edit" in original_data:
            original_data = original_data["edit"]
        button = original_data["button_data"]
        q = self.writesql(update(buttons).where(buttons.buttonname == button["buttonname"]).where(buttons.tab == button["tab"]).where(buttons.formname == self.title).values(**button_new))
        if not q:
            self.alert(f"Error updating button {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return
        q = self.writesql(update(batchsequence).where(batchsequence.buttonname == button["buttonname"]).where(batchsequence.tab == button["tab"]).where(batchsequence.formname == self.title).values(**batchsequence_new))
        if not q:
            self.alert(f"Error updating batchsequence {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return

        q = self.writesql(update(buttonseries).where(buttonseries.buttonname == button["buttonname"]).where(buttonseries.tab == button["tab"]).where(buttonseries.formname == self.title).values((buttonseries.buttonname == button["buttonname"],buttonseries.tab == button["tab"],buttonseries.formname == self.title)))
        if not q:
            self.alert(f"Error updating buttonseries {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return

        self.gui_refresh()
        self.gui.signal_button_complete.emit(button["tab"], button["buttonname"])
    
    def edit_button_delete(self, data : dict):
        if "edit" in data:
            data = data["edit"]
        button = data["button_data"]

        q = self.writesql(delete(buttons).where(buttons.buttonname == button["buttonname"]).where(buttons.tab == button["tab"]).where(buttons.formname == self.title))
        if not q:
            self.alert(f"Error deleting button {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return
        
        q = self.writesql(delete(batchsequence).where(batchsequence.buttonname == button["buttonname"]).where(batchsequence.tab == button["tab"]).where(batchsequence.formname == self.title))
        if not q:
            self.alert(f"Error deleting batchsequence {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return
        
        q = self.writesql(delete(buttonseries).where(buttonseries.buttonname == button["buttonname"]).where(buttonseries.tab == button["tab"]).where(buttonseries.formname == self.title))
        if not q:
            self.alert(f"Error deleting buttonseries {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return

        self.gui_refresh()

##edit tab Functions########################################################################################################
    def edit_tab_delete(self, tab_name, form_name):
        print(tab_name)
        print(form_name)
        q = self.writesql(delete(tabs).where(tabs.tab == tab_name).where(tabs.formname == form_name))
        if not q:
            self.alert(f"Error deleting tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(buttons).where(buttons.tab == tab_name).where(buttons.formname == form_name))
        if not q:
            self.alert(f"Error deleting buttons on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(batchsequence).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name))
        if not q:
            self.alert(f"Error deleting batchsequence on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(buttonseries).where(buttonseries.tab == tab_name).where(buttonseries.formname == form_name))
        if not q:
            self.alert(f"Error deleting buttonseries on tab {tab_name} in form {form_name}")
            return
        self.gui_refresh()

    def edit_tab_update(self, tab_name, form_name, data):
        new_tab_name = data["tab"]
        q = self.writesql(update(tabs).where(tabs.tab == tab_name).where(tabs.formname == form_name).values(**data))
        if not q:
            self.alert(f"Error updating tab {tab_name} in form {form_name}")
            return
        q = self.writesql(update(buttons).where(buttons.tab == tab_name).where(buttons.formname == form_name).values(**{"tab": new_tab_name}))
        if not q:
            self.alert(f"Error updating buttons on tab {tab_name} in form {form_name}")
            return

        q = self.writesql(update(batchsequence).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name).values(**{"tab": new_tab_name}))
        if not q:
            self.alert(f"Error updating batchsequence on tab {tab_name} in form {form_name}")
            return

        q = self.writesql(update(buttonseries).where(buttonseries.tab == tab_name).where(buttonseries.formname == form_name).values(**{"tab": new_tab_name}))
        if not q:
            self.alert(f"Error updating buttonseries on tab {tab_name} in form {form_name}")
            return
        self.gui_refresh()

##edit sequence Functions####################################################################################################
    def edit_sequence_data(self, button_name, tab_name, source):
        self.logger.info(f'Constructing data for edit sequence "{button_name}" on tab "{tab_name}" in form "{self.title}"')
        buttonseries_data = self.readsql(select(buttonseries.formname, buttonseries.tab, buttonseries.buttonname).where(buttonseries.assignname == source).where(buttonseries.formname == self.title).order_by(buttonseries.runsequence.asc()))
        current_button = self.readsql(select("*").where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == self.title), one=True)
        if len(buttonseries_data) == 0:
            self.logger.warning(f"No buttonseries data found for button: {button_name} on tab: {tab_name} in form: {self.title}")

        dict_struct = {}
        dict_struct["buttonseries_data"] = [dict(item._mapping) for item in buttonseries_data]
        dict_struct["current_button"] = dict(current_button._mapping)
        state = "sequence"
        return(dict_struct, state) 
        
    def edit_sequence_update(self, data, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):
        current_button = data["edit"]["button_data"]
        current_tab = current_button["tab"]
        current_form = current_button["formname"]
        current_name = current_button["buttonname"]
        current_assignname = data["sequence"]["current_batch"]["source"]

        if buttons_table_dict["buttonname"] != current_name:
            q = self.writesql(update(buttons).where(buttons.buttonname == current_name).where(buttons.tab == current_tab).where(buttons.formname == current_form).values(buttonname = buttons_table_dict["buttonname"]))
            if not q:
                self.alert(f"Error updating buttonname on tab {current_tab} in form {current_form}")
                return
            q = self.writesql(update(batchsequence).where(batchsequence.buttonname == current_name).where(batchsequence.tab == current_tab).where(batchsequence.formname == current_form).values(buttonname = buttons_table_dict["buttonname"]))
            if not q:
                self.alert(f"Error updating buttonname on tab {current_tab} in form {current_form}")
                return
        #delete all buttonseries data for this button
        q = self.writesql(delete(buttonseries).where(buttonseries.assignname == current_assignname))
        if not q:
            self.alert(f"Error deleting buttonseries on tab {current_tab} in form {current_form}")
            return
        #insert new buttonseries data

        for button_series in button_series_table_dict:
            button_series["formname"] = current_form
            q = self.writesql(insert(buttonseries).values(**button_series))
            if not q:
                self.alert(f"Error inserting buttonseries on tab {current_tab} in form {current_form}")
                return
        self.gui.signal_button_complete.emit(current_tab, current_name)
        self.gui_refresh()
        
    def edit_sequence_save(self, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):




        q = self.writesql(insert(buttons).values(**buttons_table_dict))
        if not q:
            self.alert(f"Error inserting button on tab {buttons_table_dict['tab']} in form {buttons_table_dict['formname']}")
            return
        q = self.writesql(insert(batchsequence).values(**batchsequence_table_dict))
        if not q:
            self.alert(f"Error inserting batchsequence on tab {batchsequence_table_dict['tab']} in form {batchsequence_table_dict['formname']}")
            return


        for button_series in button_series_table_dict:
            q = self.writesql(insert(buttonseries).values(**button_series))
            if not q:
                self.alert(f"Error inserting buttonseries on tab {button_series['tab']} in form {button_series['formname']}")
                return
        self.gui_refresh()

    def edit_sequence_delete(self, data_dict):
        button_name = data_dict["current_button"]["buttonname"]
        tab_name = data_dict["current_button"]["tab"]
        form_name = data_dict["current_button"]["formname"]

        assignname = data_dict["current_batch"]["source"]

        q = self.writesql(delete(buttons).where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == form_name))
        if not q:
            self.alert(f"Error deleting button on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(batchsequence).where(batchsequence.buttonname == button_name).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name))
        if not q:
            self.alert(f"Error deleting batchsequence on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(buttonseries).where(buttonseries.formname == form_name).where(buttonseries.assignname == assignname))
        if not q:
            self.alert(f"Error deleting buttonseries on tab {tab_name} in form {form_name}")
            return
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

        batchsequence_cur = self.readsql(select("*").where(batchsequence.tab == old_tab).where(batchsequence.formname == old_form))
        batchsequence_cur = [dict(item._mapping) for item in batchsequence_cur]
        for batchsequence_ in batchsequence_cur:
            batchsequence_["tab"] = new_tab
            batchsequence_["formname"] = new_form
            q = self.writesql(insert(batchsequence).values(**batchsequence_))
            if not q:
                self.alert(f"Error inserting batchsequence {batchsequence_['batchsequence']} in form {new_form}")
                return

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
        print(old_form, old_tab, old_button, new_form, new_tab, new_button)
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
#############################################################################################################################




















class Loader:
    def __init__(self, gui):
        self.pmgr = PluginHandler()
        self.logger = self.pmgr.return_logger()
        self.config = ConfigHandler(self.logger, "EXAUT_IAN")
        self.db = QueryHandler(self.logger, self.config.db_location)
        self.ui = UserInterfaceHandlerPyQT(self.logger, self.db, self.pmgr.pmgr, gui, self.config.form_name)
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
    backend = Loader(None)
    backend.ui.formname = "test"
    a = backend.ui.load()
    b = backend.ui.refresh()
    assert a == ("test", "test")
    assert b == (['test'], {'test': {'buttons': [[1, 'test', 1, None]], 'grid': 2, 'description': None, 'size': None}})

    edit_button_test, state = backend.ui.edit_button_data("test", "test")
    edit_button_test["form_data"] = ["test"]
    edit_button_test["tab_data"] = ["test"]
    assert edit_button_test == {'button_data': {'formname': 'test', 'tab': 'test', 'buttonname': 'test', 'buttonsequence': 1, 'columnnum': 1, 'buttondesc': None, 'buttongroup': None, 'active': None, 'treepath': None}, 'batchsequence_data': [{'formname': 'test', 'tab': 'test', 'buttonname': 'test', 'runsequence': None, 'folderpath': None, 'filename': None, 'type': 'test', 'source': None, 'target': None, 'databasepath': None, 'databasename': None, 'keypath': None, 'keyfile': None, 'treepath': None}], 'form_data': ["test"], 'tab_data': ["test"]}


    print("tests passed")
    backend = None





