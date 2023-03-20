from sqlalchemy import insert, select, or_
from __important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QComboBox, QGridLayout, QHBoxLayout, QLineEdit, QCheckBox
from PyQt6.QtCore import pyqtSignal, Qt
import openpyxl
import os
import pandas as pd
class export_tab_xlsx(PluginInterface):
    load = True
    types = {"target":4, "tab":3, "form":5}
    type_types = {"target":{"type":"drag_drop_folder", "description":"please select the export location"}, "__Name":"Export tab -> xlsx"}


    callname = "export_tab_xlsx"
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


    def main(self, save_loc, tabname, form) -> bool: 
        tabs_data = self.readsql(select(tabs.formname, tabs.tab))
        forms_data = self.readsql(select(forms.formname))
        data = {}
        for items in forms_data:
            data[items["formname"]] = []

        for items in tabs_data:
            if items["formname"] in data:
                data[items["formname"]].append(items["tab"])
        forms_array = []
        for items in forms_data:
            forms_array.append(items["formname"])   
        formname, tabname, savename, filter = self.Popups.custom(Popup, data, forms_array, tabname, form)
        if not formname or not tabname:
            return False
        if not savename:
            savename = tabname

        full_loc = save_loc + "/" + tabname + '.xlsx'
        excel_writer = pd.ExcelWriter(full_loc)

        data = self.readsql(select('*').where(forms.formname == formname))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='forms', index=False)

        data = self.readsql(select('*').where(tabs.formname == formname).where(tabs.tab == tabname).order_by(tabs.tabsequence))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='tabs', index=False)
        


        data = self.readsql(select('*').where(buttons.formname == formname).where(buttons.tab == tabname).order_by(buttons.columnnum).order_by(buttons.buttonsequence))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='buttons', index=False)

        data = self.readsql(select('*').where(batchsequence.formname == formname).where(batchsequence.tab == tabname))
        df = pd.DataFrame(data)
        df.to_excel(excel_writer, sheet_name='batchsequence', index=False)

        data = self.readsql(select('*').where(buttonseries.formname == formname).where(buttonseries.tab == tabname))
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
            if filter:
                #import with openpyxl, add filter to each sheet
                wb[sheet].auto_filter.ref = wb[sheet].calculate_dimension()
        
        wb.save(full_loc)

        self.logger.success(f"tab {tabname} exported")
        self.logger.success(f"location "+ full_loc) 

        open_doc = self.Popups.yesno("Open the created XLSX document?")
        if open_doc:
            os.startfile(full_loc)


class Popup(QDialog):
    signal = pyqtSignal(tuple)
    def __init__(self, parent=None, form_tabs = {}, forms = [], tabname = "", form = ""):
        super(Popup, self).__init__(parent)
        self._done = False
        self.form_tabs = form_tabs
        self.forms = forms
        self.tabname = tabname
        self.form = form

        self.initUI()


    def initUI(self):
        self.setWindowTitle('Popup')

        self.label_fname = QLabel(self)
        self.label_fname.setText("Select Form")
        self.fname = QComboBox(self)
        self.fname.addItems(self.forms)

       
        self.label_tname = QLabel(self)
        self.label_tname.setText("Select Tab")
        self.tname = QComboBox(self)
        self.tname.addItems(self.form_tabs[self.forms[0]])
        self.fname.currentTextChanged.connect(self.update_tabs)
        
        if self.form:
            #find index of self.form in self.fname
            index = self.fname.findText(self.form, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.fname.setCurrentIndex(index)
        if self.tabname:
            #find index of self.tabname in self.tname
            index = self.tname.findText(self.tabname, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.tname.setCurrentIndex(index)

        

        self.label_export_name = QLabel(self)
        self.label_export_name.setText("Export Name")
        self.export_name = QLineEdit(self)


        self.checkbox_filter = QCheckBox(self)
        self.checkbox_filter.setText("Enable Filter on headers")

        self.button = QPushButton('OK', self)
        self.button.clicked.connect(self.save_button_clicked)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.label_fname, 0, 0)
        self.layout.addWidget(self.fname, 0, 1)
        self.layout.addWidget(self.label_tname, 1, 0)
        self.layout.addWidget(self.tname, 1, 1)
        self.layout.addWidget(self.label_export_name, 2, 0)
        self.layout.addWidget(self.export_name, 2, 1)
        self.layout.addWidget(self.checkbox_filter, 3, 0)
        self.layout.addWidget(self.button, 4, 0, 1, 2)
        

    
    def update_tabs(self):
        self.tname.clear()
        self.tname.addItems(self.form_tabs[self.fname.currentText()])
    
        

    


    

    def closeEvent(self, event):
        if not self._done:
            self.signal.emit((False, False, False, False))
        event.accept()


    def save_button_clicked(self):
        self.signal.emit((self.fname.currentText(), self.tname.currentText(), self.export_name.text(), self.checkbox_filter.isChecked()))
        self._done = True
        self.close()