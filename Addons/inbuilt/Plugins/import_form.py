from sqlalchemy import insert
from .__important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
import os 
import json
from PyQt6.QtWidgets import QLabel, QPushButton, QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt6.QtCore import pyqtSignal
class import_form(PluginInterface):
    load = True
    types = {"source":3}
    type_types = {"source":["drag_drop_folder", "Please select Pipeline"], "__Name":"Import Form <- json"}

    callname = "import_form_json"
    hooks_handler = ["log"]
    hooks_method = ["writesql"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, folder) -> bool: 
        if folder == "":
            return False
        folder = folder.replace("/", "\\")
        #for file in folder
        filelist = {}
        for file in os.listdir(folder):
            if file.endswith(".json"):
                data = json.loads(open(folder + "\\" + file, "r").read())
                filelist[file[:-5]] = data
        print("done")
        for file in filelist:
            print(file)
        formname, dataset = self.Popups.custom(Popup, filelist)
        if not formname and not dataset and not formname:
            return False
        #select dataset from filelist
        if formname == "":
            formname = dataset
        if dataset == "":
            self.logger.error("Dataset name cannot be empty")
            return False
        data = filelist[dataset]

        for k, v in data.items():
            if type(v) == dict:
                for k1 in v:
                    if k1 == "formname":
                        data[k][k1] = formname

            else:
                for i, j in enumerate(v):
                    for k1 in j:
                        if k1 == "formname":
                            data[k][i][k1] = formname
        queries = []
        for item, v in data.items():
            if type(v) == dict:
                queries.append(insert(eval(item)).values(v))
            elif type(v) == list:
                #each item in v should be like the following f".values[{v[0]}]" + f".values[{v[1]}]"
                for i in v:
                    queries.append(insert(eval(item)).values(i))
        x = self.writesql(queries)
        self.Popups.refresh()
        if x:
            return True
        return False




class Popup(QDialog):
    signal = pyqtSignal(tuple)
    def __init__(self, parent=None, data=""):
        super(Popup, self).__init__(parent)
        self.parent_ = parent
        self._done = False
        self.data = data
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Popup')

        self.label_fname = QLabel(self)
        self.label_fname.setText("Enter Form Name")
        self.fname = QLineEdit(self)

        self.label_select_tab = QLabel(self)
        self.label_select_tab.setText("Select Form to Import")
        self.select_tab = QComboBox(self)
        self.select_tab.addItems(list(self.data.keys()))
    
        self.save_button = QPushButton(self)
        self.save_button.setText("Done")
        self.save_button.clicked.connect(self.save_button_clicked)

        layout = QVBoxLayout()
        self.setLayout(layout)

        flayout = QHBoxLayout()

        flayout.addWidget(self.label_fname)
        flayout.addWidget(self.fname)

        tlayout = QHBoxLayout()
        tlayout.addWidget(self.label_select_tab)
        tlayout.addWidget(self.select_tab)



       
        
        layout.addLayout(tlayout)
        layout.addLayout(flayout)
        layout.addWidget(self.save_button)

    #if exited
    def closeEvent(self, event):
        if not self._done:
            self.signal.emit((False, False))
        event.accept()


    def save_button_clicked(self):
        self.signal.emit((self.fname.text(), self.select_tab.currentText()))
        self._done = True
        self.close()


