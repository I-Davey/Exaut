from .__important.TypeInterface import TypeInterface
from PyQt6.QtWidgets import  QFileDialog, QHBoxLayout, QLabel, QPushButton
from functools import partial
from os.path import isdir, isfile


class browse_file(TypeInterface):
    load = True
    params = ( "description", "optional")
    callname = ("file")
    hook_name = "browse_file"
    data = None
    q_object = QFileDialog.getOpenFileName

    def load_self(self, hooks):
        None

    def main(self, description, arguments = None, is_optional = False, hook = False) -> None:
        self.is_optional = is_optional
       #only allow one folder to be selected
        self.button = QPushButton("Select File, " )
        self.button.clicked.connect(partial(self.handle_click, arguments))
        if is_optional:
            description = "(Optional) " + description
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(description))
        self.layout.addWidget(self.button)
        return(self.layout)

    def create_object(self, arguments = None, *some, **other):

        return(self.handle_click)

        
    def handle_click(self,  file, arguments = None, **other):
        #if folder is a folder
        if file and isfile(file):
            #rightclick on file
            #get dir from folder
            file = file.split("\\")
            file.pop()
            file = "\\".join(file)
            return self.q_object(None, "Select File", file,  filter=arguments if arguments else "All Files (*)")
        return self.q_object(None, "Select File", filter=arguments if arguments else "All Files (*)" )

    def validate_result(self) -> bool:
        self.data = self.q_widget.selectedFiles()[0]
        if self.data in (None, "") and not self.is_optional:
            self.q_widget.setStyleSheet("background-color: red")
            return False
        else:
            self.q_widget.setStyleSheet("background-color: None")
            return True

    def delete_all(self):
        self.button.deleteLater()
        self.layout.deleteLater()