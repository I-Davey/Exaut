#from PyQt6.QtWidgets import QApplication, QMainWindow
#from Components.auth import Auth
import imp
from multiprocessing.reduction import duplicate
import threading

#run authenticate in a thread
#print("authenticating")
#auth_object = Auth()
#authenticate = auth_object.authenticate
#authenticate("init")




print("loading..")
from PyQt6 import QtCore,QtGui,QtWidgets
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
import time
import os,sys,ctypes,shutil
import math,ctypes,apsw,math
from functools import partial
import webbrowser
import Components.PICAT_gui as PICAT_gui
from loguru import logger
from iniconfig import Parse
from Plugins import Plugins 
from Components.Popups.Create_sequence import Create_sequence
from Components.Popups.edit_popup_tab import edit_popup_tab
from Components.Popups.Edit_Popup import Edit_Popup
from Components.Popups.Edit_Layout import Edit_Layout
from Components.Popups.Create_Process.Create_Process import Create_Process
from Components.Popups.data_transfers import data_transfer
from Components.oldtypes import run as run_types
from Components.Excel import Excel_Popup
from version import version
from time import perf_counter
from PyQt6.QtCore import QThread
import nest_asyncio
import asyncio
#Import CustomContextMenu
from PyQt6.QtCore import Qt



db_cfg = Parse("SQLCONN").cfg
current_filename = os.path.basename(sys.argv[0]).split(".")[0]
file_cfg = Parse(current_filename.upper()).cfg
logger.debug(f"filename: {current_filename.upper()} + filecfg_arr = {file_cfg}")
form_name = None
if not file_cfg:
    logger.error(f"No [{current_filename}] header in config.ini")
    #pop up with ctypes
    ctypes.windll.user32.MessageBoxW(0,"No [{}] header in config.ini, please check file name and capitalization within config.ini".format(current_filename.upper()),"PICAT Error",1)
    #exit progrm
    sys.exit()
else:
    form_name = file_cfg["form"]
connectionpath = db_cfg["connectionpath"] if db_cfg["connectionpath"] else os.getcwd()
connection_db ="\\" + db_cfg["connection"]
logger.debug(f"connectionpath = {connectionpath}, connection_db = {connection_db}")
logger.debug(f"Form name is: {form_name}")
picat_cfg = Parse("APPLICATION VARIABLES").cfg
PG_PASS = picat_cfg["pg_pass"]
signalsprefix = picat_cfg["signalsprefix"]
pmgr = Plugins()
if pmgr.fail == True:
    logger.error(f"Critical error, plugin manager failed to load")
    logger.error(pmgr.error)
    sys.exit()


#
# SQLite Functions

ReadSQL = pmgr.methods["ReadSQL"]["run"].main
WriteSQL = pmgr.methods["WriteSQL"]["run"].main

runExcel = Excel_Popup

if not connection_db and not connectionpath:
    result = ctypes.windll.user32.MessageBoxW("SQLITE DB Connection details not found in config.ini","",1)
    if result==1:
        sys.exit()

db_conn = connectionpath + connection_db
if os.path.exists(db_conn):
    connection = apsw.Connection(db_conn)
    cursor = connection.cursor()
else:
    result = ctypes.windll.user32.MessageBoxW(0,f"failed to locate {db_conn}","",1)
    if result==1:
        sys.exit()

# Create tables
WriteSQL("create table if not exists forms(formname char(63) "+
         "primary key,formdesc text); pragma foreign_keys = on")

'''
WriteSQL("create table if not exists tabs(formname char(63),"+
         "tab char(63),tabsequence integer,tabdesc text,treepath char(1023),"+
         "primary key(formname,tab),foreign key(formname) references forms"+
         "(formname) on delete no action on update no action); pragma foreign_keys = on")
'''

WriteSQL("create table if not exists tabs(formname char ( 63 ),tab char ( 63 ),tabsequence INTEGER,grid INTEGER,tabdesc TEXT,treepath CHAR ( 1023 ),tabgroup CHAR ( 63 ),tabsize INTEGER,primary key(formname,tab)); pragma foreign_keys = on")


WriteSQL("CREATE TABLE if not exists buttonseries(formname char(63),tab char(63),buttonname char(63),assignname char(63),runsequence INTEGER,primary key(formname,tab,buttonname,assignname,runsequence)); pragma foreign_keys = on")

WriteSQL("create table if not exists buttons(formname char(63),"+
         "tab char(63),buttonname char(63),buttonsequence "+
         "integer,columnnum integer,buttondesc text,buttongroup char(63),active char(63),"+
         "treepath char(1023),primary key(formname,tab,"+
         "buttonname),foreign key(formname,tab) references tabs(formname,"+
         "tab) on delete no action on update no action); pragma "+
         "foreign_keys = on")

WriteSQL("create table if not exists sqlengine(enginepathfile char(1023) "+
         "primary key); pragma foreign_keys = on")

WriteSQL("create table if not exists batchsequence(formname char(63),tab "+
         "char(63),buttonname char(63),runsequence integer,"+
         "folderpath char(1023),filename char(255),type char(63),"+
         "source char(1023),target char(1023),databasepath char(1023),"+
         "databasename char(255),keypath char(1023),"+
         "keyfile char(255),treepath char(1023),primary key(formname,tab,buttonname,runsequence)); pragma foreign_keys = on")
         #"foreign key(formname,tab,buttonname) references buttons(formname,"+ "tab,buttonname) on delete no action on update no action); pragma "+"foreign_keys = on")



