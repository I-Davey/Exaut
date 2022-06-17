
print("loading..")
from PyQt6 import QtCore,QtGui,QtWidgets

from PyQt6.QtWidgets import *
from PyQt6 import QtGui

import os,sys
import math,math
from functools import partial
import Components.EXAUT_gui as EXAUT_gui
from loguru import logger
from Components.Popups.Create_sequence import Create_sequence
from Components.Popups.edit_popup_tab import edit_popup_tab
from Components.Popups.Edit_Popup import Edit_Popup
from Components.Popups.Edit_Layout import Edit_Layout
from Components.Popups.Create_Process.Create_Process import Create_Process
from Components.Popups.data_transfers import data_transfer
from Components.oldtypes import run as run_types
from time import perf_counter
import nest_asyncio
from Exaut_backend import Loader
#Import CustomContextMenu

class UI_Window(QMainWindow,EXAUT_gui.Ui_EXAUT_GUI):

    signal_refresh = QtCore.pyqtSignal()
    signal_move_start = QtCore.pyqtSignal(bool)
    signal_popup_yesno = QtCore.pyqtSignal(str,str,str,str)
    signal_popup_data = QtCore.pyqtSignal(str,str,str)

    def __init__(self,parent=None):
        super(UI_Window,self).__init__(parent)
        self.setupUi(self)
        self.tablist = []
        self.tab_buttons = {}
        self.icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__),'favicon.ico'))
        self.backend = Loader(self)
        self.logger = self.backend.logger
        self.api = self.backend.ui
        self.popup_msgs = {}
        self.title = ""
        self.form_desc = ""
        self.form_title = ""
        self.edit_mode = False
        self.current_sequence = None
        self.edit_layout = None

        self.handle_connects()
        self.load()
        self.refresh(start = True)

    def handle_connects(self):
        self.signal_popup_yesno.connect(self.yes_no_popup)
        self.signal_popup_data.connect(self.data_entry_popup)
        self.signal_refresh.connect(self.refresh)


        self.actionAbout.triggered.connect(self.about_window)
        self.actionRefresh.triggered.connect(self.refresh)
        self.actionAdd_Seq.triggered.connect(self.add_sequence)
        self.actionAdd_Proc.triggered.connect(self.add_process)
        self.actionEdit_layout.triggered.connect(self.layout_editor)

    def move_handler(self, pressed):
        self.pressed = pressed

    def load(self):
        form_title, form_desc = self.api.load()
        self.form_title = form_title
        self.form_desc = form_desc
        self.title = form_title


        self.setWindowTitle(self.form_desc)
        self.setWindowIcon(self.icon)
        #set all icons

        if len(self.tablist) == 0:
            None


        self



    def refresh(self, start = False, layout_mode = False):
        if not start:
            self.refreshing = True
        self.tablist, self.tab_buttons = self.backend.ui.refresh()
        self.curTab = self.SM_Tabs.currentIndex()
        self.curtabsize = (self.width(), self.height())
            
        if len(self.tab_buttons) > self.curTab:
            try:
                #get index position of self.curtab in self.tabs_buttons dictionary
                key = self.tablist[self.curTab]
                ctabsize = self.tab_buttons[key]["size"]
            #convert self.curtabsize to string with space
                curtabsizestr =f"{str(self.curtabsize[0])},{str(self.curtabsize[1])}"
                if ctabsize != curtabsizestr:
                    self.refreshing = False   

            except:
                logger.error("the following error should not interrupt your experience")
                logger.error(f"index error on tabsize, {self.tabsize} RE: {self.curTab} send this to Ian: {self.e}")
                
        for h in reversed(range(0,self.SM_Tabs.count())):
            self.SM_Tabs.removeTab(h)
          

        tabcount = 0
        for tab_name, tab_data in self.tab_buttons.items():
            tab_grid = tab_data['grid']
            tab_desc = tab_data['description']
            tab_size = tab_data['size']
            tab_buttons = tab_data['buttons']

            if tab_grid==None or tab_grid=="":
                tab_grid = 1
            tab = QtWidgets.QWidget()
            tab.setToolTip(str(tab_desc))
            tab.setObjectName("Tab_"+str(tabcount))
            TabGrid = QtWidgets.QGridLayout(tab)
            ScrollArea = QtWidgets.QScrollArea(tab)
            ScrollArea.setWidgetResizable(True)
            ScrollAreaContents = QtWidgets.QWidget()
            ScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 248, 174))
            ScrollGrid = QtWidgets.QGridLayout(ScrollAreaContents)
            Grid = QtWidgets.QGridLayout()
            tabcount += 1

            button_arr = []
            for num, (buttonsequence, buttonname, columnnum, buttondesc) in enumerate(tab_buttons):

                Grid.setRowStretch(9999,3)
                button = QtWidgets.QPushButton(ScrollAreaContents)
                button.setToolTip(str(buttondesc))
                button.setText(str(buttonname))
                button.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
                ###add buttoncontextmenu
                button.customContextMenuRequested.connect(partial(self.button_context_menu,button))

                if columnnum in (None, ""):
                    x = 0
                    y = 0
                    if tab_grid in (None, "") or tab_grid < 1:
                        tab_grid = 1
                    if tab_grid < 2:
                        x = num // tab_grid
                        y = num % tab_grid
                        if len(button_arr) == 0:
                            button_arr.append(0)
                        button_arr[0] += 1
                    else:
                        x = num % math.ceil(len(tab_buttons)/tab_grid)
                        y = num // math.ceil(len(tab_buttons)/tab_grid)
                        while len(button_arr) < y+1:
                            button_arr.append(0)
                        button_arr[y] += 1

                else:
                    if len(button_arr) < tab_grid:
                        for i in range(tab_grid):
                            if i >= len(button_arr):
                                button_arr.append(0)
                    
                    y = columnnum - 1
                    if tab_grid in (None, "") or tab_grid < 1:
                        tab_grid = 1
                    if y > tab_grid - 1:
                        y = tab_grid - 1
                    elif y < 0:
                        y = 0
                    x = button_arr[y]
                    button_arr[y] += 1
                Grid.addWidget(button, x, y, 1, 1)
                button.setStyleSheet(" QPushButton:focus { background-color: tomato }")
                button.clicked.connect(partial(self.button_click,buttonname,tab_name,button,mode=1))
            ScrollGrid.addLayout(Grid, 0, 0, 1, 1)
            ScrollArea.setWidget(ScrollAreaContents)
            TabGrid.addWidget(ScrollArea, 0, 0, 1, 1)
            self.SM_Tabs.addTab(tab, str(tab_name))
            self.SM_Tabs.setTabText(self.SM_Tabs.indexOf(tab), str(tab_name))
        if self.curTab<0 or self.curTab > self.SM_Tabs.count()-1:
            self.SM_Tabs.setCurrentIndex(0)
        else:
            self.SM_Tabs.setCurrentIndex(self.curTab)
        self.SM_Tabs.currentChanged.connect(partial(self.get_tab_change,tab_size))
        self.SM_Tabs.tabBarClicked.connect(self.on_tab_change_handler)
        #if self.edit_layout and layout_mode == False:
            #self.edit_layout.resetlayout(initial=True)
        logger.success("Refreshed code")
        #self.actionEdit_mode_toggled(self.edit_mode)
        self.refreshing = False            

    def get_tab_change(self,n):
            if self.refreshing:
                return
            #curtabtext
            curtabtext = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
            if curtabtext in self.tab_buttons:
                curtabsize = self.tab_buttons[curtabtext]["size"]
                if curtabsize not in (None, ""):                
                    self.curtabsize = int(curtabsize.split(",")[0]), int(curtabsize.split(",")[1])
                    self.resize(self.curtabsize[0], self.curtabsize[1])
                else:
                    self.resize(650,300)
            else:
                self.resize(650,300)

    def on_tab_change_handler(self, index):
        #if counter for tab is not even


        if self.edit_mode:
            curtab = str(self.SM_Tabs.tabText(index))
            if curtab in self.tab_edit_dict:
                #make active window
                self.tab_edit_dict[curtab].setFocus()
            else:
                x = edit_popup_tab(self, curtab)
                x.show()
                self.tab_edit_dict.update({curtab:x})

    def Alert(self, message, title="Alert", icon=QtWidgets.QMessageBox.Icon.Warning):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()

    def Error(self, message, title="Error", icon=QtWidgets.QMessageBox.Icon.Critical):
        self.logger.error(message)
        self.Alert(message, title, icon)

