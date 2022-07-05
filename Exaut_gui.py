
print("loading..")
from PyQt6 import QtCore,QtGui,QtWidgets

from PyQt6.QtWidgets import *
from PyQt6 import QtGui

from time import perf_counter

import os,sys
import math,math
from functools import partial
import re

import pyperclip

import Components.EXAUT_gui as EXAUT_gui
from Components.Popups.Create_sequence import Create_sequence
from Components.Popups.edit_popup_tab import edit_popup_tab
from Components.Popups.Edit_Popup import Edit_Popup
from Components.Popups.Edit_Layout import Edit_Layout
from Components.Popups.Create_Process.Create_Process import Create_Process
from time import perf_counter
import nest_asyncio
from Exaut_backend import Loader
import webbrowser
#Import CustomContextMenu


class CustomTab(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super(CustomTab, self).__init__(parent)
        self.parent_ = parent
    
    

    def contextMenuEvent(self, event):
        #get tab at position
        tab_index = self.tabBar().tabAt(event.pos())
        if tab_index == -1:
            return
        self.parent_.tab_context_menu(tab_index)

    #accept drops


class CustomTabArea(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super(CustomTabArea, self).__init__(parent)
        self.parent_ = parent
        self.setAcceptDrops(True)
    def dragEnterEvent(self, event):
       event.accept()
    def dropEvent(self, event):
        #print mimedata info
        mimedata = event.mimeData()
        if not mimedata.hasUrls():
            return
        for url in mimedata.urls():
            #if web url:

            file = url.toLocalFile()
            if not file:
                #get full url:
                file = url.toString()
                if not file:
                    return
                #split by first . second item
                file_name =  file.split(".")[1]
                type_ = "url"
                self.parent_.handle_tab_drag_event(file_name, type_, file)
                return
            print(file)
            #split slash
            file_split = file.split("/")
            #get file name
            file_name = file_split[-1]
            #split extension
            #if not . in file_name:
            type_ = None
            if "." in file_name:
                file_name_split = file_name.split(".")
                file_name = file_name_split[0]
                type_ = file_name_split[-1]
            else:
                file_name = file_name
                type_ = "folder"
            if type_ in ("lnk", "xlsx", "pdf", "db", "txt", "png", "pdf", "jpg", "ini","txt","csv","json", "docx", "doc", "pptx", "vsdx", "xlsb", "log", "htm","gif", "mdgm"):
                type_ = "exe"
            self.parent_.handle_tab_drag_event(file_name, type_, file)
            return
    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        self.customContextMenu()
        return super().contextMenuEvent(a0)   

    def customContextMenu(self):
        #option for Paste that goes to pasteHandler
        menu = QMenu(self)
        menu.addAction("Paste URL", self.pasteurlHandler)
        menu.exec(QtGui.QCursor.pos())

    def pasteurlHandler(self):
        clipboard = pyperclip.paste()
        filename = clipboard.split(".")[-1]
        type_ = "url"
        self.parent_.handle_tab_drag_event(filename, type_, clipboard)

        print(clipboard)
        #if url:
        
class CustomButton(QPushButton):
    
    def __init__(self, parent, color_default = None, color_hover = None, color_hover_border = None, color_border = None, clicked_border = None, clicked_color = None):
        super().__init__(parent)
        self.color_default = QtGui.QColor(225, 225, 225) if color_default is None else color_default
        self.color_border = QtGui.QColor(160, 160, 160) if color_border is None else color_border
        self.color_hover = QtGui.QColor(229, 241, 251) if color_hover is None else color_hover
        self.color_hover_border = QtGui.QColor(0, 120, 215) if color_hover_border is None else color_hover_border
        self.clicked_color = QtGui.QColor(110, 127, 204) if clicked_color is None else clicked_color
        self.clicked_border =  QtGui.QColor(29, 63, 219) if clicked_border is None else clicked_border

        self.duration = 200

        self.start_animation_clicked_main = None
        self.start_animation_clicked_border = None
        self.clicked_anim = False
        self.start_animation_focus = None
        self.start_animation_focus_border = None

        self.stop_animation_focus = None
        self.stop_animation_focus_border = None

        self.handle_style()

        #set stylesheet

    def handle_style(self):            
        self.setStyleSheet(f"""QPushButton{{
                            border-style: solid;
                            background-color: {self.color_default.name()};
                            border-width: 1px 1px 1px 1px;
                            border-radius: 2px;
                            border-color: {self.color_border.name()};
                            padding: 4px;
                            }}
                            """)

    def update_style(self, startstr, newval):
        cur_style = self.styleSheet()

        #find in cur_style, the string x: y; where x is startstr and y in unknown, use regex
        #example, startstr = "background-color", therefore string will be background-color: x;
        startstr_regex = re.compile(f"{startstr}:\s*([^;]*);")
        startstr_match = startstr_regex.search(cur_style)
        #if it matches, replace the found string with the newval
        if startstr_match:
            new_style = cur_style.replace(startstr_match.group(0), f"{startstr}: {newval};")
            self.setStyleSheet(new_style)

    def return_specific_style(self, startstr):
        cur_style = self.styleSheet()

        #find in cur_style, the string x: y; where x is startstr and y in unknown, use regex
        #example, startstr = "background-color", therefore string will be background-color: x;
        startstr_regex = re.compile(f"{startstr}:\s*([^;]*);")
        startstr_match = startstr_regex.search(cur_style)

        if startstr_match:
            hex_val = startstr_match.group(1)
            #dont even ask lmao
            return(QtGui.QColor(*QtGui.QColor(hex_val).getRgb()))

    #on event QtCore.QEvent.HoverMove
    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() not in [QtCore.QEvent.Type.HoverEnter, QtCore.QEvent.Type.HoverLeave, QtCore.QEvent.Type.MouseButtonPress,QtCore.QEvent.Type.MouseButtonRelease]:
            return super().event(e)

        if e.type() == QtCore.QEvent.Type.HoverEnter:
            if not self.clicked_anim:
                self.handle_focus_animation_start()
        elif e.type() == QtCore.QEvent.Type.HoverLeave:
            if not self.clicked_anim:
                self.handle_focus_animation_stop()
        elif e.type() == QtCore.QEvent.Type.MouseButtonPress:
            self.handle_clicked()
        elif e.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self.reset_clicked_style()
        return super().event(e)

    def handle_focus_animation_start(self):
        if self.stop_animation_focus:
            self.stop_animation_focus.stop()
        if self.stop_animation_focus_border:
            self.stop_animation_focus_border.stop()
        self.start_animation_focus = QtCore.QVariantAnimation(self, duration=self.duration, startValue=self.palette().window().color(), endValue=self.color_hover)
        self.start_animation_focus.valueChanged.connect(self.handle_focus_animation_update)
        self.start_animation_focus_border = QtCore.QVariantAnimation(self, duration=self.duration, startValue=self.return_specific_style("border-color"), endValue=self.color_hover_border)
        self.start_animation_focus_border.valueChanged.connect(self.handle_clicked_animation_update_border)

        self.start_animation_focus.start()
        self.start_animation_focus_border.start()

    def handle_focus_animation_stop(self):
        if self.start_animation_focus:
            self.start_animation_focus.stop()
        if self.start_animation_focus_border:
            self.start_animation_focus_border.stop()
        self.stop_animation_focus = QtCore.QVariantAnimation(self, duration=self.duration, startValue=self.palette().window().color(), endValue=self.color_default)
        self.stop_animation_focus.valueChanged.connect(self.handle_focus_animation_update)
        self.stop_animation_focus_border = QtCore.QVariantAnimation(self, duration=self.duration, startValue=self.return_specific_style("border-color"), endValue=self.color_border)
        self.stop_animation_focus_border.valueChanged.connect(self.handle_clicked_animation_update_border)
        self.stop_animation_focus.start()
        self.stop_animation_focus_border.start()
 
    def handle_focus_animation_update(self, value):
        self.update_style("background-color", value.name())

    def handle_clicked(self):
        self.clicked_anim = True
        self.handle_clicked_animation_start()

    def handle_clicked_animation_start(self):
        self.start_animation_clicked_main = QtCore.QVariantAnimation(self, duration=self.duration, startValue=self.palette().window().color(), endValue=self.clicked_color)
        self.start_animation_clicked_border = QtCore.QVariantAnimation(self, duration=self.duration, startValue=self.return_specific_style("border-color"), endValue=self.clicked_border)
        self.start_animation_clicked_main.valueChanged.connect(self.handle_clicked_animation_update_main)
        self.start_animation_clicked_border.valueChanged.connect(self.handle_clicked_animation_update_border)
        self.start_animation_clicked_main.start()

    def handle_clicked_animation_update_border(self, value):
        self.update_style("border-color", value.name())
    
    def handle_clicked_animation_update_main(self, value):
        self.update_style("background-color", value.name())

    def reset_clicked_style(self):
        if self.start_animation_clicked_main:
            self.start_animation_clicked_main.stop()
        if self.start_animation_clicked_border:
            self.start_animation_clicked_border.stop()
        self.clicked_anim = False
        self.handle_style()

class UI_Window(QMainWindow,EXAUT_gui.Ui_EXAUT_GUI):
    signal_button_complete = QtCore.pyqtSignal(str,str)
    signal_tab_complete = QtCore.pyqtSignal(str)
    signal_refresh = QtCore.pyqtSignal()
    signal_move_start = QtCore.pyqtSignal(bool)
    signal_popup_yesno = QtCore.pyqtSignal(str,str,str,str)
    signal_popup_data = QtCore.pyqtSignal(str,str,str)
    signal_popup_tabto = QtCore.pyqtSignal(str, str)
    signal_alert = QtCore.pyqtSignal(str, str)


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
        self.button_dict = {}
        self.lasttab = None
        self.size_static = False
        self.show_hidden_tabs = False

        self.SM_Tabs = CustomTab(self)
        self.setCentralWidget(self.SM_Tabs)


        self.handle_connects()
        self.load()
        self.refresh(start = True)

    def handle_connects(self):
        self.signal_popup_yesno.connect(self.yes_no_popup)
        self.signal_popup_data.connect(self.data_entry_popup)
        self.signal_refresh.connect(self.refresh)
        self.signal_button_complete.connect(self.handle_button_complete)
        self.signal_popup_tabto.connect(self.tabto)
        self.signal_alert.connect(self.alert)

        self.actionAbout.triggered.connect(self.about_window)
        self.actionRefresh.triggered.connect(self.refresh)
        self.actionAdd_Seq.triggered.connect(self.add_sequence)
        self.actionAdd_Proc.triggered.connect(self.add_process)
        self.actionEdit_layout.triggered.connect(self.layout_editor)
        self.actionAdd_Desc.triggered.connect(self.add_description)
        self.actionTabsize.triggered.connect(self.ChangeTabSize)
        self.actionTab_Copy.triggered.connect(self.tab_copy)
        self.actionTab_Move.triggered.connect(self.tab_move)
        self.actionTab.triggered.connect(self.add_tab)
        self.actionTabUrl.triggered.connect(self.add_tab_url)
        self.actionTabFolder.triggered.connect(self.add_tab_folder)
        self.actionAdd_tabto.triggered.connect(self.add_tabto)
        self.actionAdd_tablast.triggered.connect(self.add_tablast)
        self.actionOpen_Files_Explorer.triggered.connect(self.open_tab_folder)
        self.actionOpenTabUrl.triggered.connect(self.open_tab_url)
        self.actionHidden_mode.triggered.connect(self.show_hidden_tabs_handler)


        #lambda self.size_static = not self.size_static
        self.actionstaticsize.triggered.connect(self.setsizesstatic)

    def move_handler(self, pressed):
        self.pressed = pressed

    def show_hidden_tabs_handler(self):
        self.show_hidden_tabs = not self.show_hidden_tabs
        self.refresh()

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

    def handle_button_complete(self, tab, button):
        #get self object by f"{tab}|{button}"
        button = self.button_dict[f"{tab}|{button}"] if f"{tab}|{button}" in self.button_dict else None
        if button:
            button.reset_clicked_style()

    def refresh(self, start = False, layout_mode = False):
        if not start:
            self.refreshing = True
        self.button_cache = {}
        self.tablist, self.tab_buttons = self.backend.ui.refresh()
        self.curTab = self.SM_Tabs.currentIndex()
        self.curtabsize =  f"{self.width()},{self.height()}"
        self.button_dict = {}
            
        for h in reversed(range(0,self.SM_Tabs.count())):
            self.SM_Tabs.removeTab(h)
          

        tabcount = 0
        for tab_name, tab_data in self.tab_buttons.items():
            tab_grid = tab_data['grid']
            tab_desc = tab_data['tabdesc']
            tab_size = tab_data['tabsize']
            tab_buttons = tab_data['buttons']
            tab_group = tab_data['tabgroup']
            if tab_grid==None or tab_grid=="":
                tab_grid = 1
            if tab_group in ("x", "hidden", "hide", "hid"):
                if not self.show_hidden_tabs:
                    continue
            tab = CustomTabArea(self)
            tab.setToolTip(str(tab_desc))
            tab.setObjectName("Tab_"+str(tab_name))

            TabGrid = QtWidgets.QGridLayout(tab)
            ScrollArea = QtWidgets.QScrollArea(tab)
            ScrollArea.setWidgetResizable(True)
            ScrollAreaContents = QtWidgets.QWidget()
            ScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 248, 174))
            ScrollGrid = QtWidgets.QGridLayout(ScrollAreaContents)
            Grid = QtWidgets.QGridLayout()
            tabcount += 1
            ScrollGrid.addLayout(Grid, 0, 0, 1, 1)
            ScrollArea.setWidget(ScrollAreaContents)
            TabGrid.addWidget(ScrollArea, 0, 0, 1, 1)
            self.SM_Tabs.addTab(tab, str(tab_name))
            self.SM_Tabs.setTabText(self.SM_Tabs.indexOf(tab), str(tab_name))
            #set tab context menu

            ##todo: add tab window context menu
            #tab.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            #tab.customContextMenuRequested.connect(partial(self.tab_context_menu, tab))

            button_arr = []
            tab_buttons_copy = self.tab_buttons.copy()
            tab_buttons_copy[tab_name]["allitems"] = [tab, TabGrid, ScrollArea, ScrollAreaContents, ScrollGrid, Grid, button_arr]
            self.button_cache = tab_buttons_copy

        if not self.curTab or self.curTab > self.SM_Tabs.count()-1:
            self.SM_Tabs.setCurrentIndex(0)
        else:
            self.SM_Tabs.setCurrentIndex(self.curTab)
        self.SM_Tabs.currentChanged.connect(self.get_tab_change)
        #if self.edit_layout and layout_mode == False:
            #self.edit_layout.resetlayout(initial=True)
        self.logger.success("Refreshed code")
        #on actionhidden mode press. run show_hidden_tabs_handler
        self.actionHidden_mode.setChecked(self.show_hidden_tabs)
        self.refreshing = False
        self.get_tab_change(self.curTab)

    def setsizesstatic(self):
        self.size_static = not self.size_static

    def handle_color(self, color):
        default_color = QtGui.QColor(225, 225, 225)
        color_base = color
        color_base_tuple = color_base.split(",")
        color_base_rgb = QtGui.QColor(int(color_base_tuple[0]), int(color_base_tuple[1]), int(color_base_tuple[2]))
        if len(color_base_tuple) == 4:
            default_color = color_base_rgb

        r, g, b = (color_base_tuple[0], color_base_tuple[1], color_base_tuple[2])
        losers = []
        winner = None
        #find largest rgb
        if int(r) > int(g) and int(r) > int(b):
            max_rgb = int(r)
            losers.append(int(g))
            losers.append(int(b))
            winner = 0
        elif int(g) > int(r) and int(g) > int(b):
            max_rgb = int(g)
            losers.append(int(r))
            losers.append(int(b))
            winner = 1
        else:
            max_rgb = int(b)
            losers.append(int(r))
            losers.append(int(g))
            winner = 2
        #decrease the others by 50 %
        for pos, loser in enumerate(losers):
            loser = int(loser - (loser * 0.25))
            if loser < 0:
                loser = 0
            losers[pos] = loser
        
        #combine rgb into tuple
        if winner == 0:
            color_border = QtGui.QColor(int(r), int(losers[0]), int(losers[1]))
        elif winner == 1:
            color_border = QtGui.QColor(int(losers[0]), int(g), int(losers[1]))
        else:
            color_border = QtGui.QColor(int(losers[0]), int(losers[1]), int(b))
        

               

        color_hover = color_base_rgb
        sat_dec = 0.50
        color_hover.setHsv(color_hover.hue(), int(color_hover.saturation()*(1-sat_dec)), color_hover.value())
        color_hover_tuple = color_hover.getRgb()
        color_hover = QtGui.QColor(color_hover_tuple[0], color_hover_tuple[1], color_hover_tuple[2])

        color_hover_border = color_border
        color_clicked = color_base_rgb
        color_clicked.setHsv(color_clicked.hue(), int(color_clicked.saturation()*(1 + sat_dec * 2)), color_clicked.value())
        color_clicked_border = color_border

        return(default_color, color_hover, color_hover_border, color_border,  color_clicked_border, color_clicked)

    def get_tab_change(self,n, **kwargs):
        if self.refreshing:
            return
        if "start" not in kwargs:
            for item in self.button_dict:
                self.button_dict[item].deleteLater()
            self.button_dict = {}

            curtabtext = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())

            if curtabtext in self.button_cache:
                all_items = self.button_cache[curtabtext]["allitems"]
                ScrollAreaContents = all_items[3]
                Grid = all_items[5]
                button_arr = []
                tab_buttons = self.button_cache[curtabtext]["buttons"]
                tab_grid = self.button_cache[curtabtext]['grid']
                tabgroup = self.button_cache[curtabtext]['tabgroup']

                for num, (buttonsequence, buttonname, columnnum, buttondesc, type_, color) in enumerate(tab_buttons):

                    Grid.setRowStretch(9999,3)
                    if color != None:
                        button = CustomButton(ScrollAreaContents, *self.handle_color(color))
                    elif type_ == "assignseries":
                        button = CustomButton(
                            ScrollAreaContents,
                            color_border=QtGui.QColor(255, 107, 38),
                            color_hover=QtGui.QColor(252, 209, 189),
                            color_hover_border=QtGui.QColor(247, 92, 20),
                            clicked_color=QtGui.QColor(255, 170, 127),
                            clicked_border=QtGui.QColor(255, 170, 0))
                    elif type_ == None:
                        #color red
                        button = CustomButton(
                            ScrollAreaContents,
                            color_border=QtGui.QColor(255, 0, 0),
                            color_hover=QtGui.QColor(252, 22, 33),
                            color_hover_border=QtGui.QColor(247, 0, 0),
                            clicked_color=QtGui.QColor(255, 170, 127),
                            clicked_border=QtGui.QColor(255, 170, 0))
                    else:
                        button = CustomButton(ScrollAreaContents)
                    self.button_dict[f"{curtabtext}|{buttonname}"] = button
                    button.setToolTip(str(buttondesc))
                    button.setText(str(buttonname))
                    button.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

                    ###add buttoncontextmenu
                    button.customContextMenuRequested.connect(partial(self.button_context_menu,button, type_))
                    x = 0
                    y = 0
                    if tab_grid in (None, "") or tab_grid < 1:
                            tab_grid = 1
                    if columnnum in (None, ""):
                        x = 0
                        y = 0
                        
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
                    button.clicked.connect(partial(self.button_click,buttonname,curtabtext,button,mode=1))
        #curtabtext
        #check if maximized
        
        if not self.size_static and not self.isMaximized():
            if curtabtext in self.tab_buttons:
                curtabsize = self.tab_buttons[curtabtext]["tabsize"]
                if curtabsize not in (None, ""):                
                    self.curtabsize = int(curtabsize.split(",")[0]), int(curtabsize.split(",")[1])
                    self.resize(self.curtabsize[0], self.curtabsize[1])
                    None
                else:
                    self.resize(650,300)
                    None
            else:
                self.resize(650,300)
                None

    def Alert(self, message, title="Alert", icon=QtWidgets.QMessageBox.Icon.Warning):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()

    def Error(self, message, title="Error", icon=QtWidgets.QMessageBox.Icon.Critical):
        self.logger.error(message)
        self.Alert(message, title, icon)


