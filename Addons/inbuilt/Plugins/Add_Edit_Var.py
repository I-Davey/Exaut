from .__important.PluginInterface import PluginInterface
import os
from sqlalchemy import insert, select, or_, text, update
from backend.db.Exaut_sql import *
import shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class Add_Edit_Var(PluginInterface):
    load = True
    types = {"type_":2,"source":3, "target":4, "databasepath":5}
    callname = ("add_var","edit_var")
    hooks_handler = ["log"]
    hooks_method = ["readsql", "writesql"]
    type_types = {
    "type_":{"type":"dropdown", "description":"please select Required Action", "optional":False, "options":["add_var","edit_var"]},
    "source":{"type":"text", "description":"please Enter Variable Name", "optional":True},
    "target":{"type":"text", "description":"please Enter Variable Value", "optional":True},
    "databasepath":{"type":"checkbox", "description":"Is Variable Global?", "optional":False},
    "__Name":"Add or Edit Variable"
    }


    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main
   

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, type_,variable_name, value, is_global) -> bool:
        self.type_ = type_
        self.variable_name = variable_name
        self.value = value
        self.is_global = is_global
        self.orig_loc = self.loc_
        if type_ == "add_var":
            return self.add_var()

        elif type_ == "edit_var":
            return self.edit_var()
    
    def add_var(self):        
        if not self.variable_name or not self.value:
            x = self.Popups.custom(Add_Dialog, self.variable_name, self.value, self.is_global)
            if x == (None,):
                return False
            self.variable_name, self.value, self.is_global_form, self.is_global_location = x
        formname = "*" if self.is_global else self.form_
        variables_list = self.readsql(select('*').where(variables.loc == self.loc_).where(variables.form == formname))
        variables_list = [dict(item._mapping) for item in variables_list]
        list_of_keys = [item["key"] for item in variables_list]
        if self.variable_name in list_of_keys:
            self.logger.error("Variable Already Exists")
            res = self.Popups.yesno(f"Variable {self.variable_name} Already Exists", f"Variable {self.variable_name} Already Exists, Do you want to overwrite it?")
            if res:
                self.writesql(update(variables).where(variables.loc == self.loc_).where(variables.form == formname).where(variables.key == self.variable_name).values(value = self.value))
                self.logger.success(f"Variable {self.variable_name} Updated to {self.value}")
                return True
        else:
            self.writesql(insert(variables).values(loc = self.loc_, form = formname, key = self.variable_name, value = self.value))
            self.logger.success(f"Variable {self.variable_name} Created with value {self.value}")
            return True
            

        

    def edit_var(self):
        formname = "*" if self.is_global else self.form_
        global_variables_list = self.readsql(select('*').where(variables.loc == self.loc_).where(variables.form == "*"))
        local_local_variables_list = self.readsql(select('*').where(variables.loc == self.loc_).where(variables.form == self.form_))
        local_global_variables_list = self.readsql(select('*').where(variables.loc == self.loc_).where(variables.form == "*"))
        global_global_variables_list = self.readsql(select('*').where(variables.loc == '*').where(variables.form == "*"))

        local_variables_list = local_local_variables_list 
        global_variables_list = local_global_variables_list + global_global_variables_list

        variables_list = self.readsql(select('*').where(variables.loc == self.loc_).where(variables.form == formname))

        global_keys = [item["key"] for item in global_variables_list]
        global_values = [item["value"] for item in global_variables_list]

        local_keys = [item["key"] for item in local_variables_list]
        local_values = [item["value"] for item in local_variables_list]

        list_of_keys = [item["key"] for item in variables_list]
        if not self.variable_name or not self.value:

            x = self.Popups.custom(Edit_Dialog, self.variable_name, self.value, self.is_global, global_keys, global_values,  local_keys, local_values)
            if x == (None,):
                return False
            self.variable_name, self.value, self.is_global = x
            list_of_keys = global_keys if self.is_global else local_keys
        if self.variable_name in list_of_keys:
            cur_loc = self.loc_
            if self.is_global:

                in_loc_global = self.readsql(select('*').where(variables.loc == '*').where(variables.form == "*").where(variables.key == self.variable_name))
                in_loc_local = self.readsql(select('*').where(variables.loc == self.loc_).where(variables.form == "*").where(variables.key == self.variable_name))
                #if both ghave a value
                if in_loc_global and in_loc_local:
                    cur_loc = self.orig_loc       
                else:
                    cur_loc = '*'     
                    

            self.writesql(update(variables).where(variables.loc == cur_loc).where(variables.form == formname).where(variables.key == self.variable_name).values(value = self.value))
            self.logger.success(f"Variable {self.variable_name} Updated to {self.value}")
            return True
        else:
            res = self.Popups.yesno(f"Variable {self.variable_name} Does not Exists", f"Variable {self.variable_name} Does not Exists, Do you want to create it?")
            if res:
                self.writesql(insert(variables).values(loc = self.loc_, form = formname, key = self.variable_name, value = self.value))
                self.logger.success(f"Variable {self.variable_name} Created with value {self.value}")
                return True
        self.logger.error(f"Variable {self.variable_name} Not Found")
        return False
        

        


