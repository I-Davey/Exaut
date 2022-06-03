from asyncio import Handle
from typing import Tuple

from PyQt5.QtCore import QThread
from loguru import logger
#import QVBoxLayout
from PyQt5.QtWidgets import QPushButton,  QFormLayout, QLineEdit, QLabel, QPushButton, QDialog, QComboBox, QGridLayout, QFileDialog, QWidget, QVBoxLayout, QSizePolicy, QMenu
from PyQt5.QtCore import Qt, pyqtSignal
import pyperclip
from .TypeManager.Types_handler import Types
from functools import partial
import collections
from PyQt5 import QtWidgets
#{'Zipcrypt': {'source': ['folder', 'please select source folder'], 'target': ['folder', 'please select destination folder'], 'databasename': ['text', 'please enter password']}}
class Create_Process(QDialog):
    def __init__(self, parent_, PluginManager, formname, tabname):
        
        super().__init__(parent_)
        self.parent_ = parent_
        self.formname = formname
        self.tabname = tabname
        self.resize(0, 150)
        self.setWindowTitle(f"Create New Button - {tabname}")
        self.layout = QFormLayout()
        self.setLayout(self.layout)


        self.typemgr = Types()
        self.threads = []
        self.type_map = {}
        self.type_list = []
        self.type_data = []
        self.object_list = []
        self.PluginManager = PluginManager
          #copy of  self.plugin_types dict
        self.plugin_types = self.PluginManager.plugin_type_types.copy()
        self.create_button = None
        self.button_name = None
        self.button_description = None
        self.chosen_type = None
        self.list_types()
        self.multiselect = QComboBox()
        self.multiselect.addItem(" ")
        self.handlemultiselect()

        #action on self.multiselect item seleciton
        self.multiselect.currentIndexChanged.connect(lambda: self.generate_type_types(self.multiselect.currentText()))

        #_UNDELETE

        #        self.multiselect.currentIndexChanged.connect(lambda: self.generate_type_types_Handler(self.multiselect.currentText()))


        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_proc_handler)
        #set horizontal fit to text
        self.multiselect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        temp_grid = QGridLayout()
        temp_grid.addWidget(self.multiselect, 0, 0)
        temp_grid.addWidget(self.create_button, 0, 1)
        self.layout.addRow(QLabel("Select Type"), temp_grid)

        self.generated_widget_layout = QFormLayout()
        self.layout.addRow(self.generated_widget_layout)


        
    def handlemultiselect(self):
        self.multiselect.addItems(self.type_list)

    def list_types(self):
        for key in self.plugin_types:
            #check if it is an array
            if isinstance(self.plugin_types[key], list):
                if self.plugin_types[key][0] == True:
                    self.plugin_types[key].pop(0)
                self.type_list.append(self.plugin_types[key][1])
                self.type_map.update({self.plugin_types[key][1]: key})
                self.plugin_types[key] = self.plugin_types[key][0]
            else:
                self.type_list.append(key)

            
    def generate_type_types_Handler(self, type_name):
        worker = Generic_Function_Thread(self.checkplugins, type_name)
        worker.start()
        self.threads.append(worker)
        worker.finished.connect(partial(self.generate_type_types, type_name))

    def checkplugins(self,type_):
        if type_ in self.type_map:
            type_ = self.type_map[type_]
        if type_ in self.plugin_types:
            if callable(self.plugin_types[type_]):
                self.plugin_types[type_] = self.plugin_types[type_]()       

    def generate_type_types(self, type_):


        #delete all items on generated_widget_layout
        #if type_ in self.type_map
        type_1 = type_
        if type_ in self.type_map:
            type_ = self.type_map[type_]
        self.chosen_type = type_
        for i in reversed(range(self.generated_widget_layout.count())): 
            x = self.generated_widget_layout.itemAt(i)
            y = x.widget()
            if y:
                y.setParent(None) if y else None
                y.deleteLater()
            lyt = x.layout()
            while lyt:
                t = lyt
                if lyt:
                    for i in reversed(range(lyt.count())): 
                        x = lyt.itemAt(i)
                        wdgt = x.widget()
                        if wdgt:
                            wdgt.setParent(None) if wdgt else None
                            wdgt.deleteLater()
                t.setParent(None) if t else None
                t.deleteLater()
                lyt = x.layout()
        self.object_list = []
        self.type_data = []
        if type_ in (" ","", None):
            return
        self.button_name = QLineEdit()
        self.button_name.setPlaceholderText(type_1)
        self.generated_widget_layout.addRow(QLabel("Button Name"), self.button_name)
        self.button_description = QLineEdit()
        self.button_description.setPlaceholderText(" Description")
        self.generated_widget_layout.addRow(QLabel("(optional) Description"), self.button_description)
        #if self.plugin_types[type_] is a function

        for key, data in self.plugin_types[type_].items():
            optional = False
            if isinstance(data, dict):
                type_type = data["type"]
                type_description = data["description"]
                if "args" not in data:
                    data["args"] = None
                if "optional" not in data:
                    data["optional"] = False
                type_args = data["args"] 
                optional = data["optional"] 

            else:
                type_type  = data[0]
                type_description = data[1]
                type_args = data[2] if len(data) > 2 else None
                optional = data[3] if len(data) > 3 else False
                data = {"type": type_type, "description": type_description, "args": type_args, "optional": optional}
            if self.typemgr.exists(type_type):
                required_params = self.typemgr.getparams(type_type)
                #REQUIRED PARAMS = TUPLE OR NONE
                plist = []
                if required_params is not None:
                    for param in required_params:
                        plist.append(data[param])
                
                callback_, gen_object = self.typemgr.create(type_type,  *plist, db_key=key)
                if gen_object is not None:
                    #if gen_object is iterable
                    if isinstance(gen_object, tuple):
                        print("list")
                        self.generated_widget_layout.addRow(*gen_object)
                    else:
                        self.generated_widget_layout.addRow(gen_object)
                self.type_data.append(callback_)
                self.object_list.append(gen_object)
            

    def create_proc_handler(self):
        if not self.check_data():
            return
        self.create_process()
        
    def check_data(self):
        valid = True
        if self.button_name:
            if self.button_name.text() in (None, ""):
                self.button_name.setStyleSheet("background-color: red")
                valid = False
        else:
            self.button_name.setStyleSheet("background-color: None")
            valid = False

        for item in self.type_data:
            if not item.validate_result():
                valid = False

        return valid

    def create_process(self):
        both_value_dict = {"formname": self.formname, "tab": self.tabname, "buttonname": self.button_name.text()}
        batchsequence_value_dict = {}
        button_value_dict = {}
        batchsequence_value_dict.update(both_value_dict)
        for item in self.PluginManager.plugin_loc:
            if self.PluginManager.plugin_loc[item] == self.chosen_type:
                self.call_type = item
                batchsequence_value_dict["type"] = item
                break
        for item in self.type_data:
            batchsequence_value_dict[item.key] = item.data
        if self.button_description.text() != "":
            button_value_dict["buttondesc"]= self.button_description.text()
        button_value_dict.update(both_value_dict)
        button_value_dict["buttonsequence"] = "0"
        button_value_dict["columnnum"] = "0"


        #handles special functions for changing data within the type python file (complex 😳😳😭😭😏😏 )
        batchsequence_value_dict = self.PluginManager.plugins[self.chosen_type]['object'].getTypeFunc(batchsequence_value_dict) 
        #
        bseq_q = self.create_query("batchsequence", batchsequence_value_dict)
        btn_q = self.create_query("buttons", button_value_dict)
        self.parent_.WriteSQL(bseq_q)
        self.parent_.WriteSQL(btn_q)
        self.parent_.Refresh()

        self.multiselect.setCurrentIndex(0)
        

    def create_query(self, table, value_dict):
        query = "INSERT INTO " + table + " ("
        for key in value_dict:
            query += key + ", "
        query = query[:-2] + ") VALUES ("
        for key in value_dict:
            if isinstance(value_dict[key], list):
                data = ""
                for item in value_dict[key]:
                    data += str(item) + "||"
                value_dict[key] = data[:-2]
            query += "'" + value_dict[key] + "', "
        query = query[:-2] + ");"
        return query


    def browse_folder(self, db_key):
        qwidget = self.type_data[db_key]["qwidget"]
        dir_ = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_ != "":
            qwidget.setText(dir_)
            self.type_data[db_key]["result"] = dir_
                
    def browse_file(self, db_key, type_args):
        
        qwidget = self.type_data[db_key]["qwidget"]
        file = QFileDialog.getOpenFileName(self, "Select File", filter=type_args if type_args else "All Files (*)")
        if file[0] != "":
            qwidget.setText(file[0])
            self.type_data[db_key]["result"] = file[0]


    def selection_layered_changed(self, index, qcombo2, qcombo3):
        index = index.currentIndex() - 1
        qcombo2.clear()
        qcombo2.addItem(" ")
        for i, item in enumerate(qcombo3[index]):
            qcombo2.addItem(item[0])