#Drag Drop Handlers################################################################################################################


    def handle_tab_drag_event(self, filename, type_, file):
        if type_ in ("exe", "folder", "url"):
            tabtext = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
            cur_proc = Create_Process(self, self.api.pmgr, self.form_title, tabtext, existing=True, type_=type_, filename=filename, file=file)
            cur_proc.signal_insert.connect(self.api.create_process_insert)
            cur_proc.show()

###################################################################################################################################



##Other GUI Handlers###############################################################################################################

    def db_refresh(self):
        self.tablist, self.tab_buttons = self.backend.ui.refresh()

    def add_tab(self):
        self.db_refresh()
        tab_name = QInputDialog.getText(self, "Add Tab", "Tab Name:")
        if not tab_name[1] or tab_name[0] == "":
            return
        if tab_name[0].lower() in [tab.lower() for tab in self.tablist]:
            self.Error("Tab name already exists")
            return
        self.api.add_tab(tab_name[0], self.form_title)

    def open_tab_folder(self):
        self.db_refresh()
        tab_name = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        folder = self.tab_buttons[tab_name]["treepath"]
        if folder in (None, ""):
            askifadd = QtWidgets.QMessageBox.question(self, 'Add New Tab Folder',"Do you want to add a new tab folder?",QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,QtWidgets.QMessageBox.StandardButton.No)
            if askifadd==QtWidgets.QMessageBox.StandardButton.Yes:
                self.add_tab_folder()
            return
        #open on default browser
        webbrowser.get('windows-default').open(folder)

    def open_tab_url(self):
        self.db_refresh()
        tab_name = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        url = self.tab_buttons[tab_name]["taburl"]
        if url in (None, ""):
            askifadd = QtWidgets.QMessageBox.question(self, 'Add New Tab URL',"Do you want to add a new tab URL?",QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,QtWidgets.QMessageBox.StandardButton.No)
            if askifadd==QtWidgets.QMessageBox.StandardButton.Yes:
                self.add_tab_url()
            return
        #open on default browser
        webbrowser.get('windows-default').open(url)
            
    def add_tab_url(self):
        self.db_refresh()
        tab_url = QInputDialog.getText(self, "Add Tab", "Tab URL:")
        if not tab_url[1] or tab_url[0] == "":
            return
        curtabtext = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        self.api.add_tab_url(curtabtext, tab_url[0], self.form_title)

    def add_tab_folder(self):
        self.db_refresh()
        #open folder tree
        tab_folder = QFileDialog.getExistingDirectory(self, "Add Tab Folder", "", QFileDialog.Option.ShowDirsOnly)
        if not tab_folder:
            return
        curtabtext = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        self.api.add_tab_folder(curtabtext, tab_folder, self.form_title)

    def add_tablast(self):
        self.db_refresh()
        curtabtext = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        self.api.add_tablast("tablast", curtabtext, self.form_title)

    def add_tabto(self):
        self.db_refresh()
        curtab = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        tab_to = QInputDialog.getItem(self, "Add Tab", "Tab To:", self.tablist, 0, False)
        if not tab_to[1] or tab_to[0] == "":
            return
        self.api.add_tabto(tab_to[0], curtab, self.form_title)

    def add_process(self):
        self.db_refresh()
        cur_proc = Create_Process(self, self.api.pmgr, self.form_title, str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())))
        cur_proc.signal_insert.connect(self.api.create_process_insert)
        cur_proc.show()

    def add_sequence(self):
        self.db_refresh()
        if not self.current_sequence:
            self.current_sequence = Create_sequence(self)
            self.current_sequence.signal_save.connect(partial(self.api.edit_sequence_save))
            self.current_sequence.show()

    def edit_button(self, data : dict, state, button = False):
        self.db_refresh()
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

    def edit_tab(self, tab_name):
        self.db_refresh()
        #all current tabs
        cur_tabs = self.tablist
        cur_tab_data = self.tab_buttons[tab_name]
        edit_tab = edit_popup_tab(self, tab_name, cur_tab_data, cur_tabs)
        edit_tab.signal_delete.connect(partial(self.api.edit_tab_delete, tab_name, self.form_title))
        edit_tab.signal_update.connect(partial(self.api.edit_tab_update, tab_name, self.form_title))
        edit_tab.show()

    def layout_editor(self):
        self.db_refresh()
        if self.edit_layout != None:
            try:
                self.edit_layout.close()
            except:
                self.edit_layout = None
                
        self.edit_layout = Edit_Layout(self)
        self.edit_layout.signal_save.connect(self.api.edit_layout_save)
        self.edit_layout.show()

    def tab_copy(self):
        self.db_refresh()
        tab = str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex()))
        forms, tabs =  self.api.copy_tab_data()
        #selection box for forms
        #get index for current form in forms
        cur_form = self.form_title
        cur_form_index = forms.index(cur_form)
        form_select = QtWidgets.QInputDialog.getItem(self, "Copy Tab", "Select Form", forms,cur_form_index,False)
        if not form_select[1]:
            return

        #enter new tab name popup with current tab name
        while True:
            new_tab_name = QtWidgets.QInputDialog.getText(self, "Copy Tab", "Enter New Tab Name", text=tab)
            if not new_tab_name[1]:
                return
            #get form elect value
            form_select_value = form_select[0]
            found = False
            for item in tabs[form_select_value]:
                if item == new_tab_name[0]:
                    self.Alert("Tab Name Already Exists")
                    found = True
            if not found:
                break
        self.api.copy_tab_insert(new_tab_name[0], form_select_value, tab, cur_form)
    
    def tab_move(self):
        self.db_refresh()
        tab = str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex()))
        forms, tabs =  self.api.copy_tab_data()
        #selection box for forms
        #get index for current form in forms
        cur_form = self.form_title
        cur_form_index = forms.index(cur_form)
        form_select = QtWidgets.QInputDialog.getItem(self, "Move Tab", "Select Form", forms,cur_form_index,False)
        if not form_select[1]:
            return

        #enter new tab name popup with current tab name
        while True:
            new_tab_name = QtWidgets.QInputDialog.getText(self, "Move Tab", "Enter New Tab Name", text=tab)
            if not new_tab_name[1]:
                return
            #get form elect value
            form_select_value = form_select[0]
            found = False
            for item in tabs[form_select_value]:
                if item == new_tab_name[0]:
                    self.Alert("Tab Name Already Exists")
                    found = True
            if not found:
                break
        self.api.move_tab_insert(new_tab_name[0], form_select_value, tab, cur_form)

    def button_copy(self,button_name, tab_name, type_, mode, duplicate=False):

        self.db_refresh()
        if type_ == "assignseries":
            self.Alert("Cannot copy an assignseries button at this time")
            return
        self._button_copy_move_form_dict = self.api.button_map()

        if duplicate:
            new_button_name = button_name + "_copy"
            if new_button_name in self._button_copy_move_form_dict[self.form_title][tab_name]:
                self.Alert("Button Name Already Exists")
                return
            self.api.copy_button_insert(self.form_title, tab_name,  button_name, self.form_title,  tab_name,  new_button_name) 
            return


        self._button_copy_move_mode = [mode,  self.form_title,  tab_name, button_name,]
        self._button_copy_move_form_dropdown = QtWidgets.QComboBox()
        self._button_copy_move_tab_dropdown = QtWidgets.QComboBox()

        self._button_copy_move_form_dropdown.addItems(list(self._button_copy_move_form_dict.keys()))
        self._button_copy_move_form_dropdown.currentTextChanged.connect(self.button_copy_form_change)



        #popup with form dropdown and button dropdown
        self._button_copy_move_popup = QtWidgets.QDialog()
        if mode:
            self._button_copy_move_popup.setWindowTitle("Copy Button")
        else:
            self._button_copy_move_popup.setWindowTitle("Move Button")
        self._button_copy_move_popup.setFixedSize(300,200)
        self._button_copy_move_popup.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self._button_copy_move_popup.setModal(True)
        self._button_copy_move_popup.setWindowIcon(QtGui.QIcon(self.icon))

        gridlayout = QtWidgets.QGridLayout()
        self._button_copy_move_popup.setLayout(gridlayout)
        #add form dropdown
        self._button_copy_move_form_dropdown_label = QtWidgets.QLabel("Form:")
        self._button_copy_move_form_dropdown_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self._button_copy_move_form_dropdown_label.setFixedWidth(50)
        self._button_copy_move_form_dropdown_label.setFixedHeight(20)
        gridlayout.addWidget(self._button_copy_move_form_dropdown_label, 0, 0)
        gridlayout.addWidget(self._button_copy_move_form_dropdown, 0, 1)

        #add button dropdown
        self._button_copy_move_tab_dropdown_label = QtWidgets.QLabel("Tab:")
        self._button_copy_move_tab_dropdown_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self._button_copy_move_tab_dropdown_label.setFixedWidth(50)
        self._button_copy_move_tab_dropdown_label.setFixedHeight(20)
        gridlayout.addWidget(self._button_copy_move_tab_dropdown_label, 1, 0)
        gridlayout.layout().addWidget(self._button_copy_move_tab_dropdown, 1, 1)


        #text box for new button name
        self._button_copy_move_new_button_name = QtWidgets.QLineEdit()
        self._button_copy_move_new_button_name.setText(button_name)
        self._button_copy_move_new_button_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._button_copy_move_new_button_name.setFixedHeight(30)
        gridlayout.addWidget(self._button_copy_move_new_button_name, 2, 1)


        #save button:

        if mode:
            self._button_copy_move_save_button = QtWidgets.QPushButton("Copy")
        else:
            self._button_copy_move_save_button = QtWidgets.QPushButton("Move")
        #button expand to fill row, columnspan 2
        self._button_copy_move_save_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._button_copy_move_save_button.setFixedHeight(30)
        
        gridlayout.addWidget(self._button_copy_move_save_button, 3, 1)
        self._button_copy_move_save_button.clicked.connect(self.button_copy_move_save)



        self._button_copy_move_form_dropdown.setCurrentIndex(self._button_copy_move_form_dropdown.findText(self.form_title))
        self.button_copy_form_change(self.form_title)

        self._button_copy_move_popup.show()

    def button_copy_move_save(self):
        #get form and button
        form = self._button_copy_move_form_dropdown.currentText()
    
        tab = self._button_copy_move_tab_dropdown.currentText()

        button_name = self._button_copy_move_new_button_name.text()
        if button_name == "":
            self.Alert("Button Name Cannot Be Blank")
            return
        #check if button already exists
        if button_name  in self._button_copy_move_form_dict[form][tab]:
            self.Alert("Button Already Exists")
            return
        if self._button_copy_move_mode[0]:
            self.api.copy_button_insert(self._button_copy_move_mode[1], self._button_copy_move_mode[2], self._button_copy_move_mode[3],  form, tab, button_name)
        else:
            self.api.move_button_insert(self._button_copy_move_mode[1], self._button_copy_move_mode[2], self._button_copy_move_mode[3],  form, tab, button_name)
        self._button_copy_move_popup.close()

    def button_copy_form_change(self, form):
        self._button_copy_move_tab_dropdown.clear()
        self._button_copy_move_tab_dropdown.addItems(list(self._button_copy_move_form_dict[form].keys()))
        


            
