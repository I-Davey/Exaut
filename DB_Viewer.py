from functools import partial
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import *
import sys,time

from pyparsing import col
from backend.db.Exaut_sql import *
from sqlalchemy import insert, select, create_engine
from time import perf_counter
from loguru import logger
import os
from sqlalchemy.orm import sessionmaker

#Insert Dialog box where user can register the students.


class DBHandler():
    def __init__(self,db_loc = "Z:\\Dev\\DB\\exaut.db"):
        self.logger = logger
        self.engine = create_engine(f'sqlite:///{db_loc}', echo=False, future=True)
        self.Session = sessionmaker(self.engine)
        self.check_tables_exist()

    def check_tables_exist(self):
        #if forms does not exist, create it
        for table in tables:
            if not  self.engine.dialect.has_table(self.engine.connect(), table):
                self.logger.debug(f"Table: {table} does not exist, creating")
                curtable = eval(table)
                curtable.metadata.create_all(self.engine)
                self.logger.success(f"Successfully created {table}")
        
    def readsql(self, query, one=False, log = False, timer = False):
        if log:
            self.logger.info(query.compile(dialect=self.engine.dialect))
        if timer:
            start = perf_counter()
        with self.Session.begin() as session:
            if one == True:
                data = session.execute(query).first()
            else:
                data = session.execute(query).all()
        if timer:
            end = perf_counter()
            self.logger.info(f"Query took {round((end-start),2)} seconds")

        return data
    
    def writesql(self, query, log = False):
        if log:
            self.logger.info(query.compile(dialect=self.engine.dialect))
        with self.Session.begin() as session:
            try:
                session.execute(query)
                return True
            except Exception as e:
                if e.__class__.__name__ == "IntegrityError":
                    #take text in e up to newline
                    e = e.__str__().split('\n')[0]
                    self.logger.error(f"{e.__class__.__name__}: {e}")
                else:
                    self.logger.error(f"Error: {e}")
                return False
            
    def get_table_query(self, tbl):
        info_arr = []
        session = self.Session()
        for row in session.query(tbl).all():
            row_dict = row.__dict__
            #remove the _sa_instance_state attribute
            del row_dict["_sa_instance_state"]
            info_arr.append(row_dict)
        session.close()
        return info_arr
            
    
    def read_mult(self, queries:list, log = False):
        with self.Session.begin() as session:
            for query in queries:
                if log:
                    self.logger.info(query.compile(dialect=self.engine.dialect))
                data = session.execute(query).all()
                yield data


class InsertDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(InsertDialog, self).__init__(*args, **kwargs)

        self.QBtn = QPushButton()   #create Push button
        self.QBtn.setText("Register")

        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)
        self.setFixedHeight(250)

        self.QBtn.clicked.connect(self.addstudent)

        layout = QVBoxLayout()  #set verticle layout

        self.nameinput = QLineEdit()
        self.nameinput.setPlaceholderText("Name")
        layout.addWidget(self.nameinput)

        self.branchinput = QComboBox() # create and add value to combobox
        self.branchinput.addItem("Mechanical")
        self.branchinput.addItem("Civil")
        self.branchinput.addItem("Electrical")
        self.branchinput.addItem("Electronics and Communication")
        self.branchinput.addItem("Computer Science")
        self.branchinput.addItem("Information Technology")
        layout.addWidget(self.branchinput)

        self.seminput = QComboBox()
        self.seminput.addItem("1")
        self.seminput.addItem("2")
        self.seminput.addItem("3")
        self.seminput.addItem("4")
        self.seminput.addItem("5")
        self.seminput.addItem("6")
        self.seminput.addItem("7")
        self.seminput.addItem("8")
        layout.addWidget(self.seminput)

        self.mobileinput = QLineEdit()
        self.mobileinput.setPlaceholderText("Mobile")
        self.mobileinput.setInputMask('99999 99999') # set validator for user can only input interger input
        layout.addWidget(self.mobileinput)

        self.addressinput = QLineEdit()
        self.addressinput.setPlaceholderText("Address")
        layout.addWidget(self.addressinput)

        layout.addWidget(self.QBtn)
        self.setLayout(layout)

