from __important.PluginInterface import PluginInterface


from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from pandas import DataFrame, read_excel


class WWG_GDrive_xlsx_filter(PluginInterface):
    load = True
    types = {"keyfile":8}
    type_types = {"keyfile":{"type":"drag_drop_file", "description":"please select the excel document"}}

    callname = "wwgdrive_filter"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}





    def main(self,xlsx_loc, Popups):
        self.logger.success(f"xlsx_loc: {xlsx_loc}")
        #load the excel file and get the dataframe
        try:
            df = read_excel(xlsx_loc)
        except Exception as e:
            Popups.alert("Error", str(e))
            return False
        

            

        dialog = Dialog
        x = Popups.custom(dialog)
        if x is None:
            return
        keywords, folder, filetype, start_date, end_date, is_date_filtered = x
        if not is_date_filtered:
            start_date = None
            end_date = None
        if keywords is None:
            Popups.alert("Please enter keywords")
            return
        keywords = keywords.split(",")


        #df headers: File	File Type	Folder Location	Link	Path	URL	Modified	Modified By	Created
        #modified/created format = 2022-01-03T10:06:24.558Z
        #filter on df
        #print df headers
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        #delete first column
        df = df.drop(df.columns[0], axis=1)
        print(df.columns)
    
        df = df[df["File"].str.contains("|".join(keywords))]
        df = df[df["Folder Location"].str.contains(folder)]
        df = df[df["File Type"].str.contains(filetype)]
        df = df[df["Modified"].str.contains(start_date)] if start_date else df
        df = df[df["Modified"].str.contains(end_date)] if end_date else df
        print(df.head())
        
        self.logger.debug(x)
        Popups.alert(x)

class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4
    signal = pyqtSignal(tuple)
    _done = False

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.is_date_filtered = False

        keywords_label = QLabel("Keywords:")
        self.keywords = QLineEdit()
        self.keywords.setPlaceholderText("Enter keywords separated by commas")

        folder_label = QLabel("Folder:")
        self.folder_combobox = QComboBox()
        self.folder_combobox.addItem("Any")

        filetype_label = QLabel("File Type:")
        self.filetype_combobox = QComboBox()
        self.filetype_combobox.addItem("Any")

        start_date_label = QLabel("Start Date:")
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)
        self.start_date.setEnabled(False)

        end_date_label = QLabel("End Date:")
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setEnabled(False)


        filter_date_label = QLabel("Filter on Date?")
        self.filter_date = QCheckBox()
        self.filter_date.setChecked(False)
        self.filter_date.stateChanged.connect(self.filter_date_changed)


        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.accept)


        
        object_layout = QGridLayout()
        object_layout.addWidget(keywords_label, 0, 0)
        object_layout.addWidget(self.keywords, 0, 1)
        object_layout.addWidget(folder_label, 1, 0)
        object_layout.addWidget(self.folder_combobox, 1, 1)
        object_layout.addWidget(filetype_label, 2, 0)
        object_layout.addWidget(self.filetype_combobox, 2, 1)
        object_layout.addWidget(filter_date_label, 3, 0)
        object_layout.addWidget(self.filter_date, 3, 1)
        object_layout.addWidget(start_date_label, 4, 0)
        object_layout.addWidget(self.start_date, 4, 1)
        object_layout.addWidget(end_date_label, 5, 0)
        object_layout.addWidget(self.end_date, 5, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(object_layout)
        main_layout.addWidget(self.filter_button)
        
        self.setLayout(main_layout)
        self.setWindowTitle("WWG GDrive XLSX Filter")
        
        self.setWindowTitle("Form Layout - pythonspot.com")
        
    def filter_date_changed(self, state):
        if state == 2:
            self.start_date.setEnabled(True)
            self.end_date.setEnabled(True)
            self.is_date_filtered = True
        else:
            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)
            self.is_date_filtered = False
            

    def closeEvent(self, a0) -> None:
        if self._done:
            self.signal.emit((self.keywords.text(), self.folder_combobox.currentText(), self.filetype_combobox.currentText(), self.start_date.date().toPyDate(), self.end_date.date().toPyDate(), self.is_date_filtered))
        else:
            self.signal.emit((None,))
            self.close()
        self.close()
        a0.accept()


    def accept(self):
        self._done = True
        self.close()



