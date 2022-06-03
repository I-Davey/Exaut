from sys import maxunicode
from loguru import logger
import os
import pyperclip
#import QVBoxLayout
from functools import partial
import json
from PyQt5.QtWidgets import  QComboBox,   QFormLayout, QLineEdit,  QLabel, QPushButton, QDialog, QMessageBox, QGridLayout, QFileDialog, QMenu, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
import openpyxl
from openpyxl.worksheet.cell_range import CellRange


class data_transfer(QDialog):
    def __init__(self, parent_):
        
        super().__init__(parent_)
        self.parent_ = parent_
        self.resize(0, 150)
        self.setWindowTitle("Export/Import")
        self.layout = QFormLayout()
        self.items_layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addRow(self.items_layout)

        self.importloc = None
        self.importbtn = None
        self.import_folder = None
        #SELECT formname, tab, tabsequence, grid, tabdesc, treepath, tabgroup, tabsize, taburl FROM tabs; where formname = parent_title AND tab = tab_name

        
        #items



        ##first choice
        self.transfer_action = QComboBox()
        self.transfer_actions = ["","Export", "Import"]
        self.transfer_action.addItems(self.transfer_actions)
        self.transfer_action.currentIndexChanged.connect(self.transfer_action_changed)
        self.startlayout = QGridLayout()
        self.startlayout.addWidget(self.transfer_action, 0, 0)
        self.layout.addRow(self.startlayout)

        ##export data
        self.select_folder = None


        self.export_items_layout = QGridLayout()

        self.transfer_items = QComboBox()
        self.unactual_items = [" ", "Form", "Tab", "Button"]
        self.actual_items = ["forms","tabs", "buttons", "batchsequence", "buttonseries"]
        self.actual_items_column = ["formname", "tab", "buttonname", "buttonname", "assignname"]
        self.transfer_items.addItems(self.unactual_items)
        self.transfer_items.currentIndexChanged.connect(self.transfer_items_changed)
        self.export_button = QPushButton("Export")
        #self.export_button.clicked.connect(self.export_clicked)
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setDisabled(True)

        self.maxindex = 0
        self.widgetlist = []
        ##import data
        ##TBC


    def select_folder_clicked(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.select_folder.setText(dir)

    def transfer_action_changed(self):
        #delete and add back items_layout
        self.clear_all()
        self.items_layout.deleteLater()
        self.items_layout = QGridLayout()
        self.layout.addRow(self.items_layout)
        if self.import_folder:
            self.import_folder.deleteLater()
        if self.importbtn:
            self.importbtn.deleteLater()
        
        self.importloc, self.importbtn, self.import_folder = None, None, None

        if self.transfer_action.currentText() == "Export":
            self.add_export_items()

        elif self.transfer_action.currentText() == "Import":
            self.add_import_items()

    def add_import_items(self):
        #new QFileDrop item
        self.import_folder = QFileDrop(self.browse_file, self)
        self.import_folder.link_signal.connect(self.import_signal)

        self.layout.addRow(self.import_folder)

    def browse_file(self, qwidget_item):
        
        qwidget = qwidget_item
        file = QFileDialog.getOpenFileName(self, "Select File", filter="Excel Files (*.xlsx *.xlsm *.xlsb *.xls);;All Files (*.*)")
        if file[0] != "":
            qwidget.setText(file[0])
            self.importloc = file[0]

        if not self.importbtn:
            self.importbtn = QPushButton("Import")
            self.importbtn.clicked.connect(self.import_clicked)
            self.layout.addRow(self.importbtn)

        
    def browse_folder(self, qwidget_item):
        qwidget = qwidget_item
        file = QFileDialog.getExistingDirectory(self, "Select Directory")
        if type(file) in (tuple, list, set):
            file = file[0]
            qwidget.setText(file[0])
            self.importloc = file[0]

    def import_signal(self, data):
        if data != "":
            self.importloc = data

        if not self.importbtn:
            self.importbtn = QPushButton("Import")
            self.importbtn.clicked.connect(self.import_clicked)
            self.layout.addRow(self.importbtn)
            
    def import_clicked(self):
        if not self.importloc:
            return
        #fileloc = self.importloc.text()

        if type(self.importloc) in (tuple, list, set):
            self.importloc = self.importloc[0]
 
        xcel_data = openpyxl.load_workbook(self.importloc)
        #get all sheet names:
        sheet_names = xcel_data.sheetnames
        if 'ImportItem' not in sheet_names:
            logger.error("ImportItem sheet not found")
            return
        ws = xcel_data['ImportItem']
        #get names of tables in ws
        table_queries = []

        if 'ImportForm' in ws._tables:
            columns, data = self.handle_Import(ws._tables['ImportForm'], ws)
            form_data_sql = self.create_query(columns, data, "forms")
            table_queries.append(form_data_sql)

        if 'ImportTab' in ws._tables:
            columns, data = self.handle_Import(ws._tables['ImportTab'], ws)
            tab_data_sql = self.create_query(columns, data, "tabs")
            table_queries.append(tab_data_sql)
        
        if 'ImportButton' in ws._tables:
            columns, data = self.handle_Import(ws._tables['ImportButton'], ws)
            button_data_sql = self.create_query(columns, data, "buttons")
            table_queries.append(button_data_sql)

        if 'ImportBatchsequence' in ws._tables:
            columns, data = self.handle_Import(ws._tables['ImportBatchsequence'], ws)
            batch_data_sql = self.create_query(columns, data, "batchsequence")
            table_queries.append(batch_data_sql)

        if 'ImportButtonseries' in ws._tables:
            columns, data = self.handle_Import(ws._tables['ImportButtonseries'], ws)
            buttonseries_data_sql = self.create_query(columns, data, "buttonseries")
            table_queries.append(buttonseries_data_sql)

        for query in table_queries:
            self.parent_.WriteSQL(query)

        #popup saying Complete!
        self.popup = QMessageBox()
        self.popup.setText("Import Complete!")
        self.popup.exec_()

        

    def create_query(self,columns,  data, table_name):
        #columns decides what data to insert
        query = f"""INSERT OR REPLACE INTO {table_name} ("""
        for column in columns:
            query += f"{column}, "
        query = query[:-2]
        query += ") VALUES ("
        for i in data:
            for num,j in enumerate(i):
                if j is None:
                    i[num] = "null"
                else:
                    i[num] = f"'{j}'"
            for num,j in enumerate(i):
                if num == 0:
                    query += f"{j}"
                else:
                    query += f", {j}"
            if query[-1] == ",":
                query = query[:-1]
            query += "), ("
        query = query[:-3]
        return query

    def handle_Import(self, table, sheet):
        table_range = table.ref

        table_head = sheet[table_range][0]
        table_data = sheet[table_range][1:]

        columns = [column.value for column in table_head]
        data = []

        for row in table_data:
            row_val = [cell.value for cell in row]
            data.append(row_val)
        return columns, data


        



    def add_export_items(self):
        self.select_folder = QFileDrop(self.browse_folder, self)
        self.items_layout.addWidget(QLabel("Export Folder Location:"), 0, 0)
        self.items_layout.addWidget(self.select_folder, 0, 1)
        self.items_layout.addWidget(QLabel("Data Type:"), 1, 0)
        self.items_layout.addWidget(self.transfer_items, 1, 1)

    def transfer_items_changed(self):
        self.clear_all()
        if self.transfer_items.currentText() != " ":
            #reset old data
            self.widgetlist = []
            self.maxindex = 0
            self.export_items_layout.deleteLater()
            self.export_items_layout = QGridLayout()
            self.layout.addRow(self.export_items_layout)            #get position in unactual items that the user selected
            self.layout.addRow(self.export_button)

            selected_item = self.unactual_items.index(self.transfer_items.currentText())
            #remove all items in actual_items before that number for one var, and add back the items in unactual_items after that number for the other var
            self.actual_tables = self.actual_items[selected_item - 1 :]
            self.needed_data_tables = self.actual_items[:selected_item]
            self.needed_data_columns = self.actual_items_column[:selected_item]
            self.handle_needed_data(self.needed_data_tables, self.needed_data_columns)

    def clear_all(self):
        for widget in self.widgetlist:
            widget.deleteLater()
        self.widgetlist = []
        self.maxindex = 0
        self.export_items_layout.deleteLater()
        self.export_items_layout = QGridLayout()
        self.layout.addRow(self.export_items_layout)
        self.export_button.setDisabled(True)


    def handle_needed_data(self, tables, columns):
        #select distinct data[0] qcombox

        ReadSQL = self.parent_.ReadSQL

        query = f"SELECT DISTINCT  {columns[0]} FROM {tables[0]}"
        logger.info(query)
        data = ReadSQL(query)
        #[['COPY'], ['IAN'], ['SGX'], ['SQL'], ['exaut'], ['test']]
        #turn into ['COPY', 'IAN', 'SGX', 'SQL', 'exaut', 'test']
        data = [item[0] for item in data]

        logger.info(data)

        #create combobox
        export_items = QComboBox()
        export_items.addItem(" ")
        export_items.addItems(data)
        export_items.currentIndexChanged.connect(partial(self.export_items_changed, index = 0))
        self.export_items_layout.addWidget(export_items, 0, 0)
        self.widgetlist.append(export_items)
        self.maxindex = 0

        #select distinct data[1] where data[0] = data[0] qcombobox

    def export_items_changed(self, value_index, index = None):

        val_str = self.widgetlist[index].currentText()

        logger.success(f"index {index} maxindex {self.maxindex} value {val_str}")
        if (index == 0 and self.maxindex == 0)  or index > self.maxindex:
            if val_str == " ":
                return
            self.maxindex = index
            nextitem = index + 1
            if nextitem < len(self.needed_data_tables):
                query = self.querybuilder(self.needed_data_tables[nextitem], self.needed_data_columns[nextitem], self.needed_data_columns[0], val_str, index=index)
                logger.info(query)
                data = self.parent_.ReadSQL(query)
                data = [item[0] for item in data]
                logger.info(data)
                export_items = QComboBox()
                export_items.addItem(" ")
                export_items.addItems(data)
                export_items.currentIndexChanged.connect(partial(self.export_items_changed, index = nextitem))
                self.export_items_layout.addWidget(export_items, 0, nextitem)
                
                self.widgetlist.append(export_items)


        else:
            self.maxindex = index

            #every item after maxindex is deleted
            for i in range(self.maxindex + 1, len(self.widgetlist)):
                self.widgetlist[i].deleteLater()
            self.widgetlist = self.widgetlist[:self.maxindex + 1]
            if val_str == " ":
                return
            nextitem = index + 1
            if nextitem < len(self.needed_data_tables):
                query = self.querybuilder(self.needed_data_tables[nextitem], self.needed_data_columns[nextitem], self.needed_data_columns[0], val_str, index = index)
                logger.info(query)
                data = self.parent_.ReadSQL(query)
                data = [item[0] for item in data]

                export_items = QComboBox()
                export_items.addItem(" ")

                export_items.addItems(data)
                export_items.currentIndexChanged.connect(partial(self.export_items_changed, index = nextitem))
                self.export_items_layout.addWidget(export_items, 0, nextitem)
                self.widgetlist.append(export_items)

        if self.maxindex + 1 >= int(len(self.needed_data_tables) / 2):
            self.export_button.setEnabled(True)
        else:
            self.export_button.setDisabled(True)
    def querybuilder(self, table, column, column_to_check, value, index = None):

        if index == 0:
            #remove all after furst item in self.widgetlist
            for i in range(1,len(self.widgetlist) - 1):
                self.widgetlist[i].deleteLater()
            self.widgetlist = self.widgetlist[:1]
        #select distinct x where a = b and c = d
        querybase = f"SELECT DISTINCT  {column} FROM {table} WHERE"
        for i in range(len(self.widgetlist)):
            querybase += f" {self.needed_data_columns[i]} = '{self.widgetlist[i].currentText()}' AND "
        querybase = querybase[:-5]
        return querybase


    def export_data(self):
        #acutal items ~ transfer_items: Form = 1, Tab = 2, Button = 3
        if self.transfer_items.currentIndex() == 0:
            return
        elif self.transfer_items.currentIndex() == 1:
            self.export_form_data()
        elif self.transfer_items.currentIndex() == 2:
            self.export_tab_data()
        elif self.transfer_items.currentIndex() == 3:
            self.export_button_data()

    def export_form_data(self, form = None):
        if form == None:
            form = self.widgetlist[0].currentText()
        #formname, formdesc
        query1 = f"SELECT * from forms WHERE formname = '{form}'"
        form = self.parent_.ReadSQL(query1)[0]
        
        form_obj = Form_Object(form[0], form[1])

        tabs = self.parent_.ReadSQL(f"SELECT * from tabs WHERE formname = '{form_obj.formname}'")
        tab_objects = []
        for tab in tabs:
            tab_objects.append(Tab_Object(tab[0], tab[1], tab[2], tab[3], tab[4], tab[5], tab[6], tab[7]))
        
        buttons = self.parent_.ReadSQL(f"SELECT * from buttons WHERE formname = '{form_obj.formname}'")
        button_objects = []
        for button in buttons:
            button_objects.append(Button_Object(button[0], button[1], button[2], button[3], button[4], button[5], button[6], button[7], button[8]))

        batchsequence = self.parent_.ReadSQL(f"SELECT * from batchsequence WHERE formname = '{form_obj.formname}'")
        batchsequence_objects = []
        for batch in batchsequence:
            batchsequence_objects.append(Batchsequence_Object(batch[0], batch[1], batch[2], batch[3], batch[4], batch[5], batch[6], batch[7], batch[8], batch[9], batch[10], batch[11], batch[12], batch[13]))
        json_data = {}

        buttonseries_objects = []
        buttonseries = self.parent_.ReadSQL(f"SELECT * from buttonseries WHERE formname = '{form_obj.formname}'")
        for series in buttonseries:
            buttonseries_objects.append(Buttonseries_Object(series[0], series[1], series[2], series[3], series[4]))

        json_data["forms"] =  [form_obj.todict()]
        json_data["tabs"] = [tab.todict() for tab in tab_objects]
        json_data["buttons"] = [button.todict() for button in button_objects]
        json_data["batchsequence"] = [batch.todict() for batch in batchsequence_objects]
        json_data["buttonseries"] = [series.todict() for series in buttonseries_objects]

        self.save(json_data, form_obj.formname)

    def export_tab_data(self, tab = None):
        form = self.widgetlist[0].currentText()
        tab = self.widgetlist[1].currentText()
        query1 = f"SELECT * from tabs WHERE formname = '{form}' AND tab = '{tab}'"
        query1  = self.parent_.ReadSQL(query1)[0]
        tab_obj = Tab_Object(query1[0], query1[1], query1[2], query1[3], query1[4], query1[5], query1[6], query1[7])
        json_data = {}
        
        button_objects = []
        buttons = self.parent_.ReadSQL(f"SELECT * from buttons WHERE formname = '{form}' AND tab = '{tab}'")
        for button in buttons:
            button_objects.append(Button_Object(button[0], button[1], button[2], button[3], button[4], button[5], button[6], button[7], button[8]))
        
        batchsequence_objects = []
        batchsequence = self.parent_.ReadSQL(f"SELECT * from batchsequence WHERE formname = '{form}' AND tab = '{tab}'")
        for batch in batchsequence:
            batchsequence_objects.append(Batchsequence_Object(batch[0], batch[1], batch[2], batch[3], batch[4], batch[5], batch[6], batch[7], batch[8], batch[9], batch[10], batch[11], batch[12], batch[13]))

        series_key = []
        for batch in batchsequence_objects:
            if batch.type == "assignseries":
                series_key.append(batch.source)

        buttonseries_objects = []

        for item in series_key:
            query2 = f"SELECT * from buttonseries WHERE formname = '{form}' AND assignname = '{item}'"
            query2  = self.parent_.ReadSQL(query2)[0]
            buttonseries_objects.append(Buttonseries_Object(query2[0], query2[1], query2[2], query2[3], query2[4]))
        
        json_data["tabs"] = [tab_obj.todict()]
        json_data["buttons"] = [button.todict() for button in button_objects]
        json_data["batchsequence"] = [batch.todict() for batch in batchsequence_objects]
        json_data["buttonseries"] = [series.todict() for series in buttonseries_objects]
        self.save(json_data, f"{form}_{tab}.json")

    def export_button_data(self, button = None):
        form = self.widgetlist[0].currentText()
        tab = self.widgetlist[1].currentText()
        button = self.widgetlist[2].currentText()
        query1 = f"SELECT * from buttons WHERE formname = '{form}' AND tab = '{tab}' AND buttonname = '{button}'"
        query1  = self.parent_.ReadSQL(query1)[0]
        button_obj = Button_Object(query1[0], query1[1], query1[2], query1[3], query1[4], query1[5], query1[6], query1[7], query1[8])
        json_data = {}

        batchsequence_objects = []
        batchsequence = self.parent_.ReadSQL(f"SELECT * from batchsequence WHERE formname = '{form}' AND tab = '{tab}' AND buttonname = '{button}'")
        for batch in batchsequence:
            batchsequence_objects.append(Batchsequence_Object(batch[0], batch[1], batch[2], batch[3], batch[4], batch[5], batch[6], batch[7], batch[8], batch[9], batch[10], batch[11], batch[12], batch[13]))

        series_key = []
        for batch in batchsequence_objects:
            if batch.type == "assignseries":
                series_key.append(batch.source)

        buttonseries_objects = []

        for item in series_key:
            query2 = f"SELECT * from buttonseries WHERE formname = '{form}' AND assignname = '{item}'"
            query2  = self.parent_.ReadSQL(query2)
            for series in query2:
                buttonseries_objects.append(Buttonseries_Object(series[0], series[1], series[2], series[3], series[4]))

            

        json_data["buttons"] = [button_obj.todict()]
        json_data["batchsequence"] = [batch.todict() for batch in batchsequence_objects]
        json_data["buttonseries"] = [series.todict() for series in buttonseries_objects]
        self.save(json_data, f"{form}_{tab}_{button}.json")

    def save(self, json_data, filename):
        filename = "ExportItem.json"
        if self.select_folder.curtext() == "" or self.select_folder.curtext() == "Select Folder":
            self.select_folder.setText(os.getcwd())
        try:
            with open(os.path.join(self.select_folder.curtext(), filename), 'w') as f:
                json.dump(json_data, f, indent=4)
                logger.success(f"{filename} saved to {self.select_folder.curtext()}")
                QMessageBox.information(self, "Success", f"{filename} saved to {self.select_folder.curtext()}")
        except Exception as e:
            logger.error(f"{filename} could not be saved to {self.select_folder.curtext()}")
            logger.error(e)
            #pyqt error popup
            QMessageBox.warning(self, "Error", f"{filename} could not be saved to {self.select_folder.curtext()}. Check if it is open")
        #add button to open folder
        self.open_folder = QPushButton("Open Folder")
        self.open_folder.setText(self.select_folder.curtext())
        self.open_folder.clicked.connect(self.open_folder_clicked)
        self.open_folder.show()
        self.open_folder.setEnabled(True)
        self.open_folder.setVisible(True)

    def open_folder_clicked(self):
        os.startfile(self.open_folder.text())



class Form_Object:
    def __init__(self, formname, formdesc):
        self.formname = formname
        self.formdesc = formdesc
    def toarr(self):
        return [self.formname, self.formdesc]
    def todict(self):
        return {"formname": self.formname, "formdesc": self.formdesc}
class Tab_Object:
    def __init__(self, formname, tab_name, tab_sequence, grid, tab_desc, treepath, tab_group, tab_size):
        self.formname = formname
        self.tab_name = tab_name
        self.tab_sequence = tab_sequence
        self.grid = grid
        self.tab_desc = tab_desc
        self.treepath = treepath
        self.tab_group = tab_group
        self.tab_size = tab_size
    def toarr(self):
        return [self.formname, self.tab_name, self.tab_sequence, self.grid, self.tab_desc, self.treepath, self.tab_group, self.tab_size]
    def todict(self):
        return {"formname" :self.formname, "tab": self.tab_name, "tabsequence": self.tab_sequence, "grid": self.grid, "tabdesc": self.tab_desc, "treepath": self.treepath, "tabgroup": self.tab_group, "tabsize": self.tab_size}
class Button_Object:
    def __init__(self, formname, tab, buttonname, buttonsequence, columnnum, buttondesc, buttongroup, active, treepath):
        #buttonname, buttonsequence, columnnum, buttondesc, buttongroup, active, treepath
        self.formname = formname
        self.tab = tab
        self.buttonname = buttonname
        self.buttonsequence = buttonsequence
        self.columnnum = columnnum
        self.buttondesc = buttondesc
        self.buttongroup = buttongroup
        self.active = active
        self.treepath = treepath
    def toarr(self):
        return [self.formname, self.tab, self.buttonname, self.buttonsequence, self.columnnum, self.buttondesc, self.buttongroup, self.active, self.treepath]
    def todict(self):
        return {"formname": self.formname, "tab": self.tab, "buttonname": self.buttonname, "buttonsequence": self.buttonsequence, "columnnum": self.columnnum, "buttondesc": self.buttondesc, "buttongroup": self.buttongroup, "active": self.active, "treepath": self.treepath}
class Batchsequence_Object:
    def __init__(self, formname, tab, buttonname,runsequence, folderpath, filename, type, source, target, databasepath, databasename, keypath, keyfile, treepath):
        self.formname = formname
        self.tab = tab
        self.buttonname = buttonname
        self.runsequence = runsequence
        self.folderpath = folderpath
        self.filename = filename
        self.type = type
        self.source = source
        self.target = target
        self.databasepath = databasepath
        self.databasename = databasename
        self.keypath = keypath
        self.keyfile = keyfile
        self.treepath = treepath
    def toarr(self):
        return [self.formname, self.tab, self.buttonname, self.runsequence, self.folderpath, self.filename, self.type, self.source, self.target, self.databasepath, self.databasename, self.keypath, self.keyfile, self.treepath]
    def todict(self):
        return {"formname": self.formname, "tab": self.tab, "buttonname": self.buttonname, "runsequence": self.runsequence, "folderpath": self.folderpath, "filename": self.filename, "type": self.type, "source": self.source, "target": self.target, "databasepath": self.databasepath, "databasename": self.databasename, "keypath": self.keypath, "keyfile": self.keyfile, "treepath": self.treepath}   
class Buttonseries_Object:
    def __init__(self, formname, tab, buttonname, assignname, runsequence):
        self.formname = formname
        self.tab = tab
        self.buttonname = buttonname
        self.assignname = assignname
        self.runsequence = runsequence
    def toarr(self):
        return [self.formname, self.tab, self.buttonname, self.assignname, self.runsequence]
    def todict(self):
        return {"formname": self.formname, "tab": self.tab, "buttonname": self.buttonname, "assignname": self.assignname, "runsequence": self.runsequence}

    #runsequence, folderpath, filename, "type", "source", target, databasepath, databasename, keypath, keyfile, treepath



class QFileDrop(QWidget):
    link_signal = pyqtSignal(list)

    def __init__(self, call_func, text=False, parent=None):
         
        super(QFileDrop, self).__init__(parent)
        self.text = text
        self.setAcceptDrops(True)
        self.call_func = call_func
        self.parent_ = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.create_browse()
        self.add_browse()

    def create_browse(self):
        self.browse_ = QPushButton("Browse")
        self.browse_.clicked.connect(partial(self.call_func, self.browse_))

    def add_browse(self):

        self.gridlayout = QGridLayout()
        if self.text == True:
            self.qlabel_item = QLabel("Select Import File:")
            self.gridlayout.addWidget(self.qlabel_item, 0, 0)
        self.gridlayout.addWidget(self.browse_, 0, 1)
        self.layout.addLayout(self.gridlayout)
        #add right click menu
        self.browse_.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browse_.customContextMenuRequested.connect(self.right_click_menu)


    def right_click_menu(self, pos):
        menu = QMenu()
        menu.addAction("copy file/folder", self.copy_file)
        menu.addAction("copy full path", self.copy_file_path)
        menu.exec_(self.browse_.mapToGlobal(pos))

    def copy_file(self):
        text = self.browse_.text()
        if text != "":
            #split by \\ or / and get last item
            if "\\" in text:
                text = text.split("\\")[-1]
            elif "/" in text:
                text = text.split("/")[-1]
            
            
        pyperclip.copy(text)

    def copy_file_path(self):
        text = self.browse_.text()
        if text != "":
            pyperclip.copy(text)
        

    def setText(self, text):
        self.browse_.setText(text)

    def remove_browse(self):
        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.browse_)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.link_signal.emit( links)
            self.browse_.setText(links[0])

    def browse_folder(self, db_key):
        qwidget = self.type_data[db_key]["qwidget"]
        dir_ = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_ != "":
            qwidget.setText(dir_)
            self.type_data[db_key]["result"] = dir_
  
    def curtext(self):
        return self.browse_.text()