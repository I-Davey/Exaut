from __important.PluginInterface import PluginInterface
import os 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
class teststuff(PluginInterface):
    load = True
    types = {}
    type_types = { "__Name":"t1"}

    callname = "test1"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self,  Popups) -> bool: 
        #check if dir exists



        #if exe exists:   
        dialog = Dialog
        x = Popups.custom(dialog)
        self.logger.debug(x)
        Popups.alert(x)

class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4
    signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.createFormGroupBox()
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("Form Layout - pythonspot.com")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        self.name = QLineEdit()
        self.country = QLineEdit()
        self.age = QSpinBox()
        layout.addRow(QLabel("Name:"), self.name)
        layout.addRow(QLabel("Country:"), self.country)
        layout.addRow(QLabel("Age:"), self.age)
        self.formGroupBox.setLayout(layout)

    def accept(self):
        self.signal.emit((self.name.text(), self.country.text(), self.age.value()))
        self.close()

