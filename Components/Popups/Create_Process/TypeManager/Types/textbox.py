from .__important.TypeInterface import TypeInterface
from PyQt6.QtWidgets import  QFileDialog, QHBoxLayout, QLabel, QLineEdit



class textbox(TypeInterface):
    load = True
    params = ("type","description", "args", "optional")
    callname = ("text")
    hook_name = "textbox"
    data = None
    q_object = QLineEdit

    def load_self(self, hooks):
        None

    def main(self, callname, description, arguments, is_optional = False) -> None:
        self.is_optional = is_optional
       #only allow one folder to be selected
        self.q_widget = self.create_object()

        if is_optional:
            description = "(Optional) " + description
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(description))
        self.layout.addWidget(self.q_widget)
        return(self.layout)        

    def create_object(self):
        return self.q_object("")

    def validate_result(self) -> bool:
        self.data = self.q_widget.text()
        if self.data in (None, "") and not self.is_optional:
            self.q_widget.setStyleSheet("background-color: red")
            return False
        else:
            self.q_widget.setStyleSheet("background-color: None")
            return True

    def delete_all(self):
        self.q_widget.deleteLater()
        self.layout.deleteLater()