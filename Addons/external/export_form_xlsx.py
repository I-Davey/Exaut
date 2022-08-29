from sqlalchemy import insert, select, or_
from __important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QComboBox, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
import pandas as pd
class export_form_xlsx(PluginInterface):
    load = True
    types = {"target":4}
    type_types = {"target":{"type":"drag_drop_folder", "description":"please select the export location"}, "__Name":"Export Form -> xlsx"}


    callname = "export_form_xlsx"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, save_loc) -> bool: 
        q = self.readsql(select(forms.formname, forms.formdesc))
        a = [x["formname"] for x in q]
        popup = Popup
        name = self.Popups.custom(popup, a)[0]
        print(name)

        full_loc = save_loc + "/" + name + '.xlsx'
        excel_writer = pd.ExcelWriter(full_loc)

        data = self.readsql(select('*').where(forms.formname == name))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='forms', index=False)

        data = self.readsql(select('*').where(tabs.formname == name))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='tabs', index=False)
        


        data = self.readsql(select('*').where(buttons.formname == name))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='buttons', index=False)

        data = self.readsql(select('*').where(batchsequence.formname == name))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='batchsequence', index=False)

        data = self.readsql(select('*').where(buttonseries.formname == name))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='buttonseries', index=False)

        data = self.readsql(select('*').where(or_(variables.form == name, variables.form == "*")).where(or_(variables.loc == self.loc_, variables.loc == "*")))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='variables', index=False)

        data = self.readsql(select("*").where(pluginmap.plugin != None))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='pluginmap', index=False)

        data = self.readsql(select("*").where(actions.plugin != None))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='actions', index=False)
        data = self.readsql(select("*").where(actions_categories.category != None))

        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='actions_categories', index=False)

        excel_writer.save()


        self.logger.success(f"Form {name} exported")
        self.logger.success(f"location "+ full_loc) 
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


        

    


    

