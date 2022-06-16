from PyQt6 import QtGui, QtCore
from loguru import logger
#import QVBoxLayout
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QGridLayout,  QFormLayout, QLineEdit, QComboBox, QLabel, QPushButton, QDialog,  QMessageBox
from functools import partial

class DragButton(QPushButton):

    def fake_init(self, parent_, bname):
        self.parent_ = parent_
        self.bname = bname

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.__mousePressPos = event.globalPosition().toPoint()
            self.__mouseMovePos = event.globalPosition().toPoint()
    
        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            # adjust offset from clicked point to origin of widget
            self.show()
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPosition().toPoint()
            self.raise_()
            diff = globalPos - self.__mouseMovePos
            diff.setX(0)

            newPos = self.mapFromGlobal(currPos + diff)
            logger.trace(f"{newPos.x()}, {newPos.y()}, {self.parent_.height()}")
            if newPos.y() < 80:
                newPos.setY(80)
            if newPos.y() > self.parent_.height() - 75:
                newPos.setY(self.parent_.height() - 75)
            self.__mouseMovePos = globalPos
            self.move(newPos)
            for item in self.parent_.button_items:
                if item["btn_item"] == self:
                    item["x"] = newPos.x()
                    item["y"] = newPos.y()
                    item["x_btn"].move(newPos.x()+self.width(), newPos.y())

        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            buttons = []
            for item in self.parent_.button_items:

                
                #add item to buttons array ordered by y position
                buttons.append([item['btn_item'].y(), item['btn_item'], item['x_btn']])

            buttons.sort(key=lambda x: x[0])
            self.parent_.reset_layout(buttons)
            moved = event.globalPosition().toPoint() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
        super(DragButton, self).mouseReleaseEvent(event)


