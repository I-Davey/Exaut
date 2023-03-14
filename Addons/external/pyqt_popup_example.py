from __important.PluginInterface import PluginInterface
import os 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
class pyqt_popup_example(PluginInterface):
    load = True
    types = {}
    type_types = { "__Name":"t1"}

    callname = "PYQT in Action Example"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self,  ) -> bool: 
        #check if dir exists



        #if exe exists:   
        dialog = Dialog
        x = self.Popups.custom(dialog)
        self.logger.debug(x)
        self.Popups.alert(x)

class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4
    signal = pyqtSignal(tuple)
    _done = False

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

    def closeEvent(self, a0) -> None:
        if not self._done:
            self.signal.emit((self.name.text(), self.country.text(), self.age.value()))
        self.close()
        a0.accept()


    def accept(self):
        self._done = True
        self.signal.emit((self.name.text(), self.country.text(), self.age.value()))
        self.close()