class DB_Window(QMainWindow,PICAT_gui.Ui_PICAT_SM):
    def __init__(self,parent=None):
        super(DB_Window,self).__init__(parent)
        self.setupUi(self)
        QtWidgets.QApplication.setStyle('windowsvista')
        self.ReadSQL = ReadSQL
        self.WriteSQL = WriteSQL
        self.refreshing = False
        self.curtabsize = None
        # Get Form Title & Description
        formtitle = ReadSQL("select formname from forms")
        if len(formtitle)<1:
            formtitle = 'Untitled'
        else:
            formtitle = []
            for item in ReadSQL("select formname from forms"):
                formtitle.append(item[0])

        if form_name:
            if form_name in formtitle:
                self.title = form_name
            else:
                new_formdesc = str(QInputDialog.getText(None,"New form description","New form description:",QLineEdit.EchoMode.Normal,"")[0])
                if not new_formdesc:
                    ctypes.windll.user32.MessageBoxW(0,"Form name not found in DB. exiting.","FAIL",0)
                    sys.exit()
                #INSERT INTO forms (formname, formdesc)
                WriteSQL("insert into forms (formname, formdesc) values ('"+form_name+"','"+new_formdesc+"')")
                self.title = form_name


        else:
            self.title = formtitle


        formdesc = ReadSQL(f"select formdesc from forms where formname='{self.title}'")
        if len(formdesc)<1:
            formdesc = 'Untitled'
        else:
            formdesc = ReadSQL(f"select formdesc from forms where formname='{self.title}'")[0][0]
        self.setWindowTitle(formdesc)
        self.actionEdit_mode_toggled()
        self.cur_seq = None

        # File Tree
        self.actionOpen_Files_Explorer.triggered.connect(self.Open_File_Tree)

        # Add EXE
        self.actionAdd_exe.triggered.connect(self.Add_EXE)
        self.actionCopy_folder.triggered.connect(self.copyFolder)
        self.actionAdd_tabto.triggered.connect(self.Add_Tabto)

        self.actionAdd_Seq.triggered.connect(self.Add_Seq)
        self.actionAdd_Proc.triggered.connect(self.Add_Proc)


        self.actionAdd_Desc.triggered.connect(self.Add_Desc)


        self.actionEdit_layout.triggered.connect(self.layout_editor)

        
        #add URL
        self.actionAdd_url.triggered.connect(self.Add_url)

        self.actionAdd_Folder.triggered.connect(self.Add_Folder)

        self.actionEdit_mode.toggled.connect(self.actionEdit_mode_toggled)
        self.actionEdit_mode.setChecked(self.edit_mode)

        #copy file
        self.actionCopy.triggered.connect(self.Copy_File)

        self.sht2tbl.triggered.connect(self.addsht2tbl)

        self.actionTab_Copy.triggered.connect(self.Copy_Tab_form)
        self.actionTab_Move.triggered.connect(self.Move_Tab_form)

        # Refresh
        self.actionRefresh.triggered.connect(self.Refresh)
        
        self.actionTabsize.triggered.connect(self.ChangeTabSize)

        self.actionTab.triggered.connect(self.NewTab)

        self.actionTabUrl.triggered.connect(self.NewTabUrl)

        self.actionTabFolder.triggered.connect(self.NewTabFolder)

        self.actionOpenTabUrl.triggered.connect(self.OpenTabUrl)

        # Import Excel
        self.customimportexport.triggered.connect(self.data_transfer_handler)

        # Export Excel
        self.actionExport_to_Excel.triggered.connect(self.ExportExcel)
        self.actionImport_from_Excel.triggered.connect(self.ImportExcel)


        # Last Saved Tab
        self.lasttab = ""

        self.threads = []

        self.edit_layout = None
        
        self.tab_edit_dict = {}

        self.counter_for_tab = 0
        
        #Main: Set Up Tabs Filter
        #self.Main_CB_Tabs.addItem("")
        tablist = ReadSQL("select tab from tabs where formname = '"+self.title+"'")
        if len(tablist)>0:
            for tl in range(len(tablist)):
                self.Main_CB_Tabs.addItem(str(tablist[tl][0]))
        self.Main_CB_Tabs.currentIndexChanged.connect(self.on_tab_change)


        #Main: Set Up Buttons Filter
        self.Main_CB_Buttons.currentIndexChanged.connect(self.on_button_change)

        #Main: Insert Record
        #self.Main_Button_InsertRec.clicked.connect(self.on_InsertRec)

        #Main: Delete Record
        self.Main_Button_DeleteRec.clicked.connect(self.on_DeleteRec)

        #Main: Main Table
        self.Main_Table.itemChanged.connect(self.on_CellChange)



        #Create Tabs & Buttons

        self.actionAbout.triggered.connect(self.AboutMsg_Try)

        self.Refresh(start=True)
        self.Refresh(start=True)
        #self.auth_handle()

    def auth_handle(self):
        self.auththread = QThread(self)
        self.auth_object = auth_Thread()
        self.auth_object.moveToThread(self.auththread)
        self.auththread.started.connect(self.auth_object.start_auth)
        self.auth_object.auth_signal.connect(lambda: sys.exit(1))
        self.auth_object.freeze_signal.connect(self.freeze_window)
        self.auththread.start()

    def data_transfer_handler(self):
        dt  = data_transfer(self)
        dt.exec()


    def freeze_window(self, freeze):
        if freeze:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            #freeze gui all buttons
            self.setEnabled(False)
        else:
            QtWidgets.QApplication.restoreOverrideCursor()
            #unfreeze gui all buttons
            self.setEnabled(True)

    def Refresh(self, start = False, layout_Mode = False):
        if not start:
            self.refreshing = True
        self.curTab = self.SM_Tabs.currentIndex()
        self.curtabsize = (self.width(), self.height())

        formtabs = ReadSQL("select tab from tabs where formname = '"+
                           self.title+"' order by tabsequence asc")
        tabgrid = ReadSQL("select grid from tabs where formname = '"+
                           self.title+"' order by tabsequence asc")
        tabsdesc = ReadSQL("select tabdesc from tabs where formname = '"+
                           self.title+"' order by tabsequence asc")
        tabsize = ReadSQL("select tabsize from tabs where formname = '"+
                          self.title+"' order by tabsequence asc")

        #check if tabsize is the same for current tab and self.curtabsize:
        if len(tabsize)> self.curTab:
            try:
                ctabsize = tabsize[self.curTab][0]
                #convert self.curtabsize to string with space
                curtabsizestr =f"{str(self.curtabsize[0])},{str(self.curtabsize[1])}"
                if ctabsize != curtabsizestr:
                    self.refreshing = False
            except IndexError as e:
                logger.error("the following error should not interrupt your experience")
                logger.error(f"index error on tabsize, {tabsize} RE: {self.curTab} send this to Ian: {e}")

        for h in reversed(range(0,self.SM_Tabs.count())):
            self.SM_Tabs.removeTab(h)
        
        if len(formtabs)>0:
            for ft in range(len(formtabs)):
                if tabgrid[ft][0]==None or tabgrid[ft][0]=="":
                    tabgrid[ft][0] = 1
                self.tab = QtWidgets.QWidget()
                self.tab.setToolTip(str(tabsdesc[ft][0]))
                self.tab.setObjectName("Tab_"+str(ft+1))
                self.TabGrid = QtWidgets.QGridLayout(self.tab)
                self.TabGrid.setObjectName("TabGrid_"+str(ft+1))
                self.SM_ScrollArea = QtWidgets.QScrollArea(self.tab)
                self.SM_ScrollArea.setWidgetResizable(True)
                self.SM_ScrollArea.setObjectName("SM_ScrollArea_"+str(ft+1))
                self.SM_ScrollAreaContents = QtWidgets.QWidget()
                self.SM_ScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 248, 174))
                self.SM_ScrollAreaContents.setObjectName("SM_ScrollAreaContents_"+str(ft+1))
                self.SM_ScrollGrid = QtWidgets.QGridLayout(self.SM_ScrollAreaContents)
                self.SM_ScrollGrid.setObjectName("SM_ScrollGrid_"+str(ft+1))
                self.SM_Grid = QtWidgets.QGridLayout()
                self.SM_Grid.setObjectName("SM_Grid_"+str(ft+1))
                allbuttons = ReadSQL("select buttonname from buttons where "+
                                     "formname = '"+self.title+"' and tab = '"+
                                     str(formtabs[ft][0])+"' order by buttonsequence asc")
                if len(allbuttons)>0:
                    formbuttons = ReadSQL("select buttonname from buttons where "+
                                          "formname = '"+self.title+"' and tab = '"+
                                          str(formtabs[ft][0])+"' and columnnum is null "+
                                          "order by buttonsequence asc")
                    formbuttons2 = ReadSQL("select buttonname from buttons where "+
                                           "formname = '"+self.title+"' and tab = '"+
                                           str(formtabs[ft][0])+"' and columnnum is not null "+
                                           "order by buttonsequence asc")
                    buttonsordered = []
                    for i in range(len(formbuttons)):
                        buttonsordered.append(formbuttons[i])
                    for i in range(len(formbuttons2)):
                        buttonsordered.append(formbuttons2[i])
                    buttoncol = ReadSQL("select columnnum from buttons where "+
                                        "formname = '"+self.title+"' and tab = '"+
                                        str(formtabs[ft][0])+"' and columnnum is not null "+
                                        "order by buttonsequence asc")
                    buttoncolordered = []
                    for i in range(len(formbuttons)):
                        buttoncolordered.append(None)
                    for i in range(len(formbuttons2)):
                        buttoncolordered.append(buttoncol[i])
                    buttonsdesc = ReadSQL("select buttondesc from buttons where "+
                                          "formname = '"+self.title+"' and tab = '"+
                                          str(formtabs[ft][0])+"' and columnnum is null "+
                                          "order by buttonsequence asc")
                    buttonsdesc2 = ReadSQL("select buttondesc from buttons where "+
                                           "formname = '"+self.title+"' and tab = '"+
                                           str(formtabs[ft][0])+"' and columnnum is not null "+
                                           "order by buttonsequence asc")
                    buttondescordered = []
                    for i in range(len(buttonsdesc)):
                        buttondescordered.append(buttonsdesc[i])
                    for i in range(len(buttonsdesc2)):
                        buttondescordered.append(buttonsdesc2[i])

                    accumbuttons = []
                    for bn in range(len(buttonsordered)):
                        if bn!=0:
                            self.SM_Grid.setRowStretch(bn,3)
                        self.button = QtWidgets.QPushButton(self.SM_ScrollAreaContents)
                        self.button.setToolTip(str(buttondescordered[bn][0]))
                        self.button.setObjectName("SM_Button_"+str(ft+1)+"_"+str(bn+1))
                        self.button.setText(str(buttonsordered[bn][0]))
                        #add rightclick menu to run button_context_menu
                        self.button.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
                        self.button.customContextMenuRequested.connect(partial(self.button_context_menu,self.button))

                        if buttoncolordered[bn] in (None, [None], ['']):
                            x = 0
                            y = 0
                            if tabgrid[ft][0]==None or tabgrid[ft][0]=="":
                                tabgrid[ft][0] = 1
                                x = bn//tabgrid[ft][0]
                                y = bn%tabgrid[ft][0]
                                while len(accumbuttons)<1:
                                    accumbuttons.append(0)
                                accumbuttons[0] += 1
                            else:
                                if tabgrid[ft][0]<2:
                                    x = bn//tabgrid[ft][0]
                                    y = bn%tabgrid[ft][0]
                                    while len(accumbuttons)<1:
                                        accumbuttons.append(0)
                                    accumbuttons[0] += 1
                                else:
                                    x = bn%math.ceil(len(buttonsordered)/tabgrid[ft][0])
                                    y = bn//math.ceil(len(buttonsordered)/tabgrid[ft][0])
                                    while len(accumbuttons)<y+1:
                                        accumbuttons.append(0)
                                    accumbuttons[y] += 1
                        else:
                            if len(formbuttons2)>0:
                                if len(accumbuttons)<tabgrid[ft][0]:
                                    lenaccumbuttons = len(accumbuttons)
                                    for i in range(tabgrid[ft][0]):
                                        if i>=lenaccumbuttons:
                                            accumbuttons.append(0)
                                
                                y = buttoncolordered[bn][0]-1
                                if tabgrid[ft][0]==None or tabgrid[ft][0]<2:
                                    tabgrid[ft][0] = 1
                                if y>tabgrid[ft][0]-1:
                                    y = tabgrid[ft][0]-1
                                elif y<0:
                                    y = 0
                                x = accumbuttons[y]
                                
                                accumbuttons[y] += 1

                        self.SM_Grid.addWidget(self.button, x, y, 1, 1)
                        self.button.setStyleSheet("QPushButton { background-color: none }"
                                                  "QPushButton:hover { background-color: lightblue }"
                                                  "QPushButton:focus { background-color: tomato }" )
                        self.button.clicked.connect(partial(self.on_click_button,
                                                    self.title,
                                                    str(formtabs[ft][0]),
                                                    str(buttonsordered[bn][0]),
                                                    "SM_Button_"+str(ft+1)+"_"+str(bn+1),
                                                    button=self.button))
                self.SM_ScrollGrid.addLayout(self.SM_Grid, 0, 0, 1, 1)
                self.SM_ScrollArea.setWidget(self.SM_ScrollAreaContents)
                self.TabGrid.addWidget(self.SM_ScrollArea, 0, 0, 1, 1)
                self.SM_Tabs.addTab(self.tab, "")
                self.SM_Tabs.setTabText(self.SM_Tabs.indexOf(self.tab),formtabs[ft][0])
        if self.curTab<0 or self.SM_Tabs.count()<=self.curTab:
            self.SM_Tabs.setCurrentIndex(0)
        else:
            self.SM_Tabs.setCurrentIndex(self.curTab)
        self.SM_Tabs.currentChanged.connect(partial(self.get_tab_change,tabsize))
        self.SM_Tabs.tabBarClicked.connect(self.on_tab_change_handler)
        if self.edit_layout and layout_Mode == False:
            self.edit_layout.resetlayout(initial=True)
        logger.success("Refreshed code")
        self.actionEdit_mode_toggled(self.edit_mode)
        self.refreshing = False
   
    def copyFolder(self):
        #select type = — copy new files -full override all files — copy nonexistent  files
        #create a dropdown box to select type
        dropdown_select_type = QtWidgets.QComboBox()
        type_index_list = ["foldercopynew","foldercopyforce","foldercopynonx"]
        type_text_list = ["Copy new files","Full override all files","Copy nonexistent files"]

        dropdown_select_type.addItem("Copy new files")
        dropdown_select_type.addItem("full override all files")
        dropdown_select_type.addItem("Copy nonexistent files")
        dropdown_select_type.setCurrentIndex(0)
        #display dropdown in a dialog box
        #qinputdialog get index of selected type_text_list
        chosen_type = QtWidgets.QInputDialog.getItem(self, "Select type", "Select type", type_text_list, 0, False)

        if chosen_type[1]==True:
            for item in type_text_list:
                if item == chosen_type[0]:
                    chosen_type = type_index_list[type_text_list.index(item)]
                    break
        else:
            return
        #get source and destination folders
        source_folder = QFileDialog.getExistingDirectory(self, "Select source folder")
        if source_folder == "":
            return
        destination_folder = QFileDialog.getExistingDirectory(self, "Select destination folder")
        if destination_folder == "":
            return
        #get button name
        button_name = QInputDialog.getText(self, "Copy Folder", "Enter button name")
        if button_name[1]==True:
            button_name = button_name[0]
        else:
            return
        #create button query formname, tab, buttonname: self.title, gettext(currentindex), button_name
        curtab = str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex()))
        button_query = f"insert into buttons (formname, tab, buttonname, buttonsequence) values ('{self.title}', '{curtab}', '{button_name}', 1)"
        #batchsequence_query = insert into batchsequence formname tab buttonname "type" "source" "target
        batchsequence_query = f"insert into batchsequence (formname, tab, buttonname, type, source, target) values ('{self.title}', '{curtab}', '{button_name}', '{chosen_type}', '{source_folder}', '{destination_folder}')"
        #execute query
        WriteSQL(button_query)
        WriteSQL(batchsequence_query)

    def Move_Tab_form(self):
        curtab = str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex()))
        if curtab == "":
            ctypes.windll.user32.MessageBoxW(0,"No tab selected","FAIL",0)
            return
        forms = ReadSQL("select formname from forms where formname != '"+self.title+"'")
        if len(forms)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No forms in DB. cancelling.","FAIL",0)
            logger.error("No forms in DB. returning.")
            return
        
        #create popup with dropdown box of forms
        form_list = []
        for form in forms:
            if form[0] != self.title:
                form_list.append(form[0])
        form_list.sort()
        form_list.insert(0, self.title)
        form_list.insert(0, "")

        curtab = self.SM_Tabs.currentIndex()
        tab = str(self.SM_Tabs.tabText(curtab))
        form_list = tuple(form_list)
        form_name = str(QInputDialog.getItem(None,"Move Tab to Form","Select form to move tab to:",form_list,0,False)[0])
        if form_name == "":
            ctypes.windll.user32.MessageBoxW(0,"No form selected","FAIL",0)
            return
        new_tab_name = str(QInputDialog.getText(None,"New Tab Name","New Tab Name:",QLineEdit.EchoMode.Normal,text=tab)[0])
        if not new_tab_name:
            ctypes.windll.user32.MessageBoxW(0,"No tab name entered. cancelling.","FAIL",0)
            return
        querylist = []
        querylist.append
        querylist.append("update tabs set formname = '"+str(form_name)+"', tab = '"+str(new_tab_name)+"' where formname = '"+str(self.title)+"' and tab = '"+str(tab)+"'")
        querylist.append("update buttons set formname = '"+str(form_name)+"', tab = '"+str(new_tab_name)+"' where formname = '"+str(self.title)+"' and tab = '"+str(tab)+"'")
        querylist.append("update buttons set formname='"+str(form_name)+"', tab = '"+str(new_tab_name)+"' where formname='"+str(self.title)+"' and tab='"+str(tab)+"'")
        querylist.append("update batchsequence set formname='"+str(form_name)+"', tab = '"+str(new_tab_name)+"' where formname='"+str(self.title)+"' and tab='"+str(tab)+"'")
        querylist.append("update buttonseries set formname='"+str(form_name)+"', tab = '"+str(new_tab_name)+"' where formname='"+str(self.title)+"' and tab='"+str(tab)+"'")
        for query in querylist:
            print(query)
            WriteSQL(query)
        self.Refresh()

    def Copy_Tab_form(self):
        #read forms from db not including current form
        forms = ReadSQL("select formname from forms")
        if len(forms)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No forms in DB. cancelling.","FAIL",0)
            logger.error("No forms in DB. returning.")
            return
        #create popup with dropdown box of forms
        form_list = []
        for form in forms:
            if form[0] != self.title:
                form_list.append(form[0])
        form_list.sort()
        form_list.insert(0, self.title)
        form_list.insert(0, "")


        curtab = self.SM_Tabs.currentIndex()
        tab = str(self.SM_Tabs.tabText(curtab))
        form_list = tuple(form_list)
        form_name = str(QInputDialog.getItem(None,"Copy Tab to Form","Select form to copy tab to:",form_list,0,False)[0])
        
        if form_name == "":
            ctypes.windll.user32.MessageBoxW(0,"No form selected. cancelling.","FAIL",0)
            return
        new_tab_name = str(QInputDialog.getText(None,"Copy Tab to Form","Enter new Tab name:", text=tab)[0])
        if new_tab_name == "":
            ctypes.windll.user32.MessageBoxW(0,"No form name entered. cancelling.","FAIL",0)
            return
        #get current tab
        #curtab index = self.Main_CB_Tabs.currentIndex()

        #get current tab data
        tab_data = ReadSQL(f"select formname, tab, tabsequence, grid, tabdesc, treepath, tabgroup, tabsize, taburl  from tabs where formname = '{self.title}' and tab = '{tab}'")
        if len(tab_data)<1:
            ctypes.windll.user32.MessageBoxW(0,"Tab not found. cancelling.","FAIL",0)
            return
        #get tab data
        tab_info = tab_data[0]

        for i, item in enumerate(tab_info):
            if item != None and type(item) != int:
                tab_info[i] = f"'{item}'"
            elif item == None:
                tab_info[i] = "NULL"
        # SELECT formname, tab, buttonname, buttonsequence, columnnum, buttondesc, buttongroup, active, treepath FROM buttons WHERE formname='tab_data[0]' AND tab='tab_data[1]'';
        button_data = ReadSQL(f"select buttonname, buttonsequence, columnnum, buttondesc, buttongroup, active, treepath FROM buttons WHERE formname={tab_info[0]} AND tab={tab_info[1]}")
        for item in button_data:
            for i, it in enumerate(item):
                if it != None and type(it) != int:
                    item[i] = f"'{it}'"
                elif it == None:
                    item[i] = "NULL"
                    
        if len(button_data)<1:
            logger.warning(f"No buttons found for tab: {tab_info[1]} on form {tab_info[0]}")
            button_data = []
        querylist = []
        #select formname, tab, buttonname, runsequence, folderpath, filename, type, source, target, databasepath, databasename, keypath, keyfile, treepath from batchsequence
        batch_data = ReadSQL(f"select formname, tab, buttonname, runsequence, folderpath, filename, type, source, target, databasepath, databasename, keypath, keyfile, treepath from batchsequence WHERE formname={tab_info[0]} AND tab={tab_info[1]}")
        if len(batch_data)<1:
            logger.warning(f"No batch sequence found for tab: {tab_info[1]} on form {tab_info[0]}")
            batch_data = []
        for item in batch_data:
            for i, it in enumerate(item):
                if it != None and type(it) != int:
                    item[i] = f"'{it}'"
                elif it == None:
                    item[i] = "NULL"
            if item[6] == "'assignseries'":
                item[7] = item[7].replace("'","")
                item[7] = f"'{item[7]}_{new_tab_name}'"
        #select formname, tab, buttonname, assignname, runsequence from buttonseries
        button_series_data = ReadSQL(f"select formname, tab, buttonname, assignname, runsequence from buttonseries WHERE formname={tab_info[0]} AND tab={tab_info[1]}")
        if len(button_series_data)<1:
            logger.warning(f"No button series found for tab: {tab_info[1]} on form {tab_info[0]}")
            button_series_data = []
        for item in button_series_data:
            for i, it in enumerate(item):
                if it != None and type(it) != int:
                    item[i] = f"'{it}'"
                elif it == None:
                    item[i] = "NULL"
                    #remove '' from item[3]

            item_x = item[3].replace("'","")
            item[3] = f"'{item_x}_{new_tab_name}'"

        
        #If batchsequence type = assignseries,
        querylist.append(f"insert into tabs (formname, tab, tabsequence, grid, tabdesc, treepath, tabgroup, tabsize, taburl) values ('{form_name}', '{new_tab_name}', {tab_info[2]}, {tab_info[3]}, {tab_info[4]}, {tab_info[5]}, {tab_info[6]}, {tab_info[7]}, {tab_info[8]})")

        for button in button_data:
            querylist.append(f"insert into buttons (formname, tab, buttonname, buttonsequence, columnnum, buttondesc, buttongroup, active, treepath) values ('{form_name}', '{new_tab_name}', {button[0]}, {button[1]}, {button[2]}, {button[3]}, {button[4]}, {button[5]}, {button[6]})")
        for batch in batch_data:
            querylist.append(f"insert into batchsequence (formname, tab, buttonname, runsequence, folderpath, filename, type, source, target, databasepath, databasename, keypath, keyfile, treepath) values ('{form_name}','{new_tab_name}', {batch[2]}, {batch[3]}, {batch[4]}, {batch[5]}, {batch[6]}, {batch[7]}, {batch[8]}, {batch[9]}, {batch[10]}, {batch[11]}, {batch[12]}, {batch[13]})")
        for series in button_series_data:
            querylist.append(f"insert into buttonseries (formname, tab, buttonname, assignname, runsequence) values ('{form_name}', '{new_tab_name}', {series[2]}, {series[3]}, {series[4]})")
        #execute querylist
        for query in querylist:
            print(query)
            WriteSQL(query, True)
        logger.debug("copy tab complete")
        self.Refresh()

    def Add_Tabto(self):
        #get a list of all tabnames where the formname is the same as the current formname
        tablist = ReadSQL("select tab from tabs where formname = '"+self.title+"' order by tabsequence")
        tablist_proper = []
        if len(tablist)>0:
            for tl in range(len(tablist)):
                tablist_proper.append(str(tablist[tl][0]))
        #make a selection box of tablist
        tab_selection = QInputDialog.getItem(None,"Select Tab","Tab:",tablist_proper,0,False)
        if not tab_selection[1]:
            return
        tab_selection = tab_selection[0]
        
        #enter button name
        button_name = str(tab_selection)
        if not button_name:
            return
        curtab = self.SM_Tabs.currentIndex()
        curtab_text = self.SM_Tabs.tabText(curtab)
        #insert into buttons where formname = current formname and tab = tab_selection
        WriteSQL("insert into buttons (formname, tab, buttonname) values ('"+self.title+"','"+curtab_text+"','"+button_name+"')")
        #insert into batchsequence type = tabto and tab = current seected tab
        WriteSQL("insert into batchsequence (formname, tab, buttonname, filename, type) values ('"+self.title+"','"+curtab_text+"','"+button_name+"','"+ tab_selection+"', 'tabto')")
        self.Refresh()

    def addsht2tbl(self):
        #get a list of all tabnames where the formname is the same as the current formname
        source_folder = QFileDialog.getExistingDirectory(None,"Select Source Folder")
        if not source_folder:
            return
        #enter button name
        target_folder = QFileDialog.getExistingDirectory(None,"Select Target Folder")
        if not target_folder:
            return
        if source_folder == target_folder:
            #error
            QMessageBox.warning(None,"Error","Source and Target folders cannot be the same")
            return
        button_name = QInputDialog.getText(None,"Enter Button Name","Button Name:", text= "sht2tbl "+source_folder.split("/")[-1])
        if not button_name[1]:
            return
        button_name = button_name[0]
        curtab = self.SM_Tabs.currentIndex()
        curtab_text = self.SM_Tabs.tabText(curtab)
        WriteSQL("insert into buttons (formname, tab, buttonname) values ('"+self.title+"','"+curtab_text+"','"+button_name+"')")
        WriteSQL("insert into batchsequence (formname, tab, buttonname, type, source, target) values ('"+self.title+"','"+curtab_text+"','"+button_name+"','sht2tbl','"+source_folder+"','"+target_folder+"')")     
        self.Refresh()

    def Add_Desc(self):
        #popup edit ask for description
        new_formdesc = str(QInputDialog.getText(None,"New description button","New description Button Text:",QLineEdit.EchoMode.Normal,"*")[0])

        if not new_formdesc:
            return
        curtab = self.SM_Tabs.currentIndex()
        
        curtab = str(self.SM_Tabs.tabText(curtab))
        #insert into buttons formane = self.title, tab = current tab, buttonname = newformdesc\
        WriteSQL("insert into buttons (formname, tab, buttonname) values ('"+self.title+"','"+curtab+"','"+new_formdesc+"')")
        #insert into batchsequence type = Descriptive_button
        WriteSQL("insert into batchsequence (formname, tab, buttonname, type) values ('"+self.title+"','"+curtab+"','"+new_formdesc+"','.')")
        self.Refresh()

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
        
    def actionEdit_mode_toggled(self,state = False):
        if state:

            self.edit_mode = True
            #find all pyqt object wqith sm_scrollarea in the name
            for obj in self.findChildren(QScrollArea):
                #set red
                obj.setStyleSheet("background-color: rgb(180, 125, 125);")

            
        else:
            self.edit_mode = False
            #find all pyqt object wqith sm_scrollarea in the name
            for obj in self.findChildren(QScrollArea):
                #remove backgeround color
                obj.setStyleSheet("background-color: None;")

    def Add_Seq(self):
        
        if self.cur_seq:
            ctypes.windll.user32.MessageBoxW(0,"Please stop current sequence first","FAIL",0)
            return
        self.cur_seq = Create_sequence(self)
        if self.cur_seq.crashed:
            self.cur_seq = None
            return
        self.cur_seq.show()

    def Add_Proc(self):
        cur_proc = Create_Process(self, pmgr, self.title, str(self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())))
        cur_proc.show()

    def Copy_File(self):
        curtab = self.SM_Tabs.currentIndex()
        if curtab<1:
            logger.error("current tab is first tab")
            ctypes.windll.user32.MessageBoxW(0,"current tab is first tab","Error",0)

            return
        new_file_master = QFileDialog.getOpenFileName(None,'Open file','')[0]
        if not new_file_master:
            return
        #new file without extension and path
        new_file = new_file_master.split("/")[-1]
        #remove file name and extension from path
        start_location = os.path.dirname(new_file_master)

        #combine elements in new_file_location
        
        #open select folder dialog
        end_location = QFileDialog.getExistingDirectory(None,'Open Folder','')
        if not end_location:
            return

        dest_name =  str(QInputDialog.getText(None,"Destination File Name","Destination File Name:",QLineEdit.EchoMode.Normal, new_file)[0])
        if not dest_name:
            return
        #copy file
        new_button = str(QInputDialog.getText(None,"New Copy Button Name","New Copy Button Name:",QLineEdit.EchoMode.Normal,"Copy " + dest_name)[0])
        if not new_button:
            return

  
        copy_exec = self.type_copy("Copy " + dest_name,new_file,start_location,end_location, 1, dest_name)
        
        if copy_exec:
            logger.success(f"{dest_name} has been copied to {end_location}")
            ctypes.windll.user32.MessageBoxW(0,dest_name +" has been copied to "+end_location,"File Copied",0)
        else:
            logger.error(f"{dest_name} has not been copied to {end_location}")
            return

        self.Add_EXE_FOR_COPY(start_location, end_location, new_file, new_button, dest_name)
        self.Refresh()

    def Add_EXE_FOR_COPY(self, start_location, end_location, new_file_name, new_button, dest_name):
        curtab = self.SM_Tabs.currentIndex()
        if curtab<1:
            
            logger.error("current tab is first tab")
            ctypes.windll.user32.MessageBoxW(0,"current tab is first tab","Error",0)
            return

        curtab = str(self.SM_Tabs.tabText(curtab))

       
        if not new_button:
            logger.error("new_button is None or ''")
            return

        if not new_file_name:
            logger.error("new_file_name is None or ''")
            return
        if not start_location:
            logger.error("start_location is None or ''")
            return
        if not end_location:
            logger.error("end_location is None or ''")
            return

        does_exist = ReadSQL("select buttonname from buttons where tab = '"+curtab+"' and buttonname = '"+new_button+"'")
        
        while len(does_exist)>0:
            new_button = str(QInputDialog.getText(None,"Choose Button Name","Name Taken, Please Choose another Button Name:",QLineEdit.EchoMode.Normal,"")[0])
            if new_button!=None and new_button!="":
                does_exist = ReadSQL("select buttonname from buttons where tab = '"+curtab+"' and buttonname = '"+new_button+"'")
            else:
                return

        maxbut = ReadSQL("select max(buttonsequence) from buttons where tab = '"+curtab+"'")
        if len(maxbut) < 1:
            logger.error("Max button is less then 1")

        print(end_location)
        idir = os.path.dirname(end_location)
        if idir[-1:]!="\\": #this is redundant as he is using os.path.dirname.
            idir = idir+"\\"
        ibase = os.path.basename(end_location)
        maxbut = maxbut[0][0] + 1 if maxbut[0][0] else 1
        maxcolumn = ReadSQL("select max(columnnum) from buttons where tab = '"+curtab+"'")
        if not maxcolumn:
            maxcolumn = "null"
        elif not maxcolumn[0][0]:
            maxcolumn = "null"
        else:
            maxcolumn = "1" #putting button automatically in column 1
        formtitle = self.title
        WriteSQL(f"""insert into buttons(formname,tab,buttonname,buttonsequence,columnnum) values('{formtitle}', '{curtab}','{new_button}',{maxbut},{maxcolumn}) """)
        start_location = start_location.replace("/","\\")
        end_location = end_location.replace("/","\\")
        WriteSQL(f"""insert into batchsequence(formname,tab,buttonname,runsequence, filename,type, source, target, databasename) values('{formtitle}', '{curtab}','{new_button}',1,'{new_file_name}','copy','{start_location}','{end_location}','{dest_name}') """) 

    def NewTab(self):
        new_tab = str(QInputDialog.getText(None,"New Tab Name","Name:",QLineEdit.EchoMode.Normal,"")[0])
        if not new_tab:
            return
        #get largest tabsequence based on formname\
        max_tab = ReadSQL("select max(tabsequence) from tabs where formname = '"+self.title+"'")
        
        #write to sql database the tab
        if not max_tab:
            max_tab =  1
            WriteSQL(f"""insert into tabs(formname,tab,tabsequence) values('{self.title}','{new_tab}',{max_tab})""")
        else:
            WriteSQL(f"""insert into tabs(formname,tab,tabsequence) values('{self.title}','{new_tab}',{max_tab[0][0]+1 if max_tab[0][0] else 1})""")
        self.Refresh()

    def ChangeTabSize(self):
        #get current tab size and check if it is above 900 px, then set to 800 px

        
        curtab = self.SM_Tabs.currentIndex()    
        curtab = str(self.SM_Tabs.tabText(curtab))
        cur_width = self.width()
        cur_height = self.height()
        WriteSQL(f"""update tabs set tabsize = '{cur_width},{cur_height}' where tab = '{curtab}' and formname = '{self.title}'""")
        tabsize = ReadSQL("select tabsize from tabs where formname = '"+
                    self.title+"' order by tabsequence asc")
        self.SM_Tabs.currentChanged.connect(partial(self.get_tab_change,tabsize))


    def NewTabUrl(self):
            curtab = self.SM_Tabs.currentIndex()
            curtab = str(self.SM_Tabs.tabText(curtab))
            #select taburl from tabs where formname and tab
            options = ["Classic URL", "Onenote URL", "Telegram URL"]
        
            option, ok = QInputDialog.getItem(None, "URL Type", "URL Type", options, 0, False)
            if not ok:
                return
            taburl = ReadSQL("select taburl from tabs where formname = '"+self.title+"' and tab = '"+curtab+"'")
            if len(taburl)>0:
                taburl = taburl[0][0]
            else:
                taburl = ""
            new_url = str(QInputDialog.getText(None,"New URL","URL:",QLineEdit.EchoMode.Normal,taburl)[0])
            if option == "Onenote URL":
                if new_url.find("onenote:")>-1:
                    new_url = new_url[new_url.find("onenote:"):]
                    print(new_url)
            if option == "Telegram URL":
                #spit by / and take the last and second lsat items
                split_url = new_url.split("/")
                if len(split_url)>2:
                    post = split_url[-1]
                    channel = split_url[-2]
                    new_url = f"tg://privatepost?channel={channel}&post={post}"

                    
            #update tab change tab_url to new_url
            WriteSQL(f"""update tabs set taburl = '{new_url}' where formname = '{self.title}' and tab = '{curtab}'""")
            
    def NewTabFolder(self):
            curtab = self.SM_Tabs.currentIndex()
            curtab = str(self.SM_Tabs.tabText(curtab))
            #select taburl from tabs where formname and tab
            treepath = ReadSQL("select treepath from tabs where formname = '"+self.title+"' and tab = '"+curtab+"'")
            if len(treepath)>0:
                treepath = treepath[0][0]
            else:
                taburl = ""
            new_folder = str(QFileDialog.getExistingDirectory(None,"Select Folder",treepath))
            #update tab change tab_url to new_url
            WriteSQL(f"""update tabs set treepath = '{new_folder}' where formname = '{self.title}' and tab = '{curtab}'""")
            self.Refresh()

    def OpenTabUrl(self):
        curtab = self.SM_Tabs.currentIndex()
        curtab = str(self.SM_Tabs.tabText(curtab))
        #select taburl from tabs where formname = '"+self.title+"' and tab = '"+self.Main_CB_Tabs.currentText()+"'")
        print("select taburl from tabs where formname = '"+self.title+"' and tab = '"+curtab+"'")
        taburl = ReadSQL("select taburl from tabs where formname = '"+self.title+"' and tab = '"+curtab+"'")
        if taburl[0][0]:
            taburl = taburl[0][0]
            webbrowser.open(taburl)
        else:
            self.NewTabUrl()

    def Add_Folder(self):
        curtab = self.SM_Tabs.currentIndex()
        curtab = str(self.SM_Tabs.tabText(curtab))
        new_file = QFileDialog.getExistingDirectory(None,'Open Folder','')
        if len(new_file)<1:
            logger.error("No folder selected")
            return
        if len(new_file[0])<1:
            logger.error("No folder selected")
            return
        maxbut = ReadSQL("select max(buttonsequence) from buttons where tab = '"+curtab+"'")
        print(new_file)
        idir = os.path.dirname(new_file)
        if idir[-1:]!="//": #this is redundant as he is using os.path.dirname.
            idir = idir+"/"
        ibase = os.path.basename(new_file)
        logger.success(ibase + " " + idir)
        new_button = str(QInputDialog.getText(None,"New Folder Button Name","Name:",QLineEdit.EchoMode.Normal,"Folder " + ibase)[0])
        if not new_button:
            logger.error("ButtonName is None")
            return
        does_exist = ReadSQL("select buttonname from buttons where tab = '"+curtab+"' and buttonname = '"+new_button+"'")
        while len(does_exist)>0:
            ctypes.windll.user32.MessageBoxW(0,"Button already exists","Error",0)
            new_button = str(QInputDialog.getText(None,"New Folder Button Name","Name:",QLineEdit.EchoMode.Normal,"")[0])
            if new_button!=None and new_button!="":
                does_exist = ReadSQL("select buttonname from buttons where tab = '"+curtab+"' and buttonname = '"+new_button+"'")
            else:
                return
        maxbut = maxbut[0][0] + 1 if maxbut[0][0] else 1
        maxcolumn = ReadSQL("select max(columnnum) from buttons where tab = '"+curtab+"'")
        if not maxcolumn:
            maxcolumn = "null"
        elif not maxcolumn[0][0]:
            maxcolumn = "null"
        else:
            maxcolumn = "1" #putting button automatically in column 1
        formtitle = self.title
        WriteSQL(f"""insert into buttons(formname,tab,buttonname,buttonsequence,columnnum) values('{formtitle}', '{curtab}','{new_button}',{maxbut},{maxcolumn}) """)
        WriteSQL("insert into batchsequence(formname,tab,buttonname,runsequence,folderpath,type) values('"+formtitle+"','"+curtab+"','"+str(new_button)+"',1,'"+idir+ibase+"/','folder')")    
        self.Refresh()
    
    def Add_url(self):
        curtab = self.SM_Tabs.currentIndex()
        curtab = str(self.SM_Tabs.tabText(curtab))
        options = ["Classic URL", "Onenote URL", "Telegram URL"]
     
        option, ok = QInputDialog.getItem(None, "URL Type", "URL Type", options, 0, False)
        if not ok:
            return
        new_url = str(QInputDialog.getText(None,"New URL","URL:",QLineEdit.EchoMode.Normal,"")[0])
        if not new_url:
            return

        #check for text onenote: in new_url and remove all text before it   
        if option == "Onenote URL":
            if new_url.find("onenote:")>-1:
                new_url = new_url[new_url.find("onenote:"):]
                print(new_url)
        if option == "Telegram URL":
            #spit by / and take the last and second lsat items
            split_url = new_url.split("/")
            if len(split_url)>2:
                post = split_url[-1]
                channel = split_url[-2]
                new_url = f"tg://privatepost?channel={channel}&post={post}"

        new_button = str(QInputDialog.getText(None,"New URL Button Name","Name:",QLineEdit.EchoMode.Normal,"")[0])
        if not new_button:
            return
        maxbut = ReadSQL("select max(buttonsequence) from buttons where tab = '"+curtab+"'")
        if len(maxbut) < 1:
            logger.error("Max button is less then 1")
        maxbut = maxbut[0][0] + 1 if maxbut[0][0] else 1
        maxcolumn = ReadSQL("select max(columnnum) from buttons where tab = '"+curtab+"'")
        if not maxcolumn:
            maxcolumn = "null"
        elif not maxcolumn[0][0]:
            maxcolumn = "null"
        else:
            maxcolumn = "1"
        formtitle = self.title
        WriteSQL(f"""insert into buttons(formname,tab,buttonname,buttonsequence,columnnum) values('{formtitle}', '{curtab}','{new_button}',{maxbut},{maxcolumn}) """)

        WriteSQL(f"""insert into batchsequence(formname,tab,buttonname,runsequence,type, source) values('{formtitle}', '{curtab}','{new_button}',1,'url','{new_url}') """)
        self.Refresh()
        
    def AboutMsg_Try(self):
        try:
            self.AboutMsg()
        except Exception as e:
            logger.error("Error: "+str(e))

    def AboutMsg(self):
        ctypes.windll.user32.MessageBoxW(0,f"Version: {version} \nForm: {self.title}","About ExAuT - OnInO Technologies",0)

    def RefreshHandler(self):
        self.Refresh()
        self.Refresh()


    def button_context_menu(self,button):
        menu = QtWidgets.QMenu(self)
        #tab name is current active tab
        tabname = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        #button name is the text in the button
        button_name = button.text()

        menu.addAction("Edit", partial(self.on_click_button,
                                       self.title,
                                       tabname,
                                       button_name,
                                       button.objectName(),
                                       2,
                                       button))
        menu.addAction("Copy", partial(self.on_click_button,
                                         self.title,
                                         tabname,
                                         button_name,
                                         button.objectName(),
                                         3,
                                        button))
        menu.addAction("Move", partial(self.on_click_button,
                                         self.title,
                                         tabname,
                                         button_name,
                                         button.objectName(),
                                         4,
                                         button))
        menu.addAction("Duplicate", partial(self.on_click_button,
                                         self.title,
                                         tabname,
                                         button_name,
                                         button.objectName(),
                                         5,
                                        button))

        menu.addAction("Edit Layout", self.layout_editor)
        menu.exec(QtGui.QCursor.pos())
                                               
    def button_context_menu_handler(self,button,item):
        None

    def get_tab_change(self,n):
        if self.refreshing:
            return
        if len(n)>0 and self.SM_Tabs.currentIndex() < len(n):
            n = n[self.SM_Tabs.currentIndex()]
            n = n[0]
            if n!=None and n!="":
                n = n.split(',')
                if len(n)>1:
                    try:
                        n[0] = int(n[0])
                        n[1] = int(n[1])
                        self.resize(n[0],n[1])
                    except Exception as e:
                        logger.error(str(e))
            else:
                self.resize(650,300)
        else:
            self.resize(650,300)
    
    #Main: Change Tab ComboBox
    def on_tab_change(self):
        
        n = str(self.Main_CB_Tabs.currentText())
        logger.debug(n)
        buttonlist = ReadSQL("select buttonname from buttons where formname = '"+
                             self.title+"' and tab = '"+n+"'")
        self.Main_CB_Buttons.clear()
        self.Main_CB_Buttons.addItem("")
        if len(buttonlist)>0:
            for bl in range(len(buttonlist)):
                self.Main_CB_Buttons.addItem(str(buttonlist[bl][0]))

    #Main: Change Button ComboBox
    def on_button_change(self):
        n = str(self.Main_CB_Buttons.currentText())
        if len(n)>0:
            bh = ReadSQL("pragma table_info('batchsequence')")
            bs = ReadSQL("select runsequence,folderpath,filename,type,source,"+
                         "target,databasepath,databasename,keypath,"+
                         "keyfile from batchsequence where formname = '"+self.title+
                         "' and tab = '"+str(self.Main_CB_Tabs.currentText())+
                         "' and buttonname = '"+n+"'")
            header = []
            for h in range(3,len(bh)):
                header.append(bh[h][1])
            self.Main_Table.setColumnCount(len(bs[0]))
            self.Main_Table.setRowCount(len(bs))
            self.Main_Table.setHorizontalHeaderLabels(header)
            for i in range(len(bs)):
                for j in range(len(bs[0])):
                    self.Main_Table.setItem(i,j,QTableWidgetItem(str(bs[i][j])))
        else:
            bh = ReadSQL("pragma table_info('batchsequence')")
            if len(bh)>0:
                header = []
                for h in range(3,len(bh)):
                    header.append(bh[h][1])
            self.Main_Table.setColumnCount(0)
            self.Main_Table.setRowCount(0)
            for rr in range(self.Main_Table.rowCount()):
                self.Main_Table.removeRow(rr)

    #Main: Delete record
    def on_DeleteRec(self):
        if len(str(self.Main_CB_Tabs.currentText()))>0 and len(str(self.Main_CB_Buttons.currentText()))>0:
            tname = str(self.Main_CB_Tabs.currentText())
            bname = str(self.Main_CB_Buttons.currentText())
            bh = ReadSQL("pragma table_info('batchsequence')")
            bs = ReadSQL("select runsequence,folderpath,filename,type,source,target,"+
                         "databasepath,databasename,keypath,keyfile "+
                         "from batchsequence where formname = '"+self.title+"' and tab = '"+
                         tname+"' and buttonname = '"+bname+"'")
            bt = str(bs[0][3])
            for i in self.Main_Table.selectionModel().selectedRows():
                n = str(self.Main_Table.item(i.row(),0).text())
                WriteSQL("delete from batchsequence where formname = '"+self.title+"' and tab = '"+tname+
                         "' and buttonname = '"+bname+"' and runsequence = "+n+" and type = '"+bt+"'")
            self.Main_Table.deleteLater()
            self.Main_Table = QtWidgets.QTableWidget(self.scrollAreaWidgetContents_2)
            self.Main_Table.setObjectName("tableMain")
            self.gridLayout_4.addWidget(self.Main_Table, 0, 0, 1, 1)
            self.on_button_change()

    #Main: Change Cell
    def on_CellChange(self):
        logger.debug("cell changed")
        if len(str(self.Main_CB_Tabs.currentText()))>0 and len(str(self.Main_CB_Buttons.currentText()))>0:
            tname = str(self.Main_CB_Tabs.currentText())
            bname = str(self.Main_CB_Buttons.currentText())
            h = ReadSQL("pragma table_info('batchsequence')")
            r = self.Main_Table.currentRow()
            c = self.Main_Table.currentColumn()+3
            if r>=0 and c>2:
                txt = self.Main_Table.item(self.Main_Table.currentRow(),self.Main_Table.currentColumn()).text()
                if txt=='':
                    txt = "null"
                    self.Main_Table.setItem(self.Main_Table.currentRow(),self.Main_Table.currentColumn(),QTableWidgetItem("None"))
                else:
                    tmp = h[c][2]
                    if tmp.find("char")>=0 or tmp.find("CHAR")>=0 or tmp.find("datetime")>=0 or tmp.find("DATETIME")>=0 or tmp.find("text")>=0 or tmp.find("TEXT")>=0:
                        txt = "'"+txt+"'"
                WriteSQL("update batchsequence set "+h[c][1]+" = "+txt+" where formname = '"+self.title+"' and tab = '"+
                         tname+"' and buttonname = '"+bname+"' and runsequence = "+str(self.Main_Table.item(r,0).text()))
    
    def on_click_button(self,pname,tname,bname,objn,mode=1, button = None): ##pname = SGX, ##

        #self.SM_Grid.findChild(QPushButton,objn).setStyleSheet("background: tomato")
        bseq = ReadSQL(f"""select folderpath,filename,type,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname
        from batchsequence where formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}' order by runsequence asc""")
        
        if self.edit_mode or mode==2:
            self.edit_button(bseq,pname,tname,bname,objn,mode)
            button.setStyleSheet("background: None")

        elif len(bseq) == 0:
            ctypes.windll.user32.MessageBoxW(0, "Batchsequence not found for button \""+bname+"\" in tab \""+tname+"\" in form \""+pname+"\"", "Error", 0)
            button.setStyleSheet("background: None")

        elif mode == 3:
            self.copy_button(bseq, pname, tname, bname, objn, mode)
            button.setStyleSheet("background: None")

        elif mode == 4:
            self.move_button(bseq, pname, tname, bname, objn, mode)
            button.setStyleSheet("background: None")

        elif mode == 5:
            self.copy_button(bseq, pname, tname, bname, objn, mode, duplicate=True)
            button.setStyleSheet("background: None")

        elif self.cur_seq:
                self.cur_seq.add_button(tname,bname)
                button.setStyleSheet("background: None")

        else:
            if len(bseq)>1:
                mode = "sequence"
            for pf in range(len(bseq)):
                if str(bseq[pf][2])=="assignseries":
                    #use qthread to run handle_seq
                    newthread = Sequence_Thread(self, bname, bseq, pf, button)
                    newthread.start()
                    self.threads.append(newthread)
                elif pmgr.exists(bseq[pf][2]):
                    if mode != "sequence": 
                        newthread = Button_Thread(self,bseq,pf,button)
                        newthread.start()
                        self.threads.append(newthread)
                    else:
                        x = pmgr.call(bseq[pf][2], bseq[pf])   
                        return(x, bseq[pf][2])     
                else:
                    run_types(self, bseq, bname, pname, tname, ReadSQL)
                    button.setStyleSheet("background: None")

    def edit_button(self, bseq,pname,tname,bname,objn, mode = "edit"):
        if len(bseq) == 0:
            edit_pop = Edit_Popup(self, bseq,pname,tname,bname,objn)
            edit_pop.show()
            return
        if bseq[0][2] == "assignseries":
            #[bseq[0][2], pname, tname, bname, objn] as aray
            self.cur_seq = Create_sequence(self, edit=True, data = {"source":bseq[0][3], "tab":tname, "buttonname":bname})

            edit_popup = Edit_Popup(self, bseq, pname, tname, bname, objn)
            edit_popup.show()

            if self.cur_seq.crashed:
                self.cur_seq = None
            else:
                self.cur_seq.show()

            self.actionEdit_mode_toggled(False)
            return
        edit_pop = Edit_Popup(self, bseq,pname,tname,bname,objn)
        edit_pop.show()

    def copy_button(self, bseq, pname, tname, bname, objn, mode, duplicate = False):
        bseq0 = bseq
        pname0 = pname
        tname0 = tname
        bname0 = bname
        objn0 = objn
        mode0 = mode

        #read forms from db not including current form
        forms = ReadSQL("select formname from forms")
        if len(forms)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No forms in DB. cancelling.","FAIL",0)
            logger.error("No forms in DB. returning.")
            return
        #create popup with dropdown box of forms
        #create popup with dropdown box of forms
        if not duplicate:
            form_list = []
            for form in forms:
                if form[0] != self.title:
                    form_list.append(form[0])
            form_list.sort()
            form_list.insert(0, self.title)
            form_list.insert(0, "")
            curtab = self.SM_Tabs.currentIndex()
            tab = str(self.SM_Tabs.tabText(curtab))
            form_list = tuple(form_list)
            form_name = str(QInputDialog.getItem(None,"Copy button to Form","Select form to copy button to:",form_list,0,False)[0])
            
            if form_name == "":
                ctypes.windll.user32.MessageBoxW(0,"No form selected. cancelling.","FAIL",0)
                return

            tabs = ReadSQL("select tab from tabs where formname = '"+form_name+"'")
            if len(tabs)<1:
                #error
                ctypes.windll.user32.MessageBoxW(0,"No tabs in DB. cancelling.","FAIL",0)
                logger.error("No tabs in DB. returning.")
                return
            #create popup with dropdown box of forms
            #create popup with dropdown box of forms
            tab_list = []
            for tab in tabs:
                if tab[0] != self.title:
                    tab_list.append(tab[0])
            tab_list.sort()
            tab_list.insert(0, self.title)
            tab_list.insert(0, "")
            curtab = self.SM_Tabs.currentIndex()
            tab_list = tuple(tab_list)
            tab_name = str(QInputDialog.getItem(None,"Copy button to Form","Select tab to copy button to:",tab_list,0,False)[0])
            
            if tab_name == "":
                ctypes.windll.user32.MessageBoxW(0,"No tab selected. cancelling.","FAIL",0)
                return
            
            #get current tab
            #curtab index = self.Main_CB_Tabs.currentIndex()

            #bseq "folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11
            #select from buttons buttonsm(pname,tname,bname,objn
        if duplicate:
            form_name = self.title
            tab_name = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())

        orig_btn_data = ReadSQL(f"select * from buttons where formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}'")
        if len(orig_btn_data)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No button in DB. cancelling.","FAIL",0)
            logger.error("No button in DB. returning.")
            return
        for item in orig_btn_data:
            for i, it in enumerate(item):
                if it != None and type(it) != int:
                    item[i] = f"'{it}'"
                elif it == None:
                    item[i] = "NULL"
        orig_batchsequence_data = ReadSQL(f"select * from batchsequence where  formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}'")
        if len(orig_batchsequence_data)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No button in DB. cancelling.","FAIL",0)
            logger.error("No batchsequence in DB. returning.")
            return
        for item in orig_batchsequence_data:
            for i, it in enumerate(item):
                if it != None and type(it) != int:
                    item[i] = f"'{it}'"
                elif it == None:
                    item[i] = "NULL"
        orig_btn_data = tuple(orig_btn_data[0])
        orig_batchsequence_data = tuple(orig_batchsequence_data[0])
        #create new button
        #insert into buttons
        #insert into batchsequence 0-8
        if tab_name == tname:
            #remove * from bname
            bname = f"'{bname}_copy'"
        else:
            bname = f"'{bname}'"
        newbutton_query = f"insert into buttons values('{form_name}','{tab_name}',{bname},{orig_btn_data[3]},{orig_btn_data[4]},{orig_btn_data[5]},{orig_btn_data[6]},{orig_btn_data[7]},{orig_btn_data[8]})"
        newbatchsequence_query = f"insert into batchsequence values('{form_name}','{tab_name}',{bname},{orig_batchsequence_data[3]},{orig_batchsequence_data[4]},{orig_batchsequence_data[5]},{orig_batchsequence_data[6]},{orig_batchsequence_data[7]},{orig_batchsequence_data[8]},{orig_batchsequence_data[9]},{orig_batchsequence_data[10]},{orig_batchsequence_data[11]},{orig_batchsequence_data[12]},{orig_batchsequence_data[13]})"
        WriteSQL(newbutton_query)
        WriteSQL(newbatchsequence_query)
        self.Refresh()
        logger.success(f"Button {bname} copied to {form_name} : {tab_name}")
        if duplicate:
            #remove all ' from bname
            bname = bname.replace("'","")
            self.edit_button(bseq0,pname0,tname0,bname,objn0,mode0)
     
    def move_button(self, bseq, pname, tname, bname, objn, mode):

        #read forms from db not including current form
        forms = ReadSQL("select formname from forms")
        if len(forms)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No forms in DB. cancelling.","FAIL",0)
            logger.error("No forms in DB. returning.")
            return
        #create popup with dropdown box of forms
        form_list = []
        for form in forms:
            form_list.append(form[0])
        form_list.sort()
        form_list.insert(0,"")
        curtab = self.SM_Tabs.currentIndex()
        tab = str(self.SM_Tabs.tabText(curtab))
        form_list = tuple(form_list)
        form_name = str(QInputDialog.getItem(None,"move button to Form","Select form to move button to:",form_list,0,False)[0])
        
        if form_name == "":
            ctypes.windll.user32.MessageBoxW(0,"No form selected. cancelling.","FAIL",0)
            return

        tabs = ReadSQL("select tab from tabs where formname = '"+form_name+"' and tab != '"+tab+"'")
        if len(tabs)<1:
            #error
            ctypes.windll.user32.MessageBoxW(0,"No tabs in DB. cancelling.","FAIL",0)
            logger.error("No tabs in DB. returning.")
            return
        #create popup with dropdown box of forms
        tab_list = []
        for tab in tabs:
            tab_list.append(tab[0])
        tab_list.sort()
        tab_list.insert(0,"")
        curtab = self.SM_Tabs.currentIndex()
        tab_list = tuple(tab_list)
        tab_name = str(QInputDialog.getItem(None,"move button to form","Select tab to move button to:",tab_list,0,False)[0])
        
        if tab_name == "":
            ctypes.windll.user32.MessageBoxW(0,"No tab selected. cancelling.","FAIL",0)
            return
        #get current tab
        #curtab index = self.Main_CB_Tabs.currentIndex()

        #bseq "folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11
        #select from buttons buttonsm(pname,tname,bname,objn
        #orig_btn_data = ReadSQL(f"select * from buttons where formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}'")
        
        #orig_batchsequence_data = ReadSQL(f"select * from batchsequence where  formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}'")
        update_batchsequence_query = f"update batchsequence set formname = '{form_name}', tab = '{tab_name}' where formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}'"
        update_buttons_query = f"update buttons set formname = '{form_name}', tab = '{tab_name}' where formname = '{pname}' and tab = '{tname}' and buttonname = '{bname}'"
        WriteSQL(update_batchsequence_query)
        WriteSQL(update_buttons_query)

    def ExportExcel(self):
        eng = ReadSQL("select * from sqlengine")
        print("sqlengine data?")
        print(eng)
        if len(eng)<=0:
            ctypes.windll.user32.MessageBoxW(0,"No record exists in sqlengine table?","Failed sql!",0)
        else:
            eseq = ReadSQL("select * from pyexcelmenu where (type = 'Export' or type = 'export') order by runsequence asc")
            for exf in range(len(eseq)):
                temp00 = str(eseq[exf][2])
                if os.path.exists(temp00)==False:
                    ctypes.windll.user32.MessageBoxW(0,temp00+" does not exist?","Failed Tools/Export to Excel!",0)
                elif os.path.exists(str(eseq[exf][4])+"\\"+str(eseq[exf][5]))==False:
                    ctypes.windll.user32.MessageBoxW(0,str(eseq[exf][4])+"\\"+str(eseq[exf][5])+" does not exist?","Failed Tools/Export to Excel!",0)
                else:
                    x = Excel_Popup(logger, ctypes, self, 1,str(eseq[exf][2])+"\\"+str(eseq[exf][3]),str(eng[0][0]),str(eseq[exf][4])+"\\"+str(eseq[exf][5]),str(eseq[exf][2]),"",0,1)
                    x.show()
                    
    def ImportExcel(self):
        new_button = str(QInputDialog.getText(None,"Confirm Import",'Type "yes" to confirm import',QLineEdit.EchoMode.Normal,"")[0])
        if new_button.lower() != "yes":
            return
        eng = ReadSQL("select * from sqlengine")
        print("sqlengine data?")
        print(eng)
        if len(eng)<=0:
            ctypes.windll.user32.MessageBoxW(0,"No record exists in sqlengine table?","Failed sql!",0)
        else:
            iseq = ReadSQL("select * from pyexcelmenu where (type = 'Import' or type = 'import') order by runsequence asc")
            for imf in range(len(iseq)):
                temp00 = str(iseq[imf][2])
                if os.path.exists(temp00)==False:
                    ctypes.windll.user32.MessageBoxW(0,temp00+" does not exist?","Failed Tools/Import from Excel!",0)
                elif os.path.exists(str(eng[0][0]))==False:
                    ctypes.windll.user32.MessageBoxW(0,str(eng[0][0])+" does not exist?","Failed Tools/Import from Excel!",0)
                elif os.path.exists(str(iseq[imf][4])+"\\"+str(iseq[imf][5]))==False:
                    ctypes.windll.user32.MessageBoxW(0,str(iseq[imf][4])+"\\"+str(iseq[imf][5])+" does not exist?","Failed Tools/Import from Excel!",0)
                else:
                    x = Excel_Popup(logger,ctypes,self, 0,str(iseq[imf][2])+"\\"+str(iseq[imf][3]),str(eng[0][0]),str(iseq[imf][4])+"\\"+str(iseq[imf][5]),str(iseq[imf][2]),"",0,0)
                    x.show()
        self.Refresh()
                        
                        
    def Open_File_Tree(self):
        curtab = self.SM_Tabs.currentIndex()

        tabpath = ReadSQL("select treepath from tabs where tab = '"+self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())+"'")
        if len(tabpath)>0:
        
            tabpath = tabpath[0][0]
            if tabpath==None:
                tabpath = ""
            if tabpath[-1:]=="\\":
                tabpath = tabpath[:-1]
            if tabpath!="":
                folder = tabpath
                if os.path.exists(folder):
                    #if folder starts with two forwardslashes
                    if folder[0:2] in("//","\\\\"):
                        logger.debug("network drive detected")
                        folder = folder.replace("/","\\")
                        os.system("explorer " + folder)
                        
                    else:
                        current_dir = os.getcwd()
                        os.chdir(folder)
                        os.system(f"start .")
                        os.chdir(current_dir)
                    
                    logger.success(f"opened folder {folder}")
                    return True
                else:
                    logger.error(f"folder {folder} does not exist")
                    return False
            else:
                #ask user if they want toadd a newtabfolder
                askifadd = QtWidgets.QMessageBox.question(self, 'Add New Tab Folder',
                                                            "Do you want to add a new tab folder?",
                                                            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                                                            QtWidgets.QMessageBox.StandardButton.No)
                if askifadd==QtWidgets.QMessageBox.StandardButton.Yes:
                    self.NewTabFolder()


    def Add_EXE(self):
        curtab = self.SM_Tabs.currentIndex()
        curtab = str(self.SM_Tabs.tabText(curtab))
        new_file = QFileDialog.getOpenFileName(None,'Open file','',"EXE Files (*.exe);;Excel Files (*.xlsx *.xlsm *.xlsb *.xls);;SQLite DB Files (*.db);;All Files (*.*)")
        if len(new_file[0])<1:
            logger.error("No file selected")
            return
        new_file = new_file[0].replace("/","\\")
        maxbut = ReadSQL("select max(buttonsequence) from buttons where tab = '"+curtab+"'")
        if len(maxbut) < 1:
            logger.error("Max button is less then 1")
        print(new_file)
        idir = os.path.dirname(new_file)
        if idir[-1:]!="\\": #this is redundant as he is using os.path.dirname.
            idir = idir+"\\"
        ibase = os.path.basename(new_file)
        logger.success(ibase + " " + idir)
        new_button = str(QInputDialog.getText(None,"New EXE ButtonName","Name:",QLineEdit.EchoMode.Normal,"run " + ibase)[0])
        if not new_button:
            logger.error("ButtonName is None")
            return
        does_exist = ReadSQL("select buttonname from buttons where tab = '"+curtab+"' and buttonname = '"+new_button+"'")
        while len(does_exist)>0:
            new_button = str(QInputDialog.getText(None,"New EXE ButtonName","Name:",QLineEdit.EchoMode.Normal,"")[0])
            if new_button!=None and new_button!="":
                does_exist = ReadSQL("select buttonname from buttons where tab = '"+curtab+"' and buttonname = '"+new_button+"'")
            else:
                return
        maxbut = maxbut[0][0] + 1 if maxbut[0][0] else 1
        maxcolumn = ReadSQL("select max(columnnum) from buttons where tab = '"+curtab+"'")
        if not maxcolumn:
            maxcolumn = "null"
        elif not maxcolumn[0][0]:
            maxcolumn = "null"
        else:
            maxcolumn = "1" #putting button automatically in column 1
        formtitle = self.title
        WriteSQL(f"""insert into buttons(formname,tab,buttonname,buttonsequence,columnnum) values('{formtitle}', '{curtab}','{new_button}',{maxbut},{maxcolumn}) """)
        WriteSQL("insert into batchsequence(formname,tab,buttonname,runsequence,folderpath,filename,type) values('"+formtitle+"','"+curtab+"','"+str(new_button)+"',1,'"+idir+"','"+ibase+"','exe')")    
        self.Refresh()
     
    def ReadPG(self,query,attempts=12,sec=1):
        val = []
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            for result in results:
                val.append(list(result))
            return(val)
        except Exception as e4:
            print(query)
            print(str(e4))
            return(val)
            '''
            for i in range(0,attempts):
                try:
                    self.cursor.execute(query)
                    results = self.cursor.fetchall()
                    for result in results:
                        val.append(list(result))
                    return(val)
                except Exception as e4:
                    if i==attempts-1:
                        print(query)
                        print(str(e4))
                        return(val)
                    else:
                        time.sleep(sec)
                        continue
            '''

    # Write to Postgres
    def WritePG(self,query,attempts=12,sec=1,box=False):
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e4:
            print(query)
            print(str(e4))
            self.conn.rollback()
            '''
            for i in range(0,attempts):
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                except Exception as e4:
                    if i==attempts-1:
                        print(query)
                        print(str(e4))
                        return(val)
                    else:
                        time.sleep(sec)
                        continue
            '''

    def isSQLiteText(self,n,field):
        if field==None:
            return("null")
        elif n[0:4]=="char" or n[0:4]=="CHAR" or n[0:7]=="varchar" or n[0:7]=="VARCHAR" or n=="text" or n=="TEXT" or n=="datetime" or n=="DATETIME":
            field = str(field)
            if "'" in field:
                field = field.replace("'","''")
            return "'"+field+"'"
        else:
            field = str(field)
            if "'" in field:
                field = field.replace("'","''")
            return field

    def PG_Function(self,runfile,pg_data,inputdata,err,mode):
        pg_data = pg_data.split('|')
        txt = open(runfile).read()
        if mode==0:
            os.system("SET PGPASSWORD="+str(PG_PASS)+"& psql -h "+str(pg_data[2])+" -p "+str(pg_data[3])+" -U "+str(pg_data[1])+" -d "+str(pg_data[0])+" < \""+runfile+"\"")
        elif mode==1:
            if inputdata==None or inputdata=="":
                ctypes.windll.user32.MessageBoxW(0,"No variables specified in source?","Failed sql: "+bname+"! \\"+err,0)
            else:
                customfile = str(os.path.dirname(runfile))+"\\%%%"+str(os.path.basename(runfile))
                inputdata = inputdata.split('|')
                for i in range(len(inputdata)):
                    txt = txt.replace("%var"+str(i+1)+"%",inputdata[i])
                os.system("type NUL > "+customfile)
                if os.path.exists(customfile)==True:
                    newtxt = open(customfile,'w+')
                    newtxt.write(txt)
                    newtxt.close()
                try:
                    os.system("SET PGPASSWORD="+str(PG_PASS)+"& psql -h "+str(pg_data[2])+" -p "+str(pg_data[3])+" -U "+str(pg_data[1])+" -d "+str(pg_data[0])+" < \""+customfile+"\"")
                    os.remove(customfile)
                except OSError as e:
                    ctypes.windll.user32.MessageBoxW(0,"Error removing "+customfile+", permission issue? \\"+err,"",1)
    