###################################################################################################################################

##Gui->Backend Query Handlers######################################################################################################
    def button_click(self, buttonname, tabname, button, type_, mode=1):
        if mode == 1 and not self.current_sequence and not self.edit_mode:
            button.handle_clicked()
            self.api.button_click(buttonname, tabname, button, mode=1)
        elif mode == 2:
            button.handle_clicked()
            data, state = self.api.edit_button_data(buttonname, tabname)
            self.edit_button(data, state, button)        
        elif mode == 3:
            self.button_copy(buttonname, tabname, type_, mode = True)
        elif mode == 4:
            self.button_copy(buttonname, tabname, type_, mode = False)
            pass
        elif mode == 5:
            self.button_copy(buttonname, tabname, type_, mode = True, duplicate=True)

        elif self.current_sequence:
            button.handle_clicked()
            self.current_sequence.add_button(tabname, buttonname)
#############################################################################################################################

##Action functions###########################################################################################################
    def alert(self, message, title=None):
        icon=QtWidgets.QMessageBox.Icon.Warning

        alert_popup = QtWidgets.QMessageBox()
        if title:
            alert_popup.setWindowTitle(title)
        alert_popup.setText(message)
        alert_popup.setIcon(icon)
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

    def tabto(self,key, tabname):
        if not bool(tabname):
            if self.lasttab:
                index = [index for index in range(self.SM_Tabs.count()) if str(self.lasttab) == self.SM_Tabs.tabText(index)]
            else:
                index = ""
        else:
            self.lasttab = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
            index = [index for index in range(self.SM_Tabs.count()) if str(tabname) == self.SM_Tabs.tabText(index)]
        if len(index)>0:
            self.SM_Tabs.setCurrentIndex(index[0])
        self.popup_msgs[key] = True
            
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


    def add_description(self):
        description = QInputDialog.getText(self, "Add Description", "Enter Description", text="*")
        if description[1]:
            self.api.add_description(description[0], self.SM_Tabs.tabText(self.SM_Tabs.currentIndex()))

    def ChangeTabSize(self):
        curtab = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        cur_width = self.width()
        cur_height = self.height()
        self.api.update_tab_size(curtab, cur_width, cur_height)

##############################################################################################################################

##context menus###############################################################################################################
    def button_context_menu(self, button, type_, event):
        menu = QtWidgets.QMenu(self)
        #tab name is current active tab
        tab_name = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        #button name is the text in the button
        button_name = button.text()

        menu.addAction("Edit", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        type_,
                                        2))
        menu.addAction("Copy", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        type_,
                                        3))
        menu.addAction("Move", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        type_,
                                        4))
        menu.addAction("Duplicate", partial(self.button_click,
                                        button_name,
                                        tab_name,
                                        button,
                                        type_,
                                        5))

        menu.addAction("Edit Layout", self.layout_editor)
        menu.exec(QtGui.QCursor.pos())

    def tab_context_menu(self, tab_index):
        menu = QtWidgets.QMenu(self)
        #get text from tab
        tab_name = self.SM_Tabs.tabText(tab_index)
        menu.addAction("Edit Tab", partial(self.edit_tab,tab_name))
        menu.exec(QtGui.QCursor.pos())
##############################################################################################################################


class GUI_Handler:
    def __init__(self,title=None):
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
    gui = GUI_Handler(title="ExAuT")
    gui.start()

        
