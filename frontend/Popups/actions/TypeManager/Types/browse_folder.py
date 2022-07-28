from .__important.TypeInterface import TypeInterface
from PyQt6.QtWidgets import  QFileDialog, QHBoxLayout, QLabel, QPushButton
from os.path import isdir


class browse_folder(TypeInterface):
    load = True
    params = ("type", "description", "args", "optional")
    callname = ("folder")
    hook_name = "browse_folder"
    data = None
    q_object = QFileDialog.getExistingDirectory

    def load_self(self, hooks):
        None

    def main(self, callname, description, arguments, is_optional = False) -> None:
        self.is_optional = is_optional
       #only allow one folder to be selected
        self.button = QPushButton("Select Folder")
        self.button.clicked.connect(self.handle_click)
        if is_optional:
            description = "(Optional) " + description
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(description))
        self.layout.addWidget(self.button)
        return(self.layout)        

    def create_object(self, arguments = None, *some, **other):

        return(self.handle_click)

        
    def handle_click(self, folder, **other):
        #if folder is a folder
        if folder and isdir(folder):

            return self.q_object(None, "Select Folder", folder, QFileDialog.Option.ShowDirsOnly )
        else:
            return self.q_object(None, "Select Folder", "", QFileDialog.Option.ShowDirsOnly)
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