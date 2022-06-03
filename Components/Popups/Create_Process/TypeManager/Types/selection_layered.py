from .__important.TypeInterface import TypeInterface
from PyQt5.QtWidgets import  QVBoxLayout, QHBoxLayout, QLabel, QComboBox



class selection_layered(TypeInterface):
    load = True
    params = ("type","description", "args", "optional")
    callname = ("selection_layered")
    hook_name = "selection_layered"
    data = None
    q_object = QComboBox

    def load_self(self, hooks):
        None

    def main(self, callname, description, arguments, is_optional = False) -> None:
        self.is_optional = is_optional
       #only allow one folder to be selected
        self.qcombo1 = self.create_object()
        self.qcombo1.addItem(" ")
        self.qcombo2 = self.create_object()
        self.qcombo2.addItem(" ")
        self.qcombo3 = []


        for i, item in enumerate(arguments):
            self.qcombo1.addItem(item)
            #another combo box
            self.qcombo3.append([])

            for data in arguments[item]:
                self.qcombo3[i] += [data]
        self.q_widget = [self.qcombo1, self.qcombo2]
        self.qcombo1.currentIndexChanged.connect(self.selection_layered_changed)

        if is_optional:
            description = "(Optional) " + description
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(description[0]))
        self.layout.addWidget(self.qcombo1)
        self.layout2 = QHBoxLayout()
        self.layout2.addWidget(QLabel(description[1]))
        self.layout2.addWidget(self.qcombo2)
        self.layout3 = QVBoxLayout()
        self.layout3.addLayout(self.layout)
        self.layout3.addLayout(self.layout2)

        return(self.layout3)        

    def create_object(self):
        return self.q_object()

    def validate_result(self) -> bool:
        self.data = self.qcombo2.currentText()
        if self.data in (None, "") and not self.is_optional:
            self.q_widget.setStyleSheet("background-color: red")
            return False
        else:
            self.q_widget.setStyleSheet("background-color: None")
            return True

    def selection_layered_changed(self, index):
            index = index.currentIndex() - 1
            self.qcombo2.clear()
            self.qcombo2.addItem(" ")
            for i, item in enumerate(self.qcombo3[index]):
                self.qcombo2.addItem(item[0])

    def delete_all(self):
        self.qcombo1.deleteLater()
        self.qcombo2.deleteLater()
        self.layout.deleteLater()
        self.layout2.deleteLater()
        self.layout3.deleteLater()