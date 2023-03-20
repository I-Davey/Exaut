from sqlalchemy import insert,delete,select
from __important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
import os 
import json
import time
from PyQt6.QtWidgets import QLabel, QPushButton, QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox
from PyQt6.QtCore import pyqtSignal
import pandas as pd
class import_tab_xlsx(PluginInterface):
    load = True
    types = {"source":3, "target":4, "databasepath":5}
    type_types = {"source":["drag_drop_folder", "Please select Pipeline"], "__Name":"Import Tab <- xlsx"}

    callname = "import_tab_xlsx"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main
        self.engine = hooks["writesql"].engine

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, folder, form, tab) -> bool: 
        folder = folder.replace("/", "\\")
        #for file in folder
        filelist = {}
        for file in os.listdir(folder):
            if file.endswith(".xlsx"):
                
                filelist[file[:-5]] = file
        print("done")
        for file in filelist:
            print(file)
        tabname, dataset, formname, vars = self.Popups.custom(Popup, filelist, form, tab)
        if not dataset and not formname:
            return False
        #select dataset from filelist
        if tabname == "":
            tabname = dataset
        if dataset == "":
            self.logger.error("Dataset name cannot be empty")
            return False
        data = filelist[dataset]
        data = folder + "\\" + data
        df_form = pd.read_excel(data, sheet_name="forms")
        df_tabs  = pd.read_excel(data, sheet_name="tabs")
        df_buttons = pd.read_excel(data, sheet_name="buttons")
        df_batchsequence = pd.read_excel(data, sheet_name="batchsequence")
        df_buttonseries = pd.read_excel(data, sheet_name="buttonseries")
        df_vars = pd.read_excel(data, sheet_name="variables")
        #for each dataset, replace formname with formname
        if formname:
            df_form["formname"] = formname
            df_tabs["formname"] = formname
            df_buttons["formname"] = formname
            df_batchsequence["formname"] = formname
            df_buttonseries["formname"] = formname
        if tabname:
            df_tabs["tab"] = tabname
            df_buttons["tab"] = tabname
            df_batchsequence["tab"] = tabname
            df_buttonseries["tab"] = tabname
        form = df_form.to_dict(orient="records")[0]
        print(form["formname"])
        if len(self.readsql(select([tabs]).where(tabs.formname == formname).where(tabs.tab == tabname))) > 0:
            x = self.Popups.yesno("tab already exists. Do you want to overwrite?")
            if not x:
                return False
            
            #delete from forms, tabs, buttons, batchsequence, buttonseries where formname = form["formname"]
            formname = form["formname"]
            self.writesql(delete(tabs).where(tabs.formname == form["formname"]).where(tabs.tab == tabname))
            self.writesql(delete(buttons).where(buttons.formname == form["formname"]).where(buttons.tab == tabname))
            self.writesql(delete(batchsequence).where(batchsequence.formname == form["formname"]).where(batchsequence.tab == tabname))
            self.writesql(delete(buttonseries).where(buttonseries.formname == form["formname"]).where(buttonseries.tab == tabname))

        df_tabs.to_sql("tabs", self.engine, if_exists="append", index=False)
        df_buttons.to_sql("buttons", self.engine, if_exists="append", index=False)
        df_batchsequence.to_sql("batchsequence", self.engine, if_exists="append", index=False)
        df_buttonseries.to_sql("buttonseries", self.engine, if_exists="append", index=False)

        if vars:
            time_start = time.time()

            ###
            all_vars = pd.DataFrame(self.readsql(select('*').where(variables.form != None)))
            #overwrite all_vars with df_vars, no duplicates
            all_vars = all_vars.append(df_vars, ignore_index=True)
            all_vars = all_vars.drop_duplicates(subset=["form", "loc", "key"], keep="last")
            self.writesql(delete(variables))
            all_vars.to_sql("variables", self.engine, if_exists="append", index=False)
            ###

            time_end = time.time()
            self.logger.info(" DF::: Imported variables in {} seconds".format(time_end - time_start))
       

      
        return True
    




class Popup(QDialog):
    signal = pyqtSignal(tuple)
    def __init__(self, parent=None, data="", form="", tab=""):
        super(Popup, self).__init__(parent)
        self.parent_ = parent
        self._done = False
        self.data = data
        self.form = form
        self.tab = tab
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Popup')

        self.label_fname = QLabel(self)
        self.label_fname.setText("Enter Tab Name")
        self.fname = QLineEdit(self)

        self.label_select_tab = QLabel(self)
        self.label_select_tab.setText("Select Tab to Import")
        self.select_tab = QComboBox(self)
        self.select_tab.addItems(list(self.data.keys()))
    
        self.save_button = QPushButton(self)
        self.save_button.setText("Done")
        self.save_button.clicked.connect(self.save_button_clicked)
        self.import_vars = QCheckBox(self)
        self.import_vars.setText("Import Variables")

        layout = QVBoxLayout()
        self.setLayout(layout)

        flayout = QHBoxLayout()

        flayout.addWidget(self.label_fname)
        flayout.addWidget(self.fname)

        tlayout = QHBoxLayout()
        tlayout.addWidget(self.label_select_tab)
        tlayout.addWidget(self.select_tab)



        form_label = QLabel(self)
        form_label.setText("Select Form")
        self.form = QComboBox(self)
        self.form.addItems(list(self.parent_.api.button_map().keys()))
        self.form.setCurrentIndex(self.form.findText(self.parent_.form_title))

        curtabtext = self.parent_.SM_Tabs.tabText(self.parent_.SM_Tabs.currentIndex())
        x = self.select_tab.findText(curtabtext)
        self.select_tab.setCurrentIndex(x)
        


        

        

        flayout2 = QHBoxLayout()
        flayout2.addWidget(form_label)
        flayout2.addWidget(self.form)
        
        layout.addLayout(tlayout)
        layout.addLayout(flayout)
        layout.addLayout(flayout2)
        layout.addWidget(self.import_vars)
        layout.addWidget(self.save_button)

    #if exited
    def closeEvent(self, event):
        if not self._done:
            self.signal.emit((False, False, False,False))
        event.accept()


    def save_button_clicked(self):
        self.signal.emit((self.fname.text(), self.select_tab.currentText(), self.form.currentText(), self.import_vars.isChecked()))
        self._done = True
        self.close()