class Generic_Function_Thread(QThread):
    def __init__(self, fn, *args) -> None:
        super(QThread, self).__init__()
        self.fn = fn
        self.args = args
    def run(self):
        
        self.fn(*self.args)

class QFileDrop(QWidget):
    link_signal = pyqtSignal(list)

    def __init__(self, call_func, db_key, type_args=None, type_description=None, parent=None):
        db_key 
        super(QFileDrop, self).__init__(parent)
        self.setAcceptDrops(True)
        self.call_func = call_func
        self.db_key = db_key
        self.type_args = type_args
        self.type_description = type_description
        self.parent_ = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.create_browse()
        self.add_browse()

    def create_browse(self):
        self.browse_ = QPushButton("Browse")
        if self.type_args:
            self.browse_.clicked.connect(partial(self.call_func, self.db_key if not None else None, self.type_args if not None else None))
        else:
            self.browse_.clicked.connect(partial(self.call_func, self.db_key))

    def add_browse(self):
        self.layout.addWidget(self.browse_)
        #add right click menu
        self.browse_.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browse_.customContextMenuRequested.connect(self.right_click_menu)
        self.browse_.setToolTip(self.type_description)


    def right_click_menu(self, pos):
        menu = QMenu()
        menu.addAction("copy file/folder", self.copy_file)
        menu.addAction("copy full path", self.copy_file_path)
        menu.exec_(self.browse_.mapToGlobal(pos))

    def copy_file(self):
        text = self.browse_.text()
        if text != "":
            #split by \\ or / and get last item
            if "\\" in text:
                text = text.split("\\")[-1]
            elif "/" in text:
                text = text.split("/")[-1]
            
            
        pyperclip.copy(text)

    def copy_file_path(self):
        text = self.browse_.text()
        if text != "":
            pyperclip.copy(text)
        

    def setText(self, text):
        self.browse_.setText(text)

    def remove_browse(self):
        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.browse_)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.link_signal.emit( links)
            self.browse_.setText(links[0])