##Other GUI Handlers###############################################################################################################

    def add_process(self):
        cur_proc = Create_Process(self, self.api.pmgr, self.form_title, str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())))
        cur_proc.signal_insert.connect(self.api.create_process_insert)
        cur_proc.show()

    def add_sequence(self):
        if not self.current_sequence:
            self.current_sequence = Create_sequence(self)
            self.current_sequence.signal_save.connect(partial(self.api.edit_sequence_save))
            self.current_sequence.show()

    def edit_button(self, data : dict, state):
        if not state:

            self.Alert(f"Button {data['button_data']['buttonname']} Has no Batchsequence, Deletion Recommended")
            edit_popup = Edit_Popup(self, data, state=False)
            
        elif state == "sequence":
            self.current_sequence = Create_sequence(self, edit=True, data=data["sequence"])
            self.current_sequence.signal_delete.connect(self.api.edit_sequence_delete)
            self.current_sequence.signal_update.connect(partial(self.api.edit_sequence_update, data))

            edit_popup = Edit_Popup(self, data["edit"])
        elif state == "button":
            edit_popup = Edit_Popup(self, data)

        else:
            return

        edit_popup.signal_delete.connect(partial(self.api.edit_button_delete, data))
        edit_popup.signal_update.connect(partial(self.api.edit_button_update, data))
        edit_popup.show()
        if state == "sequence":
            self.current_sequence.show()

    def layout_editor(self):
        if self.edit_layout != None:
            try:
                self.edit_layout.close()
            except:
                self.edit_layout = None
                
        self.edit_layout = Edit_Layout(self)
        self.edit_layout.signal_save.connect(self.api.edit_layout_save)
        self.edit_layout.show()

            
