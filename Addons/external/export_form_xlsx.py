from sqlalchemy import insert, select, or_
from __important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QComboBox, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
import openpyxl
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
        self.widths = {'forms': {}, 'tabs': {'A': 9.6328125, 'B': 14.26953125, 'C': 5.26953125, 'D': 4.0, 'E': 22.453125, 'F': 18.6328125, 'G': 8.54296875, 'H': 8.7265625}, 'buttons': {'A': 9.6328125, 'B': 14.26953125, 'C': 30.453125, 'D': 8.08984375, 'E': 10.81640625, 'F': 47.54296875}, 'batchsequence': {'A': 6.26953125, 'B': 11.90625, 'C': 34.453125, 'D': 5.1796875, 'E': 49.0, 'F': 27.36328125, 'G': 15.7265625, 'H': 48.6328125, 'I': 34.90625, 'J': 12.453125, 'K': 22.08984375, 'L': 7.6328125, 'M': 6.26953125, 'N': 8.1796875}, 'buttonseries': {'B': 13.90625, 'C': 33.26953125, 'D': 25.90625, 'E': 6.0}, 'variables': {'C': 18.08984375, 'D': 36.08984375}, 'pluginmap': {'A': 33.453125, 'B': 18.81640625}, 'actions': {'A': 33.453125, 'C': 11.0}, 'actions_categories': {}}
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

        #data = self.readsql(select('*').where(or_(variables.form == name, variables.form == "*")).where(or_(variables.loc == self.loc_, variables.loc == "*")))
        data = self.readsql(select('*').where(variables.form != None))
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

        #open with openpyxl, set all column widths in all sheets to self.widths, save
        wb = openpyxl.load_workbook(full_loc)
        for sheet in wb.sheetnames:
            if sheet in self.widths:
                for col in self.widths[sheet]:
                    wb[sheet].column_dimensions[col].width = self.widths[sheet][col]
        wb.save(full_loc)

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


        

    


    

