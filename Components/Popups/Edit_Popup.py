import ctypes
from PyQt6 import QtGui, QtCore
from loguru import logger
from functools import partial
import os
#import QVBoxLayout
from PyQt6.QtWidgets import QPushButton,  QFormLayout, QLineEdit, QLabel, QPushButton, QDialog,  QMessageBox, QComboBox, QGridLayout
from PyQt6.QtCore import pyqtSignal

from Components.db.Exaut_sql import batchsequence
class Edit_Popup(QDialog):
    signal_delete = QtCore.pyqtSignal()
    signal_update = pyqtSignal(dict, dict)
    def __init__(self,parent_, data, state = True):
        super().__init__(parent_)
        self.resize(300, 300)
        self.setWindowTitle("Edit")
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.data = data
        self.parent_ = parent_

        self.form_name = self.data["button_data"]["formname"]
        self.tab_name = self.data["button_data"]["tab"]
        self.button_name = self.data["button_data"]["buttonname"]
        self.batchsequence_edit_dict = {}
        self.button_edit_dict = {}

        if state:
                batchsequence_dict = self.data["batchsequence_data"][0].copy() ##Change this for multi batchsequences
                batchsequence_dict.pop("formname")
                batchsequence_dict.pop("tab")
                batchsequence_dict.pop("buttonname")

        buttons_dict = self.data["button_data"].copy()
        buttons_dict.pop("formname")
        buttons_dict.pop("tab")
        buttons_dict.pop("buttonname")


        self.forms_dd = QComboBox()
        self.forms_dd.addItems([x['formname'] for x in self.data["form_data"]])
        self.forms_dd.currentIndexChanged.connect(self.layered_dd_changed)

        self.tabs_dd = QComboBox()
        self.layered_dd_changed()
        self.tabs_dd.setCurrentIndex(self.tabs_dd.findText(self.tab_name))

        self.button_name_edit = QLineEdit(self)
        self.button_name_edit.setText((self.button_name))

        self.save = QPushButton(self)
        self.save.setText("Update")
        self.save.clicked.connect(self.on_click_save)
        if not state:
            self.save.setDisabled(True)

        self.delete = QPushButton(self)
        self.delete.setText("Delete")
        self.delete.clicked.connect(self.on_click_delete)

        self.layout.addRow("Form name", self.forms_dd)
        self.layout.addRow("Tab name", self.tabs_dd)
        self.layout.addRow("Button name", self.button_name_edit)

        font = QtGui.QFont()
        font.setBold(True)

        btndata = QLabel("Button Data")
        btndata.setFont(font)

        self.layout.addRow(btndata)
        self.buttoneditdict = {}

        for key, value in buttons_dict.items():
            if value == None:
                value = ""
            elif type(value) == int:
                value = str(value)
            qlineedit = QLineEdit(self)
            qlineedit.setText(value)
            self.button_edit_dict.update({key:qlineedit})
            self.layout.addRow(key, qlineedit)
            
        if state:
            btnbseq = QLabel("Batchsequence Data")
            btnbseq.setFont(font)
            self.layout.addRow(btnbseq)
            for key, value in batchsequence_dict.items():
                if value == None:
                    value = ""
                elif type(value) == int:
                    value = str(value)
                qlineedit = QLineEdit(self)
                qlineedit.setText(value)
                label = QLabel_temp(key)
                label.clicked.connect(partial(self.on_click_label, item=key))
                self.batchsequence_edit_dict.update({key:qlineedit})
                self.layout.addRow(label, qlineedit)
            
        editdelete_grid = QGridLayout()
        editdelete_grid.addWidget(self.save, 0, 0)
        editdelete_grid.addWidget(self.delete, 0, 1)
        self.layout.addRow(editdelete_grid)

    def layered_dd_changed(self):
        #forms_dd currentext
        forms_text = self.forms_dd.currentText()
        self.tabs_dd.clear()
        self.tabs_dd.addItem(" ")
        for item in self.data["tab_data"]:
            if item["formname"] == forms_text:
                self.tabs_dd.addItem(item["tab"])
#################################################

    def on_click_label(self, item):
        path_text = self.qlineeditdict[item].text()
        if path_text == "":
            return
        #if realpath
        if os.path.exists(path_text):
            #open file explorer
            os.startfile(path_text)

    def on_click_save(self):
        batchsequence_changes_dict = {}
        buttons_changes_dict = {}
        for key, value in self.batchsequence_edit_dict.items():
            value = value.text() if value.text() != "" else None
            batchsequence_changes_dict.update({key:value})
        for key, value in self.button_edit_dict.items():
            value = value.text() if value.text() != "" else None
            buttons_changes_dict.update({key:value})
        batchsequence_changes_dict['formname'] = self.forms_dd.currentText()
        batchsequence_changes_dict['tab'] = self.tabs_dd.currentText()
        batchsequence_changes_dict['buttonname'] = self.button_name_edit.text()
        buttons_changes_dict['formname'] = self.forms_dd.currentText()
        buttons_changes_dict['tab'] = self.tabs_dd.currentText()
        buttons_changes_dict['buttonname'] = self.button_name_edit.text()
        self.signal_update.emit(batchsequence_changes_dict, buttons_changes_dict)
        self.close()

    def on_click_delete(self):
        qm = QMessageBox()
        qm.setText("Are you sure you want to delete?")
        qm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        qm.setDefaultButton(QMessageBox.StandardButton.No)
        qm.setWindowTitle("Delete?")
        ret = qm.exec()
        if ret == QMessageBox.StandardButton.Yes:
            self.signal_delete.emit()
            self.close()

class QLabel_temp(QLabel):
    clicked=pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()