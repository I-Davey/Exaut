from time import perf_counter
from tkinter.tix import PopupMenu
from Plugins import Plugins 
from loguru import logger
import sys
import os
from iniconfig import Parse
from Components.db.Exaut_sql import  Base, forms, tabs, buttons, batchsequence, buttonseries
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, func, and_, or_, select, update, insert, delete
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import CreateTable
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
            print(key)
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
                buttons_tabs[button.tab]["buttons"] = []
            buttons_tabs[button.tab]["buttons"].append([button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc])
        self.tab_buttons = buttons_tabs
        self.tablist = [tab.tab for tab in tab_info]
        print("EMITTING")
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
        if mode == 2:
            #self.edit_button(button_name, tab_name)
            #button.setStyleSheet("background: None;")
            pass
        
        elif len(batchsequence_data) == 0:
            self.alert(f"No batchsequence data found for button: {button_name} on tab: {tab_name} in form: {self.title}")
        
        elif mode == 3:
            #self.copy_button(batchsequence_data, button_name, tab_name)
            #button.setStyleSheet("background: None")
            pass
        elif mode == 4:
            #self.move_button(batchsequence_data, button_name, tab_name)
            #button.setStyleSheet("background: None")
            pass
        elif mode == 5:
            #self.copy_button(batchsequence_data, button_name, tab_name)
            #button.setStyleSheet("background: None")
            pass
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

            for form_name in (None, ""):
                res, type_ = button_click(button_name, tab_name, button_obj=None, mode="sequence")
                if not res:
                    if type_ == "warning":
                        logger.warning("stopped sequence")
                        break
        endtime = perf_counter()
        logger.success(f"completed button sequence {original_button_name} in {round((endtime-ctime),2)} seconds") 
            
        


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
    print("test passed")



