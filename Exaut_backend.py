from time import perf_counter
from Plugins import Plugins 
from loguru import logger
import sys
import os
from iniconfig import Parse
from Components.db.Exaut_sql import  forms, tabs, buttons, batchsequence, buttonseries
from sqlalchemy import create_engine,select, update, insert, delete
from sqlalchemy.orm import sessionmaker
from threading import Thread
from version import version
from random import randint


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
        if self.title != None:
            current_filename = self.title
        self.file_config = Parse(current_filename).cfg
        logger.debug(f"filename: {current_filename} + filecfg_arr = {self.file_config}")
        if not self.file_config:
            logger.error(f"No [{current_filename}] header in config.ini")
            ###GUI_POPUP
            sys.exit()
        else:
            self.form_name = self.file_config["form"]
        
        db_config = Parse("SQLCONN").cfg
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
            logger.error(f"Critical error, plugin manager failed to load")
            logger.error(self.pmgr.error)
            sys.exit()
    def return_logger(self):
        return logger
  
class QueryHandler():
    def __init__(self,logger, db_loc):
        self.logger = logger
        self.engine = create_engine(f'sqlite:///{db_loc}', echo=False, future=True)
        self.Session = sessionmaker(self.engine)
        
    def readsql(self, query, one=False, log = False):
        if log:
            self.logger.info(query.compile(dialect=self.engine.dialect))
        with self.Session.begin() as session:
            if one == True:
                return session.execute(query).first()
            else:
                return session.execute(query).all()
    
    def writesql(self, query, log = False):
        if log:
            self.logger.info(query.compile(dialect=self.engine.dialect))
        with self.Session.begin() as session:
            session.execute(query)

    

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
        self.popups = self.Popups(self.gui, self.logger)

    class Popups:
        def __init__(self, gui, logger):
            self.gui =  gui
            self.logger = logger

        def random(self):
            while True:
                x = randint(0, 9999999999)
                if x not in self.gui.popup_msgs:
                    return x

        def yesno(self, message, title="", default="no"):
            return self.call(self.gui.signal_popup_yesno.emit,(message, title, default))


        def data_entry(self, message, title=""):
            return self.call(self.gui.signal_popup_data, (message, title))
            
        def call(self, signal, args):
            key = str(self.random())
            signal.emit(key, *args)
            while key not in self.gui.popup_msgs:
                None
            res = self.gui.popup_msgs[key]
            del self.gui.popup_msgs[key]
            return res

    def user_input(self, input_):
        return input(input_)

    def alert(self, message):
        self.logger.info(message)
        self.gui.alert(message)

    def gui_refresh(self):
        self.gui.signal_refresh.emit()

    def refresh(self):
        tab_info = self.readsql(select(tabs.tab, tabs.grid, tabs.tabdesc, tabs.tabsize).where(tabs.formname == self.formname).order_by(tabs.tabsequence.asc()))
        self.buttondata = self.readsql(select('*').where(buttons.formname == self.formname).order_by(buttons.buttonsequence.asc()))

        buttons_data_ordered = self.buttondata.copy()
        buttons_tabs = {}
        for tab in tab_info:
            tab_name = tab.tab
            grid = tab.grid
            description = tab.tabdesc
            size = tab.tabsize
            buttons_tabs[tab_name] = {}
            buttons_tabs[tab_name]["buttons"] = []
            buttons_tabs[tab_name]["grid"] = grid
            buttons_tabs[tab_name]["description"] = description
            buttons_tabs[tab_name]["size"] = size
        #order buttons by item.columnum asc
        buttons_data_ordered.sort(key=lambda button: int(button.columnnum) if button.columnnum not in ("", None) else -5)
        for button in buttons_data_ordered:
            if button.tab not in buttons_tabs:
                buttons_tabs[button.tab] = {}
                buttons_tabs[button.tab]["buttons"] = []
            buttons_tabs[button.tab]["buttons"].append([button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc])
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
                    sequence_thread = Thread(target=self.assignseries_handler, args=(logger, self.button_click, self.readsql,  button_name, tab_name, batchsequence_))
                    sequence_thread.start()
                    return
                elif self.pmgr.exists(batchsequence_.type):
                    if mode == "sequence":
                        return self.pmgr.call(batchsequence_.type, batchsequence_._mapping, self.popups), batchsequence_.type
                    button_thread = Thread(target=self.pmgr.call, args=(batchsequence_.type, batchsequence_._mapping, self.popups))
                    button_thread.start()
                    

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
        logger.success(f"completed button sequence {original_button_name} in {round((endtime-ctime),2)} seconds") 