# this function get value from all input box and insert these values in database.

    def addstudent(self):

        name = ""
        branch = ""
        sem = -1
        mobile = -1
        address = ""

        name = self.nameinput.text()
        branch = self.branchinput.itemText(self.branchinput.currentIndex())
        sem = self.seminput.itemText(self.seminput.currentIndex())
        mobile = self.mobileinput.text()
        address = self.addressinput.text()

class SearchDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)

        self.QBtn = QPushButton()
        self.QBtn.setText("Search")

        self.setWindowTitle("Search user")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.searchstudent)
        layout = QVBoxLayout()

        self.searchinput = QLineEdit()
        self.onlyInt = QIntValidator()
        self.searchinput.setValidator(self.onlyInt)
        self.searchinput.setPlaceholderText("Roll No.")
        layout.addWidget(self.searchinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)

    def searchstudent(self):

        searchrol = ""
        searchrol = self.searchinput.text()


class DeleteDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeleteDialog, self).__init__(*args, **kwargs)

        self.QBtn = QPushButton()
        self.QBtn.setText("Delete")

        self.setWindowTitle("Delete Student")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.deletestudent)
        layout = QVBoxLayout()

        self.deleteinput = QLineEdit()
        self.onlyInt = QIntValidator()
        self.deleteinput.setValidator(self.onlyInt)
        self.deleteinput.setPlaceholderText("Roll No.")
        layout.addWidget(self.deleteinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)

    def deletestudent(self):

        delrol = ""
        delrol = self.deleteinput.text()
        


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        self.setFixedWidth(300)
        self.setFixedHeight(250)

        QBtn = QDialogButtonBox.StandardButton.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("STDMGMT")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        labelpic = QLabel()
        pixmap = QPixmap('icon/logo.png')
        pixmap = pixmap.scaledToWidth(275)
        labelpic.setPixmap(pixmap)
        labelpic.setFixedHeight(150)

        layout.addWidget(title)

        layout.addWidget(QLabel("Version 5.3.2"))
        layout.addWidget(QLabel("Copyright 2018 CYB Inc."))
        layout.addWidget(labelpic)


        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.data_changed =  []
        self.dels = []
        self.db = DBHandler()
        file_menu = self.menuBar().addMenu("&File")

        help_menu = self.menuBar().addMenu("&About")
        self.setWindowTitle("Student Management CRUD")

        self.setMinimumSize(800, 600)

        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.on_context_menu)
        self.tableWidget.cellChanged.connect(self.cellChanged)
        

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        self.select_form_dropdown = QComboBox()
        self.select_form_dropdown.addItems(tables)
        toolbar.addWidget(self.select_form_dropdown)
        self.select_form_dropdown.currentIndexChanged.connect(self.loaddata)

        self.max_records_num = QSpinBox()
        self.max_records_num.setMinimum(1)
        self.max_records_num.setMaximum(100000)
        self.max_records_num.setValue(100)
        toolbar.addWidget(self.max_records_num)

        btn_ac_refresh = QAction(QIcon(refresh_pixmap),"Refresh",self)
        btn_ac_refresh.triggered.connect(self.loaddata)
        btn_ac_refresh.setStatusTip("Refresh Table")
        toolbar.addAction(btn_ac_refresh)

        btn_ac_adduser = QAction(QIcon(add_pixmap), "Add Student", self)
        btn_ac_adduser.triggered.connect(self.insert)
        btn_ac_adduser.setStatusTip("Add Record")
        toolbar.addAction(btn_ac_adduser)



        btn_ac_search = QAction(QIcon(search_pixmap), "Search", self)
        btn_ac_search.triggered.connect(self.search)
        btn_ac_search.setStatusTip("Search for Record")
        toolbar.addAction(btn_ac_search)

        btn_ac_delete = QAction(QIcon(trash_pixmap), "Delete", self)
        btn_ac_delete.triggered.connect(self.delete)
        btn_ac_delete.setStatusTip("Delete Record")
        toolbar.addAction(btn_ac_delete)

        adduser_action = QAction(QIcon(add_pixmap),"Insert Student", self)
        adduser_action.triggered.connect(self.insert)
        file_menu.addAction(adduser_action)

        searchuser_action = QAction(QIcon(search_pixmap), "Search Student", self)
        searchuser_action.triggered.connect(self.search)
        file_menu.addAction(searchuser_action)

        deluser_action = QAction(QIcon(trash_pixmap), "Delete", self)
        deluser_action.triggered.connect(self.delete)
        file_menu.addAction(deluser_action)
 
        

        about_action = QAction(QIcon(info_pixmap),"Developer", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)


    def cellChanged(self, row, column):
        if row in self.dels:
            return
        #highlight row green when cell is changed
        self.tableWidget.item(row, column).setBackground(QColor(0, 255, 0))

        data_in_row = []
        #append all data in row to list
        for i in range(self.tableWidget.columnCount()):
            data_in_row.append(self.tableWidget.item(row, i).text())
        self.data_changed.append({"type":"update", "new_data":data_in_row, "original_data":self.original_data_arr[row]})




    def on_context_menu(self, point):
        if self.tableWidget.itemAt(point):
            if self.tableWidget.itemAt(point).row() in self.dels:
                menu = QMenu()
                undel = menu.addAction("Undelete", partial(self.undelete_row, point)) 
                action = menu.exec(self.tableWidget.mapToGlobal(point))
                return
            else:
                #context menu should only show up if a vertical header is clicked
                #^^^will add that in later
                #three option should show up: add, delete, filter
                menu = QMenu()
                add_action = menu.addAction("Add")
                delete_action = menu.addAction("Delete")
                filter_action = menu.addAction("Filter")
                action = menu.exec(self.tableWidget.mapToGlobal(point))
                if action == add_action:
                    #self.insert_row(point)
                    pass
                elif action == delete_action:
                    self.delete_row(point)
                elif action == filter_action:
                    #self.filter()
                    pass
                return

    def undelete_row(self, point):
        row = self.tableWidget.indexAt(point).row()
        #set row to red
        #add row to self.data_changed with type delete and no header "new_data"
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.item(row, i).setData(Qt.ItemDataRole.BackgroundRole, None)
        for item in self.data_changed:
            if item["type"] == "delete" and item["original_data"][0] == self.original_data_arr[row][0]:
                self.data_changed.remove(item)
                break
        self.dels.remove(row)


        


    def delete_row(self, point):
        #delete row
        #using indexAt to get the row number
        row = self.tableWidget.indexAt(point).row()
        self.dels.append(row)
        #set row to red
        #add row to self.data_changed with type delete and no header "new_data"
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.item(row, i).setBackground(QColor(255, 0, 0))
        self.data_changed.append({"type":"delete", "new_data":None, "original_data":self.original_data_arr[row]})




    def loaddata(self):
        self.tableWidget.cellChanged.disconnect(self.cellChanged)
        self.clear()
        db = eval(self.select_form_dropdown.currentText())
        

        #get the column names and types from the database
        cols = db.__table__.columns
        self.cols = [(c.name, c.type.python_type) for c in cols]
        #set column count len of cols
        self.tableWidget.setColumnCount(len(self.cols))
        for i, (name, type_) in enumerate(self.cols):
            #set header labels
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(name))
        self.load_records()
        self.tableWidget.cellChanged.connect(self.cellChanged)

        None
    
    def clear(self):
        #clear horizontal headers
        #clear all rows in table
        self.tableWidget.setHorizontalHeaderLabels([])
        #clear vertical headers
        self.tableWidget.setVerticalHeaderLabels([])
        #clear items in tablewidget
        self.tableWidget.clear()

    def load_records(self, num = None):
        if num is None:
            num = self.max_records_num.value()
        #load first 10 records
        objects_to_select = (eval(f"{self.select_form_dropdown.currentText()}.{x}") for x, y in self.cols)
        objects_to_select = list(objects_to_select)

        records = self.db.readsql(select(*objects_to_select).limit(num))
        self.tableWidget.setRowCount(len(records))
        self.original_data_arr = []
        for i, record in enumerate(records):
            self.original_data_arr.append(record)
            for j, value in enumerate(record):

                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))




        """
    def handlePaintRequest(self, printer):
        document = QTextDocument()
        cursor = QTextCursor(document)
        model = self.table.model()
        table = cursor.insertTable(
            model.rowCount(), model.columnCount())
        for row in range(table.rows()):
            for column in range(table.columns()):
                cursor.insertText(model.item(row, column).text())
                cursor.movePosition(QTextCursor.NextCell)
        document.print_(printer)
"""
    def insert(self):
        dlg = InsertDialog()
        dlg.exec()

    def delete(self):
        dlg = DeleteDialog()
        dlg.exec()

    def search(self):
        dlg = SearchDialog()
        dlg.exec()

    def about(self):
        dlg = AboutDialog()
        dlg.exec()