class Create_sequence(QDialog):
    signal_save = QtCore.pyqtSignal(dict, dict, list)
    signal_delete = QtCore.pyqtSignal() #(buttons_table_dict, batchsequence_table_dict, button_series_table_arr
    signal_update = QtCore.pyqtSignal(dict, dict, list ) 
    def __init__(self, parent, edit = False, data = {}):
        self.crashed = False
        self.is_finished = False
        self._parent = parent
        self.orderedbuttons = []
        super().__init__(parent)

        self.setWindowTitle("Sequence Builder")
        self.mainmainlayout = QVBoxLayout()
        self.mainlayout = QFormLayout()
        self.layout = QFormLayout()
        self.setLayout(self.mainmainlayout)
        self.button_items = []
        font = QtGui.QFont()
        font.setBold(True)
        self.resize(300,400)


        self.button_name = QLineEdit(self)
        self.button_name.setPlaceholderText("Enter Button Name")




        #        button_tabs.setFixedWidth(20)
        #        button_tabs.adjustSize()

        self.info_grid = QGridLayout()
        self.info_grid.setSpacing(10)
        self.info_grid.setContentsMargins(10, 10, 10, 10)
        self.info_grid.addWidget(self.button_name, 0, 0)
        self.mainlayout.addRow(self.info_grid)


        self.btn1x = QtCore.pyqtSignal(int)
        self.btn1y = QtCore.pyqtSignal(int)

        select_btn_text = QLabel("Select Buttons you want to use on main tab")
        select_btn_text.setFont(font)
        self.mainlayout.addRow(select_btn_text)
        self.mainlayout.addRow(self.layout)
        self.mainmainlayout.addLayout(self.mainlayout)

        if edit:
            self.button_save = QPushButton("Update")
            self.button_save.clicked.connect(partial(self.on_click_save, update=True))
            self.button_delete = QPushButton("Delete")
            self.button_delete.clicked.connect(self.on_click_delete)
            self.editgrid = QGridLayout()
            self.editgrid.setSpacing(10)
            self.editgrid.setContentsMargins(10, 10, 10, 10)
            self.editgrid.addWidget(self.button_save, 0, 0)
            self.editgrid.addWidget(self.button_delete, 0, 1)
            #add button save to very bottom right of app
            self.mainmainlayout.addStretch()
            self.mainmainlayout.addLayout(self.editgrid)
            if self.load_data(data) == False:
                return


        else:
            self.button_save = QPushButton("Create")
            self.curtab = self._parent.SM_Tabs.tabText(self._parent.SM_Tabs.currentIndex())
            self.button_save.clicked.connect(self.on_click_save)
            #add button save to very bottom right of app
            self.mainmainlayout.addStretch()
            self.mainmainlayout.addWidget(self.button_save)


    def on_click_delete(self , close = True):
        self.signal_delete_button.emit()
        if not close:
            self.is_finished = True
            self.close()

    def load_data(self, all_data): 
        data = all_data["current_batch"]
        self.edit_data = data
        self.button_name.setText(data["buttonname"])

        #select formname, tab, buttonname from buttonseries where assignname = data["source"] order by runsequence
        if data["source"] in("", None):
            #ERROR POPUP no source
            logger.error("no source")
            self.crashed = True
            self.close()
            return False
        grabbed_data = all_data["buttonseries_data"]
        
        for item in grabbed_data:
            self.add_button(item["tab"], item["buttonname"])

    def on_click_save(self, update = False):
        if not self.check_data():
            return
        logger.success(f"length of ordered buttons: {len(self.orderedbuttons)} \nlength of button_items: {len(self.button_items)}" )
        ordered_button_items = []
        for item in self.orderedbuttons:
            for item2 in self.button_items:
                if item[1] == item2["btn_item"]:
                    ordered_button_items.append(item2)
                    break
        for item in ordered_button_items:
            logger.debug(item["bname"])
        logger.success(f"ordered_button_items: {len(ordered_button_items)}")

        #buttons generation first
        buttons_table_dict = {}
        buttons_table_dict["buttonname"] = self.button_name.text()
        #self._parent.ReadSQL largest buttonsequence where formname and tab

        #batchsequence generation
        batchsequence_table_dict = {}
        batchsequence_table_dict["buttonname"] = self.button_name.text()
        batchsequence_table_dict["type"] = "assignseries"
        batchsequence_table_dict["source"] = self.button_name.text()
        if not update:
            batchsequence_table_dict["tab"] = self.curtab

        button_series_table_arr = []
        button_series_base_dict = {"formname" : "","tab" : "","buttonname" : "","assignname": "", "runsequence": 0}
        button_series_base_dict["assignname"] = self.button_name.text()

        for item in range(len(ordered_button_items)):
            button_series_base_dict_copy = button_series_base_dict.copy()
            button_series_base_dict_copy["tab"] = ordered_button_items[item]["tname"]
            button_series_base_dict_copy["buttonname"] = ordered_button_items[item]["bname"]
            button_series_base_dict_copy["runsequence"] = item
            button_series_table_arr.append(button_series_base_dict_copy)

        if update:


            self.signal_update.emit(buttons_table_dict, batchsequence_table_dict, button_series_table_arr)
        else:
            buttons_table_dict["formname"] =  self._parent.form_title
            buttons_table_dict["tab"] = self.curtab
            buttons_table_dict["buttonsequence"] = 0
            buttons_table_dict["columnnum"] = 0
            batchsequence_table_dict["formname"] = self._parent.form_title
            batchsequence_table_dict["tab"] = self.curtab
            batchsequence_table_dict["runsequence"] = 0
            for item in button_series_table_arr:
                item["formname"] = self._parent.form_title
            self.signal_save.emit(buttons_table_dict, batchsequence_table_dict, button_series_table_arr)
        self.is_finished = True
        self.close()

    def check_data(self):
        errormessage = ""
        is_fail = False
        if self.button_name.text() == "":
            logger.error("Button name is empty")
            errormessage += "Button name is empty\n"
            is_fail = True
        if len(self.orderedbuttons) == 0:
            logger.error("No buttons selected")
            errormessage += "No buttons selected\n"     
            is_fail = True
        if is_fail:  
            errormsg = QMessageBox()
            errormsg.setIcon(QMessageBox.Icon.Critical)
            errormsg.setText("Error: missing info")
            errormsg.setInformativeText(errormessage)
             #spawn error message over self app
            errormsg.move(int(self.pos().x()+self.frameGeometry().width()/8), int(self.pos().y()+self.frameGeometry().height()/4))

            errormsg.exec()
            return False
        else:
            return True

    def add_button(self,tname,bname):
        new_button = DragButton(bname, self)
        new_button.fake_init(self, bname)
        new_button_x = QPushButton("X")
        #run function self.clicked and send the button obj
        new_button_x.setFixedWidth(20)
        new_button_x.adjustSize()

        new_button_x.setStyleSheet("color: red; font-weight: bold;")
        
        grid = QGridLayout()
        grid.addWidget(new_button, 0, 0)
        grid.addWidget(new_button_x, 0, 1)
        self.layout.addRow(grid)
        x = len(self.orderedbuttons)
        arr = [x, new_button, new_button_x]
        dict_data = {"arrpos":x,"tname":tname,"bname":bname, "btn_item":new_button, "x":new_button.x(), "y":new_button.y(), "x_btn":new_button_x, "grid":grid}
        self.orderedbuttons.append(arr)
        self.button_items.append(dict_data)
        new_button_x.clicked.connect(lambda: self.remove_button(dict_data))


    def remove_button(self, data_dict):
        self.layout.removeRow(data_dict["grid"])
        self.button_items.remove(data_dict)
        for item in self.orderedbuttons:
            if item[1] == data_dict["btn_item"]:
                self.orderedbuttons.remove(item)
                break
        self.resizeEvent(QtGui.QResizeEvent(self.size(), QtCore.QSize()))



    def closeEvent(self, event):
        if self.crashed:
            event.accept()
            return
        self._parent.current_sequence = None           


    def reset_layout(self, buttons):
        #remove from layout
        for item in self.button_items:

            item["grid"].removeWidget(item["btn_item"])
            item["grid"].removeWidget(item["x_btn"])
            self.layout.removeRow(item["grid"])

        self.orderedbuttons = buttons
        for item in buttons:
            grid = QGridLayout()
            grid.addWidget(item[1], 0, 0)
            grid.addWidget(item[2], 0, 1)
            self.layout.addRow(grid)
            #replace grid in button_items
            for button in self.button_items:
                if button["btn_item"] == item[1]:
                    button["grid"] = grid
                    break