#type handlers 
    def type_copy(self, batch_name,file_name,file_source,file_destination,run_sequence,new_name): 
        full_file_source = file_source+"\\"+file_name 
        full_file_destination = file_destination+"\\"+new_name
        fail_handler = "Failed copy: "+batch_name+"! \\"+str(run_sequence)    
        if not os.path.exists(full_file_source):
            ctypes.windll.user32.MessageBoxW(0,full_file_source+" source does not exist?",fail_handler,0)
            return False
        if not os.path.exists(file_destination): 
            os.system("mkdir \""+file_destination+"\"") 
            if os.path.exists(file_destination)==False: 
                ctypes.windll.user32.MessageBoxW(0,file_destination+" target does not exist?",fail_handler,0) 
                return False
        try:
            shutil.copy2(full_file_source,full_file_destination) #copy file
            return True
        except:
            if not os.path.exists(full_file_destination): 
                ctypes.windll.user32.MessageBoxW(0,f"Problem copying {full_file_source} to {full_file_destination}?",fail_handler,0)  
                return False
            else: 
                ctypes.windll.user32.MessageBoxW(0,f"Problem copying {full_file_source} to {full_file_destination}. Check if file is open.",fail_handler,0) 
                return False

        return(False)

    def layout_editor(self):
        if self.edit_layout != None:
            try:
                self.edit_layout.close()
                self.edit_layout = Edit_Layout(self)
                self.edit_layout.show()
            except:
                pass
        else:
            self.edit_layout = Edit_Layout(self)
            self.edit_layout.show()


