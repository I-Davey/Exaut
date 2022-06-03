import ctypes
from PyQt5 import QtGui, QtCore
from loguru import logger
from functools import partial
import os
#import QVBoxLayout
from PyQt5.QtWidgets import QPushButton,  QFormLayout, QLineEdit, QLabel, QPushButton, QDialog,  QMessageBox, QComboBox, QGridLayout
from PyQt5.QtCore import pyqtSignal
class Edit_Popup(QDialog):
    def __init__(self, parent, bseq, pname, tname, bname, objn):
        
        super().__init__(parent)
        self.resize(300, 300)
        self.setWindowTitle("Edit")
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.pname_orig = pname
        self.tname_orig = tname
        self.bname_orig = bname
        self.parent_ = parent
        if len(bseq) == 0:
            bseq = [["","","","","","","","","","","",""]]
            ctypes.windll.user32.MessageBoxW(0, "No button sequence data found for this button - Deleting the button is recommended", "Error", 0)
        self.bseq = bseq[0]

        db_columns = ["folderpath","filename","type","source","target","databasepath","databasename","keypath","keyfile","runsequence","treepath"]
        item_dict = {}
        self.qlineeditdict = {}
        for item in range(len(self.bseq)):
            if self.bseq[item] == None:
                self.bseq[item] = ""
        for item in range(len(self.bseq) - 1):
            item_dict[db_columns[item]] = bseq[0][item]
        #take each item up to database path from db coumns from item dict and put into button_item
        self.batchsequence_items = {"runsequence":item_dict["runsequence"],"folderpath":item_dict["folderpath"],"filename":item_dict["filename"],"type":item_dict["type"],"source":item_dict["source"],"target":item_dict["target"],"databasepath":item_dict["databasepath"], "databasename":item_dict["databasename"],"keypath":item_dict["keypath"],"keyfile":item_dict["keyfile"],"treepath":item_dict["treepath"]}
        self.buttons_items = self.grab_buttons_data()
        for item in self.buttons_items:
            if self.buttons_items[item] == None:
                self.buttons_items[item] = ""

        #add pname tname bname objn as text
        #using self.parent_readsql, select tab from tabs
        tabs = self.parent_.ReadSQL(f"SELECT tab FROM tabs WHERE formname = '{self.pname_orig}'",msg=False)
        #create dropdown of forms
        tab_array = []
        for item in tabs:
            tab_array.append(item[0])
        self.tabs_dd = QComboBox()
        self.tabs_dd.addItems(tab_array)
        self.tabs_dd.setCurrentText(self.tname_orig)

        #set current active form in dropdown_of_forms 


        self.pname = QLineEdit(self)
        self.pname.setText(str(pname))  
        self.bname = QLineEdit(self)
        self.bname.setText((bname))
        self.objn = QLineEdit(self)
        self.objn.setText((objn))
        #add button save
        self.save = QPushButton(self)
        self.save.setText("Update")
        self.save.clicked.connect(self.on_click_save)
        self.delete = QPushButton(self)
        self.delete.setText("Delete")
        self.delete.clicked.connect(self.on_click_delete)

        self.layout.addRow(self.pname, self.tabs_dd)
        self.layout.addRow("Form name", self.pname)
        self.layout.addRow("Tab name", self.tabs_dd)
        self.layout.addRow("Button name", self.bname)
        self.layout.addRow("Object name", self.objn)



        font = QtGui.QFont()
        font.setBold(True)

        btndata = QLabel("Button Data")
        btndata.setFont(font)

        self.layout.addRow(btndata)
        #bold btndata
        #import Qfont


        self.buttoneditdict = {}

        for item in self.buttons_items:

            qlineedit = QLineEdit(self)
            qlineedit.setText(str(self.buttons_items[item]))
            self.buttoneditdict.update({item:qlineedit})

            self.layout.addRow(item, qlineedit)


        btnbseq = QLabel("Batchsequence Data")

        btnbseq.setFont(font)

        self.layout.addRow(btnbseq)

        for item in self.batchsequence_items:
            qlineedit = QLineEdit(self)
            qlineedit.setText(str(self.batchsequence_items[item]))
            label = QLabel_temp(item)
            label.clicked.connect(partial(self.on_click_label, item=item))
            self.qlineeditdict.update({item:qlineedit})
            self.layout.addRow(label, qlineedit)



        editdelete_grid = QGridLayout()
        editdelete_grid.addWidget(self.save, 0, 0)
        editdelete_grid.addWidget(self.delete, 0, 1)
        self.layout.addRow(editdelete_grid)

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
        queries = []
        for item in self.qlineeditdict:
            #compare to self.batchsequence_items doctopmaru
            if str(self.qlineeditdict[item].text()) != str(self.batchsequence_items[item]):
                logger.debug(f"self.qlineeditdict[item].text(), self.batchsequence_items[item]")
                batchsequence_changes_dict.update({item:self.qlineeditdict[item].text()})

        for item in self.buttoneditdict:
            if str(self.buttoneditdict[item].text()) != str(self.buttons_items[item]):
                logger.debug(self.buttoneditdict[item].text(), self.buttons_items[item])
                buttons_changes_dict.update({item:self.buttoneditdict[item].text()})
                
        
        changed_button_data = {"formname":self.pname.text(),"tab":self.tabs_dd.currentText(),"buttonname":self.bname.text()}   
        button_original = {"formname":self.pname_orig,"tab":self.tname_orig,"buttonname":self.bname_orig}
        new_button_data = {"formname":self.pname.text(),"tab":self.tabs_dd.currentText(),"buttonname":self.bname.text()}

        for item in button_original:
            if item in changed_button_data and changed_button_data[item] == button_original[item]:
                changed_button_data.pop(item)

        
        if len(changed_button_data) > 0:
            queries.append(self.make_update_query(changed_button_data, button_original, "buttons"))
            queries.append(self.make_update_query(changed_button_data, button_original, "batchsequence"))
            queries.append(self.make_update_query(changed_button_data, button_original, "buttonseries"))

        if len(buttons_changes_dict) > 0:
            queries.append(self.make_update_query(buttons_changes_dict, new_button_data, "buttons"))

        if len(batchsequence_changes_dict) > 0:
            queries.append(self.make_update_query(batchsequence_changes_dict, new_button_data, "batchsequence"))


        if len(queries) > 0:
            for query in queries:
                self.parent_.WriteSQL(query, msg=True)
        #exit popup
        
        self.parent_.Refresh()
        self.close()

    def grab_buttons_data(self):
        data = self.parent_.ReadSQL(f"SELECT buttonsequence,columnnum,buttondesc,buttongroup,active,treepath FROM buttons WHERE formname = '{self.pname_orig}' AND tab = '{self.tname_orig}' AND buttonname = '{self.bname_orig}'",msg=False)[0]
        db_buttons_columns = ["buttonsequence","columnnum","buttondesc","buttongroup","active","treepath"]
        data_dict = {}
        for item in range(len(data)):
            data_dict[db_buttons_columns[item]] = data[item]
        return data_dict



    def on_click_delete(self):
        #popup that asks to confirm if you want to delete
        #if yes, delete
        #if no, exit
        qm = QMessageBox()
        qm.setText("Are you sure you want to delete?")
        qm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        qm.setDefaultButton(QMessageBox.No)
        qm.setWindowTitle("Delete?")
        ret = qm.exec_()
        if ret == QMessageBox.Yes:
            #delete button
            #delete batchsequence
            queries = []
            queries.append(self.make_delete_query(self.pname_orig, self.tname_orig, self.bname_orig, "buttons"))
            queries.append(self.make_delete_query(self.pname_orig, self.tname_orig, self.bname_orig, "batchsequence"))
            queries.append(self.make_delete_query(self.pname_orig, self.tname_orig, self.bname_orig, "buttonseries"))
            for query in queries:
                self.parent_.WriteSQL(query, msg=True)
            self.parent_.Refresh()
            self.close()

    def make_delete_query(self, pname, tname, bname, table):
        query = "DELETE FROM " + table + " WHERE formname = '" + pname + "' AND tab = '" + tname + "' AND buttonname = '" + bname + "'"
        logger.debug(query)
        return(query)

    def make_update_query(self, changes_dict, search_dict, table):
        query = "UPDATE "+table+" SET "
        for item in changes_dict:
            query += item+" = '"+changes_dict[item]+"', "
        query = query[:-2]
        query += " WHERE "
        for item in search_dict:
            query += item+" = '"+search_dict[item]+"' AND "
        query = query[:-5]
        logger.debug(query)
        return query


class QLabel_temp(QLabel):
    clicked=pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()