##Popup Functions#############################################################################################################
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
        self.writesql(update(buttons).where(buttons.buttonname == button["buttonname"]).where(buttons.tab == button["tab"]).where(buttons.formname == self.title).values(**button_new))
        self.writesql(update(batchsequence).where(batchsequence.buttonname == button["buttonname"]).where(batchsequence.tab == button["tab"]).where(batchsequence.formname == self.title).values(**batchsequence_new))
        self.writesql(update(buttonseries).where(buttonseries.buttonname == button["buttonname"]).where(buttonseries.tab == button["tab"]).where(buttonseries.formname == self.title).values((buttonseries.buttonname == button["buttonname"],buttonseries.tab == button["tab"],buttonseries.formname == self.title)))
        self.gui_refresh()
    
    def edit_button_delete(self, data : dict):
        if "edit" in data:
            data = data["edit"]
        button = data["button_data"]
        self.writesql(delete(buttons).where(buttons.buttonname == button["buttonname"]).where(buttons.tab == button["tab"]).where(buttons.formname == self.title))
        self.writesql(delete(batchsequence).where(batchsequence.buttonname == button["buttonname"]).where(batchsequence.tab == button["tab"]).where(batchsequence.formname == self.title))
        self.writesql(delete(buttonseries).where(buttonseries.buttonname == button["buttonname"]).where(buttonseries.tab == button["tab"]).where(buttonseries.formname == self.title))
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
            self.writesql(update(buttons).where(buttons.buttonname == current_name).where(buttons.tab == current_tab).where(buttons.formname == current_form).values(buttonname = buttons_table_dict["buttonname"]))
            self.writesql(update(batchsequence).where(batchsequence.buttonname == current_name).where(batchsequence.tab == current_tab).where(batchsequence.formname == current_form).values(buttonname = buttons_table_dict["buttonname"]))

        #delete all buttonseries data for this button
        self.writesql(delete(buttonseries).where(buttonseries.assignname == current_assignname))
        #insert new buttonseries data

        for button_series in button_series_table_dict:
            button_series["formname"] = current_form
            self.writesql(insert(buttonseries).values(**button_series))
        self.gui_refresh()

    def edit_sequence_save(self, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):




        self.writesql(insert(buttons).values(**buttons_table_dict))
        self.writesql(insert(batchsequence).values(**batchsequence_table_dict))


        for button_series in button_series_table_dict:
            self.writesql(insert(buttonseries).values(**button_series))
        self.gui_refresh()

    def edit_sequence_delete(self, data_dict):
        button_name = data_dict["current_button"]["buttonname"]
        tab_name = data_dict["current_button"]["tab"]
        form_name = data_dict["current_button"]["formname"]

        assignname = data_dict["current_batch"]["source"]

        self.writesql(delete(buttons).where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == form_name))
        self.writesql(delete(batchsequence).where(batchsequence.buttonname == button_name).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name))
        self.writesql(delete(buttonseries).where(buttonseries.formname == form_name).where(buttonseries.assignname == assignname))
        self.gui_refresh()

##edit layout Functions######################################################################################################      
    def edit_layout_save(self, data):
        self.logger.info(f'Saving layout data for form "{self.title}"')  #[button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc]
        for tab, tab_data in data.items():


            for button in tab_data["buttons"]:
                #update values buttons.buttonsequence  = button[0], buttons.columnnum = button[1]
                self.writesql(update(buttons).where(buttons.buttonname == button[1]).where(buttons.tab == tab).where(buttons.formname == self.title).values(buttonsequence = button[0], columnnum = button[2]))
            #delete buttons from tab_data
            tab_data_fresh = tab_data.copy()
            del tab_data_fresh["buttons"]
            tab_data_fresh["tabdesc"] = tab_data_fresh["description"]
            del tab_data_fresh["description"]
            tab_data_fresh["tabsize"] = tab_data_fresh["size"]
            del tab_data_fresh["size"]
            #update values for tab
            self.writesql(update(tabs).where(tabs.tab == tab).where(tabs.formname == self.title).values(**tab_data_fresh))

##Add Action Functions#######################################################################################################
    def create_process_insert(self, batchsequence_dict, buttons_dict):
        self.logger.info(f'Inserting process data for form "{self.title}"')
        batchsequence_dict["runsequence"] = 0
        self.writesql(insert(batchsequence).values(**batchsequence_dict))
        self.writesql(insert(buttons).values(**buttons_dict))
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
        logger.debug(f"asked for input: {input_}")
        if input_ == "createform":
            logger.warning("form not found")
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