class Sequence_Thread(QThread):
    def __init__(self, parent_, bname, bseq,pf, button) -> None:
        super(QThread, self).__init__()
        self.parent_ = parent_
        self.bname = bname
        self.bseq = bseq
        self.pf = pf
        self.button = button
            
    def run(self):
        if str(self.bseq[self.pf][3])==None:
            ctypes.windll.user32.MessageBoxW(0,str(self.bseq[self.pf][3])+" button series name not assigned in source?","Failed assignseries: "+self.bname+"! \\"+str(self.bseq[self.pf][9]),0)
        else:
            get_series = ReadSQL("select formname,tab,buttonname from buttonseries where assignname = '"+str(self.bseq[self.pf][3])+"' and formname = '"+self.parent_.title+"' order by runsequence asc")
            if len(get_series)<=0:
                ctypes.windll.user32.MessageBoxW(0,"No assigned buttons found for "+str(self.bseq[self.pf][3])+" series assignment?","Failed assignseries: "+self.bname+"! \\"+str(self.bseq[self.pf][9]),0)
            else:
                ctime = perf_counter()
                for i in range(len(get_series)):
                    butp = get_series[i][0]
                    butt = get_series[i][1]
                    butb = get_series[i][2]
                    
                    if butp!=None and butp!="":
                        res,type_ = self.parent_.on_click_button(butp,butt,butb,"", mode="sequence")
                        if res==False:

                            if type_ == "warning":
                                logger.warning("Chose to stop sequence")
                                break
                            
                endtime = perf_counter()
                #endtime in x minutes and y seconds

                logger.success(f"completed button sequence {self.bname} in {round((endtime-ctime),2)} seconds") 
        self.button.setStyleSheet("background: None")




class Button_Thread(QThread):
    def __init__(self, parent_, bseq, pf, button) -> None:
        super(QThread, self).__init__()
        self.parent_ = parent_
        self.bseq = bseq
        self.pf = pf
        self.button = button
            
    def run(self):
        pmgr.call(self.bseq[self.pf][2], self.bseq[self.pf])
        self.button.setStyleSheet("background: None")

'''
class auth_Thread(QObject):
    auth_signal = pyqtSignal(bool)
    freeze_signal = pyqtSignal(bool)
    def __init__(self):
        super(QObject, self).__init__()


    def start_auth(self):
        auth_object.setparent(self)
        while True:
            if authenticate():
                time.sleep(5)
            else:
                self.auth_signal.emit(False)

    def emitfreeze(self, dofreeze):
        self.freeze_signal.emit(dofreeze)
        '''
async def  main():

    app = QApplication(sys.argv)
    form = DB_Window()
    form.show()
    
    app.exec()
    nest_asyncio.apply()
    sys.exit(0)




if __name__ == '__main__':
   asyncio.run(main()) 
connection.close(True)
