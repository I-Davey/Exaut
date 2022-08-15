from PyQt6 import QtGui, QtCore

#import QVBoxLayout
from PyQt6.QtWidgets import QPushButton,  QFormLayout, QLineEdit, QLabel, QPushButton, QMainWindow,  QMessageBox, QWidget, QGridLayout, QSizePolicy, QMessageBox, QInputDialog
from PyQt6.QtCore import pyqtSignal


class edit_popup_form(QMainWindow):
    signal_delete = QtCore.pyqtSignal()
    signal_update = pyqtSignal(str, str)

    def __init__(self,parent_,cur_form):
        super().__init__(parent_)
        
        self.logger = parent_.logger
        self.form_details = dict(parent_.api.get_form_details(cur_form)[0]._mapping)

        self.resize(300, 100)
        self.setWindowTitle("Edit")
        mainwidget = QWidget(self)
        self.layout = QFormLayout(mainwidget)
        self.setCentralWidget(mainwidget)

      
        
        

        self.save = QPushButton(self)
        self.save.setText("Update")
        self.save.clicked.connect(self.on_click_save)


        self.delete = QPushButton(self)
        self.delete.setText("Delete")
        self.delete.clicked.connect(self.on_click_delete)


        self.savedelgrid = QGridLayout()
        self.savedelgrid.addWidget(self.save, 0, 0)
        self.savedelgrid.addWidget(self.delete, 0, 1)





        font = QtGui.QFont()
        font.setBold(True)
        self.changes = {}
        for key, data in self.form_details.items():
            if type(data) not in [dict, list]:
                lineedit = QLineEdit(str(data) if data not in ('None', "", None) else "")
                self.layout.addRow(QLabel(key), lineedit)
                self.changes[key] = lineedit
        self.layout.addRow(self.savedelgrid)
        self.show()

    def on_click_save(self):


      
        self.signal_update.emit(*(x.text() for x in self.changes.values()))
        self.complete = True
        self.close()
    

      
    def on_click_delete(self):
            qm = QMessageBox(self)
            qm.setText("Are you sure you want to delete?")
            qm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            qm.setDefaultButton(QMessageBox.StandardButton.No)
            qm.setWindowTitle("Delete?")
            ret = qm.exec()
            if ret == QMessageBox.StandardButton.Yes:
                #enter "Confirm Delete" textbox
                confirm_delete = QInputDialog.getText(self, "Confirm Delete", "IF YOU DO NOT KNOW THE RAMIFICATIONS OF THIS ACTION THEN CLOSE THIS WINDOW IMMEDIATELY. \nPlease enter 'Delete' to confirm:")
                if confirm_delete[0] == "Delete":
                    self.signal_delete.emit()
                    self.complete = True
                    self.close()
                
                


        