class Add_Dialog(QDialog):
    signal = pyqtSignal(tuple)
    _done = False

    def __init__(self, parent=None, variable_name=None, value=None, is_global=None):
        super(Add_Dialog, self).__init__(parent)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.variable_name = variable_name
        self.value = value
        self.isglobal = is_global
        self.createFormGroupBox()
 
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        width = 350
        height = 140

        self.resize(width, height)
        self.setWindowTitle("Add New Variable")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()

        self.variable_name_qt = QLineEdit()
        self.variable_name_qt.setText(self.variable_name)

        self.value_qt = QLineEdit()
        self.value_qt.setText(self.value)

        self.isglobal_qt = QCheckBox()
        self.isglobal_qt.setChecked(self.isglobal)

        layout.addRow(QLabel("Variable Name:"), self.variable_name_qt)
        layout.addRow(QLabel("Value:"), self.value_qt)
        layout.addRow(QLabel("Global Variable:"), self.isglobal_qt)

        self.formGroupBox.setLayout(layout)

    def closeEvent(self, a0) -> None:
        if not self._done:
            self.signal.emit((None,))
        self.close()
        a0.accept()


    def accept(self):
        self._done = True
        self.signal.emit((self.variable_name_qt.text(), self.value_qt.text(), self.isglobal_qt.isChecked()))
        self.close()


class Edit_Dialog(QDialog):
    signal = pyqtSignal(tuple)
    _done = False

    def __init__(self, parent=None, variable_name=None, value=None, is_global=None, global_keys=None, global_values=None, local_keys=None, local_values=None):
        super(Edit_Dialog, self).__init__(parent)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.variable_name = variable_name
        self.value = value
        self.isglobal = is_global
        self.global_keys = global_keys
        self.global_values = global_values
        width = 350
        height = 140

        self.resize(width, height)
        self.local_keys = local_keys
        self.local_values = local_values
        if self.isglobal:
            list_of_keys = global_keys
        else:
            list_of_keys = local_keys
        self.createFormGroupBox(list_of_keys)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("Edit Variable")
        
    def createFormGroupBox(self, list_of_keys):
        self.formGroupBox = QGroupBox("")
        layout = QFormLayout()

        self.value_qt = QLineEdit()
        self.value_qt.setText(self.value)

        self.variable_name_qt = QComboBox()
        self.variable_name_qt.addItems(list_of_keys)
        self.variable_name_qt.currentTextChanged.connect(self.variable_name_changed)
        if self.variable_name and self.variable_name in list_of_keys:
            self.variable_name_qt.setCurrentText(self.variable_name)
            if self.isglobal:
                self.value_qt.setText(self.global_values[self.global_keys.index(self.variable_name)])
            else:
                self.value_qt.setText(self.local_values[self.local_keys.index(self.variable_name)])
        else:
            self.variable_name_qt.setCurrentIndex(0)
            if self.isglobal:
                if self.global_keys:
                    self.value_qt.setText(self.global_values[0])
            else:
                if self.local_values:
                    self.value_qt.setText(self.local_values[0])





        self.isglobal_qt = QCheckBox()
        #isglobalqt changed
        self.isglobal_qt.stateChanged.connect(self.isglobalqt_changed)
        self.isglobal_qt.setChecked(self.isglobal)

        layout.addRow(QLabel("variable Name:"), self.variable_name_qt)
        layout.addRow(QLabel("Value:"), self.value_qt)
        layout.addRow(QLabel("Global Variable:"), self.isglobal_qt)

        self.formGroupBox.setLayout(layout)

    def closeEvent(self, a0) -> None:
        if not self._done:
            self.signal.emit((None,))
        self.close()
        a0.accept()

    def isglobalqt_changed(self):
        if self.isglobal_qt.isChecked():
            self.variable_name_qt.clear()
            self.variable_name_qt.addItems(self.global_keys)
        else:
            self.variable_name_qt.clear()
            self.variable_name_qt.addItems(self.local_keys)

    def variable_name_changed(self):
        self.value_qt.setText(self.get_value(self.variable_name_qt.currentText()))

    def get_value(self, variable_name):
        if self.isglobal_qt.isChecked():
            if variable_name in self.global_keys:
                return self.global_values[self.global_keys.index(variable_name)]
        else:
            if variable_name in self.local_keys:
                return self.local_values[self.local_keys.index(variable_name)]
        return ""


    def accept(self):
        self._done = True
        self.signal.emit((self.variable_name_qt.currentText(), self.value_qt.text(), self.isglobal_qt.isChecked()))
        self.close()