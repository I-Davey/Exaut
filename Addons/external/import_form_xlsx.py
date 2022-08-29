from sqlalchemy import insert, select, or_, delete
from __important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QComboBox, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal
import pandas as pd
import os
class import_form_xlsx(PluginInterface):
    load = True
    types = {"target":4}
    type_types = {"target":{"type":"drag_drop_folder", "description":"please select the export location"}, "__Name":"Import Form -> xlsx"}


    callname = "import_form_xlsx"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.engine = hooks["writesql"].engine
        self.readsql = hooks["readsql"].main

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, folder) -> bool: 
        folder = folder.replace("/", "\\")
        #for file in folder
        filelist = {}
        for file in os.listdir(folder):
            if file.endswith(".xlsx"):
                filelist[file[:-5]] = folder + "\\" + file
        formname, dataset = self.Popups.custom(Popup, filelist)
        if not dataset and not formname:
            return False
        #select dataset from filelist

        if dataset == "":
            self.logger.error("Dataset name cannot be empty")
            return False
        data = filelist[dataset]

        df_form = pd.read_excel(data, sheet_name="forms")
        df_tabs  = pd.read_excel(data, sheet_name="tabs")
        df_buttons = pd.read_excel(data, sheet_name="buttons")
        df_batchsequence = pd.read_excel(data, sheet_name="batchsequence")
        df_buttonseries = pd.read_excel(data, sheet_name="buttonseries")
        #for each dataset, replace formname with formname
        if formname:
            df_form["formname"] = formname
            df_tabs["formname"] = formname
            df_buttons["formname"] = formname
            df_batchsequence["formname"] = formname
            df_buttonseries["formname"] = formname
        form = df_form.to_dict(orient="records")[0]
        print(form["formname"])
        if len(self.readsql(select([forms]).where(forms.formname == form["formname"]))) > 0:
            x = self.Popups.yesno("Form already exists. Do you want to overwrite?")
            if not x:
                return False
            
            #delete from forms, tabs, buttons, batchsequence, buttonseries where formname = form["formname"]
            formname = form["formname"]
            self.writesql(delete(forms).where(forms.formname == form["formname"]))
            self.writesql(delete(tabs).where(tabs.formname == form["formname"]))
            self.writesql(delete(buttons).where(buttons.formname == form["formname"]))
            self.writesql(delete(batchsequence).where(batchsequence.formname == form["formname"]))
            self.writesql(delete(buttonseries).where(buttonseries.formname == form["formname"]))

        df_form.to_sql("forms", self.engine, if_exists="append", index=False)
        df_tabs.to_sql("tabs", self.engine, if_exists="append", index=False)
        df_buttons.to_sql("buttons", self.engine, if_exists="append", index=False)
        df_batchsequence.to_sql("batchsequence", self.engine, if_exists="append", index=False)
        df_buttonseries.to_sql("buttonseries", self.engine, if_exists="append", index=False)

        print(df_form)

      
class Popup(QDialog):
    signal = pyqtSignal(tuple)
    def __init__(self, parent=None, forms=[]):
        super(Popup, self).__init__(parent)
        self._done = False
        self.forms = forms
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Popup')

        self.label_fname = QLabel(self)
        self.label_fname.setText("Select Form")
        self.fname = QComboBox(self)
        self.fname.addItems(self.forms)
       
    
        self.save_button = QPushButton(self)
        self.save_button.setText("export")
        self.save_button.clicked.connect(self.save_button_clicked)

        layout = QVBoxLayout()
        self.setLayout(layout)

        flayout = QHBoxLayout()
        flayout.addWidget(self.label_fname)
        flayout.addWidget(self.fname)



        layout.addLayout(flayout)
        layout.addWidget(self.save_button)

    #if exited
    def closeEvent(self, event):
        if not self._done:
            self.signal.emit((False, False))
        event.accept()


    def save_button_clicked(self):
        self.signal.emit((self.fname.currentText(),))
        self._done = True
        self.close()


        

    


    

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



       

        flayout2 = QHBoxLayout()

        
        layout.addLayout(tlayout)
        layout.addLayout(flayout)
        layout.addLayout(flayout2)
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