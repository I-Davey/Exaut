from sqlalchemy import insert, select
from __important.PluginInterface import PluginInterface
from backend.db.Exaut_sql import *
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
class Add_Form(PluginInterface):
    load = True
    type_types = {"__Name":"Add a New Form"}

    callname = "ppub"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, Plugins) -> bool: 
        q = self.readsql(select(forms.formname, forms.formdesc))
        a = [x["formname"] for x in q]
        popup = Popup
        name, desc = Plugins.custom(popup)
        if not name and not desc:
            return False
        if name == "":
            self.logger.error("Form name cannot be empty")
            return False
        
        if name in a:
            Plugins.alert("Form already exists")
            return False

        x = self.writesql(insert(forms).values(formname=name, formdesc=desc))
        if x:
            self.logger.success(f"Form {name} with description {desc} added")
        return True

class Popup(QDialog):
    signal = pyqtSignal(tuple)
    def __init__(self, parent=None, name=""):
        super(Popup, self).__init__(parent)
        self.initUI()
        self._done = False
        print(name)


    def initUI(self):
        self.setWindowTitle('Popup')

        self.label_fname = QLabel(self)
        self.label_fname.setText("Enter Form Name!")
        self.fname = QLineEdit(self)
        self.label_desc = QLabel(self)
        self.label_desc.setText("Enter Form Description!")
        self.desc = QLineEdit(self)
    
        self.save_button = QPushButton(self)
        self.save_button.setText("Done")
        self.save_button.clicked.connect(self.save_button_clicked)

        layout = QVBoxLayout()
        self.setLayout(layout)

        flayout = QHBoxLayout()
        flayout.addWidget(self.label_fname)
        flayout.addWidget(self.fname)

        dlayout = QHBoxLayout()
        dlayout.addWidget(self.label_desc)
        dlayout.addWidget(self.desc)

        layout.addLayout(flayout)
        layout.addLayout(dlayout)
        layout.addWidget(self.save_button)

    #if exited
    def closeEvent(self, event):
        if not self._done:
            self.signal.emit((False, False))
        event.accept()


    def save_button_clicked(self):
        self.signal.emit((self.fname.text(), self.desc.text()))
        self._done = True
        self.close()


        

    


    