###################################################################################################################################

##Gui->Backend Query Handlers######################################################################################################
    def button_click(self, buttonname, tabname, button, mode=1):
        if mode == 1 and not self.current_sequence and not self.edit_mode:
            self.api.button_click(buttonname, tabname, button, mode=1)
        if mode == 2:
            data, state = self.api.edit_button_data(buttonname, tabname)
            self.edit_button(data, state)
            button.setStyleSheet("background: None;")
            pass
        
        elif mode == 3:
            #self.copy_button_data(batchsequence_data, button_name, tab_name)
            #button.setStyleSheet("background: None")
            pass
        elif mode == 4:
            #self.move_button_data(batchsequence_data, button_name, tab_name)
            #button.setStyleSheet("background: None")
            pass
        elif mode == 5:
            #self.copy_button_data(batchsequence_data, button_name, tab_name)(duplicate)
            #button.setStyleSheet("background: None")
            pass
        elif self.current_sequence:
            self.current_sequence.add_button(tabname, buttonname)
            button.setStyleSheet("background: None")
#############################################################################################################################

##Action functions###########################################################################################################
    def alert(self, message, title=None):
        alert_popup = QtWidgets.QMessageBox()
        if title:
            alert_popup.setWindowTitle(title)
        alert_popup.setText(message)
        alert_popup.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        alert_popup.exec()

    def yes_no_popup(self,key, message, title, default):
        yes_no_popup = QtWidgets.QMessageBox()
        if title:
            yes_no_popup.setWindowTitle(title)
        yes_no_popup.setText(message)
        yes_no_popup.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if default == "yes":
            yes_no_popup.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)
        else:
            yes_no_popup.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        yes_no_popup.exec()
        if yes_no_popup.result() == QtWidgets.QMessageBox.StandardButton.Yes:
            self.popup_msgs[key] = True
        else:
            self.popup_msgs[key] = False

    def data_entry_popup(self,key, message, title):
        text, ok = QInputDialog.getText(self, title, message)
        if not ok: 
            self.popup_msgs[key] = None
        else:
            self.popup_msgs[key] = text
##############################################################################################################################

##others######################################################################################################################
    def about_window(self):
        about = QtWidgets.QMessageBox()
        about.setWindowTitle("About ExAuT - ***REMOVED***")
        #set QtWidgets.QMessageBox.Icon.Information
        about.setWindowIcon(self.icon)
        #add two text fields
        about.setText(f"Version: {self.api.version}\n\nForm: {self.title}\n\nCopyright (c) 2022 ***REMOVED***\n\nAll rights reserved.")
        about.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        about.exec()
##############################################################################################################################

##context menus###############################################################################################################
    def button_context_menu(self, button, event):
        menu = QtWidgets.QMenu(self)
        #tab name is current active tab
        tab_name = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        #button name is the text in the button
        button_name = button.text()

        menu.addAction("Edit", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        2))
        menu.addAction("Copy", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        3))
        menu.addAction("Move", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        4))
        menu.addAction("Duplicate", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        5))

        menu.addAction("Edit Layout", self.layout_editor)
        menu.exec(QtGui.QCursor.pos())
##############################################################################################################################


class GUI_Handler:
    def __init__(self,logger,title=None):
        self.logger = logger
        self.title = title
        self.app = None
        self.window = None



    def start(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = UI_Window()
        self.window.show()
        self.app.exec()
        nest_asyncio.apply()
        sys.exit()

    def UI_Window(self):
        return self.window

if __name__ == "__main__":
    gui = GUI_Handler(logger,title="ExAuT")
    gui.start()

        
