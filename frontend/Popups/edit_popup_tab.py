from PyQt6 import QtGui, QtCore

#import QVBoxLayout
from PyQt6.QtWidgets import QPushButton,  QFormLayout, QLineEdit, QLabel, QPushButton, QMainWindow,  QMessageBox, QWidget, QGridLayout, QSizePolicy, QMessageBox
from PyQt6.QtCore import pyqtSignal

class edit_popup_tab(QMainWindow):
    signal_delete = QtCore.pyqtSignal()
    signal_update = pyqtSignal(dict, bool)
    def __init__(self,parent_,tab_name, data, cur_tabs):
        super().__init__(parent_)
        
        self.logger = parent_.logger
        self.resize(300, 300)
        self.setWindowTitle("Edit")
        mainwidget = QWidget(self)
        self.layout = QFormLayout(mainwidget)
        self.setLayout(self.layout)
        self.setCentralWidget(mainwidget)

        self.tabname = tab_name
        self.cur_tabs = cur_tabs
        self.cur_tabs = [tab.lower() for tab in self.cur_tabs]

        data = data.copy()
        self.data = data
        #delete all items in self.data that is dict or list
        for key, value in self.data.copy().items():
            if isinstance(value, dict) or isinstance(value, list):
                self.data.pop(key)
        self.data.pop("formname")

        self.parent_ = parent_
        self.complete = False

        #get all self.curtab as lowercase

        #delete keys allitems and buttons from 
        
        

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
        for key, data in data.items():
            if type(data) not in [dict, list]:
                lineedit = QLineEdit(str(data) if data not in ('None', "", None) else "")
                self.layout.addRow(QLabel(key), lineedit)
                self.changes[key] = lineedit
        self.layout.addRow(self.savedelgrid)


    def on_click_save(self):


        if self.changes['tab'].text() != self.tabname:
            if not self.parent_.edit_mode:
                    if self.changes['tab'].text().lower() in self.cur_tabs:
                        self.parent_.Alert("Tab name already exists")
                        return
            if self.changes['tab'].text().lower() in self.cur_tabs:
                yes_no_popup = QMessageBox(self)
                yes_no_popup.setWindowTitle("Move Buttons?")
                yes_no_popup.setText("This tab already exists. Do you want to move the buttons to this tab?")
                yes_no_popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                yes_no_popup.setDefaultButton(QMessageBox.StandardButton.Yes)

                yes_no_popup.exec()
                if yes_no_popup.result() == QMessageBox.StandardButton.Yes:
                        for key, value in self.changes.items():
                            if key in self.data:
                                if value.text() != self.data[key]:
                                    self.data[key] = value.text()
                        for key, value in self.data.copy().items():
                            if value in ('None', ""):
                                self.data[key] = None
                        self.signal_update.emit(self.data, True)
                        self.complete = True
                        self.close()
                
                return

        for key, value in self.changes.items():
            if key in self.data:
                if value.text() != self.data[key]:
                    self.data[key] = value.text()
        for key, value in self.data.copy().items():
            if value in ('None', ""):
                self.data[key] = None
        self.signal_update.emit(self.data, False)
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
                self.signal_delete.emit()
                self.complete = True
                self.close()