app = QApplication(sys.argv)
add_icon_64     =   b'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'
info_icon_64    =   b'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'
refresh_icon_64 =   b'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'
search_icon_64  =   b'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'
trash_icon_64   =   b'iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABmJLR0QA/wD/AP+gvaeTAAADR0lEQVRYCe2ZsWoUURSG7x1TCEGCIpYWgayNYGMtbqGdliJBxGiRwsJKwc43iKixSrCJkDdQUgn6ADaKhCgi2okYgyDJzo5nIGdZlrAzMnPmzOIX7uXMZmbOf+f7diYbNgR+IAABCEAAAhCAAAQgAAEIQAACEIAABP4XArFNF3r9zpuTadpbilk4J+s6LrPK+C4nvw5Zdm/taXdLtls5WiMgh9/v9d4KpaMyaxtygT/6SXbm+ePu19qa1tgoqbFXpVb5O18a1Apf+oUshGOxH5fy7TbO1giQx84FQ0CWvSste6rS2fWefGS43dryeXl6DP/m37av3X4lb/7BOTODrZZttOYOaBmXxpaDgMZQHxyEgIO5NPbbSs/ZcasceQaPO7SV+6r+DSp7UdwBZUkZHYcAI7Bl2yKgLCmj4xBgBLZsWwSUJWV0XG2fgib9U08RX6tPRdwBReSN9yPAGHBRewQUETLejwBjwEXtEVBEyHg/AowBF7VHQBEh4/21/R8wus5n65vD30iN7h683vy0PdjONzqz47+8sj4+X0M+F652zNjk/XVyBygJp4oAJ/AaiwAl4VQR4AReYxGgJJwqApzAaywClIRTRYATeI1FgJJwqghwAq+xCFASThUBTuA1FgFKwqkiwAm8xiJASThVBDiB11gEKAmnigAn8BqLACXhVBHgBF5jEaAknCoCnMBrLAKUhFNFgBN4jUWAknCqCHACr7EIUBJOFQFO4DUWAUrCqSLACbzGIkBJOFUEOIHXWAQoCaeKACfwGosAJeFUEeAEXmMRoCScKgKcwGssApSEU0WAE3iNRYCScKpThrm/pfe0zLGjMzszdv/oTuvj9/N29qt5MbsDshC+mK/eLqCxtSdW15DE7KVVb+u+MYYX1hna30xASJNVCUllTtSIIfSyNFttatFmAm7Mz72Ti3gic7JGDA8X5k99aGrRZgLyC9jd/nVX6obMyRjy2Px84tv9JhdrKmBx8ezedLJ3KcS4LBeVymzrSLMYHu3+3Ln8oNvtNblIeeQ1E7eyvnX6UOjfkrSLMmdlHpbpOf5I+McYs41+TFZuXpl7L68ZEIAABCAAAQhAAAIQgAAEIAABCEAAAhAwI/AXGrBtEJ6QYIQAAAAASUVORK5CYII='
add_pixmap = QPixmap()
add_pixmap.loadFromData(QByteArray.fromBase64(add_icon_64))
info_pixmap = QPixmap()
info_pixmap.loadFromData(QByteArray.fromBase64(info_icon_64))
trash_pixmap = QPixmap()
trash_pixmap.loadFromData(QByteArray.fromBase64(trash_icon_64))
refresh_pixmap = QPixmap()
refresh_pixmap.loadFromData(QByteArray.fromBase64(refresh_icon_64))
search_pixmap = QPixmap()
search_pixmap.loadFromData(QByteArray.fromBase64(search_icon_64))
trash_pixmap = QPixmap()
trash_pixmap.loadFromData(QByteArray.fromBase64(trash_icon_64))

window = MainWindow()
window.show()
window.loaddata()
sys.exit(app.exec())