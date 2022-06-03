from .__important.TypeInterface import TypeInterface
from PyQt5.QtWidgets import QPushButton, QPushButton, QWidget, QVBoxLayout, QMenu, QGridLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
import pyperclip
from functools import partial

class QFileDrop(QWidget):
    link_signal = pyqtSignal(list)

    def __init__(self, call_func, db_key, type_args=None, type_description=None):
        
        super(QFileDrop, self).__init__()
        self.setAcceptDrops(True)
        self.call_func = call_func
        self.db_key = db_key
        self.type_args = type_args
        self.type_description = type_description
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.create_browse()
        self.add_browse()

    def create_browse(self):
        self.browse_ = QPushButton("Browse")
        self.browse_.clicked.connect(self.handle_call_func)


    def handle_call_func(self, args = None):
        if self.db_key == "drag_drop_file":
            res = self.call_func(args)
        else:
            res = self.call_func()
        if res:
            if type(res) == tuple:
                res = res[0] 
            self.browse_.setText(res)

    def add_browse(self):
        self.layout.addWidget(self.browse_)
        #add right click menu
        self.browse_.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browse_.customContextMenuRequested.connect(self.right_click_menu)
        self.browse_.setToolTip(self.type_description)


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

    def getText(self):
        return self.browse_.text()

    def remove_browse(self):
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

    

class drag_drop(TypeInterface):
    load = True
    params = ("type", "description", "args", "optional") #these are  all
    callname = ("drag_drop_folder", "drag_drop_file", "drag_drop")
    hooks = ("browse_file", "browse_folder")
    data = None
    link_signal = pyqtSignal(list)
    q_object = QFileDrop

    def load_self(self, hooks):
        self.browse_file = hooks["browse_file"]()
        self.browse_folder = hooks["browse_folder"]()

    def main(self, callname, description, arguments, is_optional = False) -> None:
        self.is_optional = is_optional
        if callname == "drag_drop_folder":
            hook = self.browse_folder
        else:
            hook = self.browse_file
        self.q_widget = self.q_object(hook, callname, arguments, description)
        self.q_widget.link_signal.connect(self.drag_drop_signal)

        
        if is_optional:
            description = "(Optional) " + description

        return(description, self.q_widget)
        
    def create_object(self):
        return(QFileDrop)


    def drag_drop_signal(self, data):
        self.data = data[0]


    def validate_result(self) -> bool:
        self.data = self.q_widget.getText()
        if self.data in (None, "", "Browse") and not self.is_optional:
            self.q_widget.setStyleSheet("background-color: red")
            return False
        else:
            self.q_widget.setStyleSheet("background-color: None")
            return True

    def delete_all(self):
        self.q_widget.remove_browse()
        self.q_widget.deleteLater()
        