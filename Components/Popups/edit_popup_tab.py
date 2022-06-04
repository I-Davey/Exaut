from loguru import logger
#import QVBoxLayout
from PyQt6.QtWidgets import  QPushButton,   QFormLayout, QLineEdit,  QLabel, QPushButton, QDialog, QMessageBox, QGridLayout

class edit_popup_tab(QDialog):
    def __init__(self, parent_, tab_name):
        
        super().__init__(parent_)
        self.tab_name = tab_name
        self.resize(600, 300)
        self.setWindowTitle("Edit")
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        #SELECT formname, tab, tabsequence, grid, tabdesc, treepath, tabgroup, tabsize, taburl FROM tabs; where formname = parent_title and tabname = tab_name
        self.parent_ = parent_
        self.column_titles = ["Form Name", "Tab Name", "Tab Sequence", "Grid", "Tab Description", "Tree Path", "Tab Group", "Tab Size", "Tab URL"]
        self.column_titles_actual = ["formname", "tab", "tabsequence", "grid", "tabdesc", "treepath", "tabgroup", "tabsize", "taburl"]
        self.query = self.parent_.ReadSQL(f"SELECT formname, tab, tabsequence, grid, tabdesc, treepath, tabgroup, tabsize, taburl FROM tabs where formname = '{parent_.title}' and tab = '{tab_name}'")[0]
        #replace None with ""
        for i in range(len(self.query)):
            if self.query[i] == None:
                self.query[i] = ""
        #display each item as an editable text field
        self.orig_tab_name = self.query[1]
        self.tab_name = QLineEdit(self.query[1])
        #tab_name readonly
        #add to layout
        self.layout.addRow("Tab Name", self.tab_name )


        for i in range(2, len(self.column_titles)):
            self.layout.addRow(self.column_titles[i], QLineEdit(str(self.query[i])))
        save_button = QPushButton("Update")
        save_button.clicked.connect(lambda: self.on_click_save())
        self.layout.addRow(save_button)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_tab())
        Delete_all_button = QPushButton("Delete All")
        Delete_all_button.clicked.connect(lambda: self.delete_tab_all())
        #set delete all red
        Delete_all_button.setStyleSheet("background-color: red")
        delete_grid = QGridLayout()
        delete_grid.addWidget(delete_button, 0, 0)
        delete_grid.addWidget(Delete_all_button, 0, 1)
        self.layout.addRow(delete_grid)


    def closeEvent(self, event):
        #remove self from tab_edit_dict
        #check if self is in tab_edit_dict
        if self.parent_.tab_edit_dict.get(self.tab_name.text()) != None:
            self.parent_.tab_edit_dict.pop(self.tab_name.text())
        event.accept()

    def delete_tab(self):
        self.parent_.ReadSQL(f"DELETE FROM tabs where formname = '{self.parent_.title}' and tab = '{self.query[1]}'")
        self.parent_.Refresh()
        self.close()

    def delete_tab_all(self):
        #give user option to delete all tabs

        delete_all_question = QMessageBox.question(self, "Delete All DATA", "WARNING: THIS WILL DELETE ALL TABS AND BUTTONS ASSOCIATED WITH THIS TAB. DO YOU WANT TO PROCEED?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if delete_all_question == QMessageBox.StandardButton.Yes:
            self.parent_.ReadSQL(f"DELETE FROM tabs where formname = '{self.parent_.title}' and tab = '{self.query[1]}'")
            self.parent_.ReadSQL(f"DELETE FROM buttons where formname = '{self.parent_.title}' and tab = '{self.query[1]}'")
            self.parent_.ReadSQL(F"DELETE FROM batchsequence where formname = '{self.parent_.title}' and tab = '{self.query[1]}'")
            self.parent_.ReadSQL(f"DELETE FROM buttonseries where formname = '{self.parent_.title}' and tab = '{self.query[1]}'")
            self.parent_.Refresh()
            self.close()
            

    def on_click_save(self):
        #create dictionary with column_titles_actual and self.query called original_info_dict
        #if tab name is changed:
            
        original_info_dict = {}
        for i in range(0, len(self.column_titles_actual)):
            original_info_dict[self.column_titles_actual[i]] = self.query[i]
        
        #create dictionary called new_data which data wthin self.layout buttons and self.column_titles_actual
        new_data = {}
        columns_newdata = self.column_titles_actual[1:]
        for i in range(0, len(columns_newdata)):
            new_data[columns_newdata[i]] = self.layout.itemAt((i*2)+1).widget().text()
        #for value in new data, replace "" with None
        for key in new_data:
            if new_data[key] == "":
                new_data[key] = "NULL"
        #use make_update_query:
        newquery = self.make_update_query(new_data, original_info_dict, "tabs")
        if self.tab_name.text() != self.orig_tab_name:
            #update batchsequence set tabname = 'newtabname' where formname = 'formname' and tabname = 'oldtabname'

            tab_name_query = f"UPDATE batchsequence SET tab = '{self.tab_name.text()}' WHERE formname = '{self.parent_.title}' and tab = '{self.orig_tab_name}'"
            buttons_query = f"UPDATE buttons SET tab = '{self.tab_name.text()}' WHERE formname = '{self.parent_.title}' and tab = '{self.orig_tab_name}'"
            buttonseries_query = f"UPDATE buttonseries SET tab = '{self.tab_name.text()}' WHERE formname = '{self.parent_.title}' and tab = '{self.orig_tab_name}'"
            self.parent_.ReadSQL(tab_name_query)
            self.parent_.ReadSQL(buttons_query)
            self.parent_.ReadSQL(buttonseries_query)
        logger.success(newquery)
        self.parent_.ReadSQL(newquery)
        self.parent_.Refresh()
        self.close()

    def make_update_query(self, changes_dict, original_data, table):
        query = "UPDATE "+table+" SET "
        for item in changes_dict:
            if changes_dict[item] == "NULL":
                query += item+" = NULL, "
            else:
                query += item+" = '"+changes_dict[item]+"', "
        query = query[:-2]
        query += " WHERE "
        for item in original_data:
            #if original_data[item] != "":
            if original_data[item] != "":
                query += str(item)+" = '"+str(original_data[item])+"' AND "
        query = query[:-5]
        return query

