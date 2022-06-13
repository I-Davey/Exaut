from asyncore import read
import enum
from tkinter.tix import Tree
from PyQt6 import QtGui, QtCore
from loguru import logger
#import QVBoxLayout
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout,  QScrollArea, QTabWidget, QComboBox, QLabel, QPushButton, QDialog,  QMessageBox, QFormLayout

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
            #logger.trace(f"{newPos.x()}, {newPos.y()}, {self.parent_.height()}")
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

class QTabWidgetHandler(QTabWidget):
    def fake_init(self, parent_):
        self.parent_ = parent_
    
class DragButton_XY(QPushButton):
    def fake_init(self, parent_, bname):
        self.parent_ = parent_
        self.bname = bname

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.__mousePressPos = event.globalPosition().toPoint()
            self.__mouseMovePos = event.globalPosition().toPoint()
    
        super(DragButton_XY, self).mousePressEvent(event)

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
            #logger.debug(f"{newPos.x()}, {newPos.y()}, {self.parent_.width()} : {self.parent_.height()}, {self.width()} : {self.height()}")
            """
            if newPos.x() < 1:
                #logger.warning("X")
                newPos.setX(1)
                
                #            if newPos.x() > self.parent_.width() -  width of button
            if newPos.x() > self.parent_.width()  - int(self.parent_.width()- 21):
                #logger.warning("WIDTH")
                newPos.setX(self.parent_.width() - int(self.parent_.width() - 21))
            if newPos.y() < 2:
                #logger.warning("Y")
                newPos.setY(2)
            if newPos.y() > self.parent_.height() - 140:
                #logger.warning("HEIGHT")
                newPos.setY(self.parent_.height() - 140)
            """
            self.__mouseMovePos = globalPos
            self.move(newPos)
            #move self.tab_data_dict[item]["buttons"][x1]["rightarrow"] = rightarrowbutton
            for item in self.parent_.tab_data_dict:
                for item2 in self.parent_.tab_data_dict[item]["buttons"]:
                    if item2["buttonmain"] == self:
                        item2["rightarrow"].move(newPos.x()+self.width(), newPos.y())
                        item2["leftarrow"].move(newPos.x()-20, newPos.y())



        super(DragButton_XY, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            buttons = []
            main_button_x = self.x()
            for i, item in enumerate(self.parent_.tab_data_dict):
                for item2 in self.parent_.tab_data_dict[item]["buttons"]:
                    if item2["buttonmain"] == self:
                        for item2 in self.parent_.tab_data_dict[item]["buttons"]:
                            #if x() is the same
                            #log x coords
                            #logger.debug(f"{item2['buttonmain'].y()}")
                            if item2["buttonmain"].parent() == self.parent():
                                #also append tab its in
                                buttons.append([item2['buttonmain'].y(), item2, self.parent_.tab_data_dict[item]["tab"]] )
            buttons.sort(key=lambda x: x[0])
            #reorder self.parent_.tab_names by order of buttons
            self.parent_.change_order(buttons)
            moved = event.globalPosition().toPoint() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
        super(DragButton_XY, self).mouseReleaseEvent(event)

class QPushButtonHandler(QPushButton):
    def fake_init(self, parent_, left):
        self.parent_ = parent_
        self.left = left
    #handle click
    def mousePressEvent(self, event):
        if self.left:
            self.parent_.leftbutton(self)
        else:
            self.parent_.rightbutton(self)
        super(QPushButtonHandler, self).mousePressEvent(event)

class Edit_Layout(QDialog):
    def __init__(self, parent_):
        self.curtab = parent_.SM_Tabs.currentIndex()

        super(Edit_Layout, self).__init__(parent_)
        self.parent_ = parent_
        self.title = self.parent_.title
        self.ReadSQL = self.parent_.ReadSQL
        self.WriteSQL = self.parent_.WriteSQL
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.SM_Tabs = QTabWidgetHandler(self.centralwidget)
        self.SM_Tabs.fake_init(self)
        self.SM_Tabs.setMovable(True)
        self.SM_Tabs.setObjectName("SM_Tabs")
        #rightplusbutton
        self.rightplusbutton = QPushButton(self.centralwidget)
        self.rightplusbutton.setObjectName("rightplusbutton")
        self.rightplusbutton.setText("+")
        self.rightplusbutton.setFixedSize(20, 20)
        self.rightplusbutton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rightplusbutton.clicked.connect(self.add_grid_x)
        #rightminusbutton
        self.rightminusbutton = QPushButton(self.centralwidget)
        self.rightminusbutton.setObjectName("rightminusbutton")
        self.rightminusbutton.setText("-")
        self.rightminusbutton.setFixedSize(20, 20)
        self.rightminusbutton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rightminusbutton.clicked.connect(self.remove_grid_x)

      

        self.x_items_grid = QGridLayout()
        self.x_items_grid.setSpacing(0)
        self.x_items_grid.setContentsMargins(0, 0, 0, 0)
        self.x_items_grid.setObjectName("y_items_grid")

        self.y_items_grid = QGridLayout()
        self.y_items_grid.setSpacing(0)
        self.y_items_grid.setContentsMargins(0, 0, 0, 0)
        self.y_items_grid.setObjectName("y_items_grid")
        #self.y_items_grid.addWidget(self.belowplusbutton, 0, 0, 0, 0)
        #self.y_items_grid.addWidget(self.belowminusbutton, 0, 1, 5,0 )
        #place right next to eachother



        #CENTRE X ITEMS GRID
        self.items_grid_centre = QGridLayout()
        self.items_grid_centre.setSpacing(0)
        self.items_grid_centre.setContentsMargins(0, 0, 0, 0)
        self.items_grid_centre.setObjectName("x_items_grid_centre")

        self.items_grid_centre.addWidget(self.SM_Tabs, 0, 0, 1, 1)
        self.items_grid_centre.addLayout(self.x_items_grid, 0, 1, 1, 1)

        #MAIN GRID

        self.layout.addRow(self.items_grid_centre)

        #f"sexect tab, tabsequence, grid from tabs where title = '{self.title}'"
        self.tab_data = self.ReadSQL(f"select tab, tabsequence, grid from tabs where formname = '{self.title}' order by tabsequence")
        #logger.debug(self.tab_data)
        self.tab_names = []
        self.tab_data_dict = {}
        for item in self.tab_data:
            self.tab_names.append(item[0])
        self.resetlayout()
        self.setWindowTitle("Edit Layout")
        #add save button
        self.save_button = QPushButton("Update and Exit")
        self.save_button.clicked.connect(self.save_layout)
        self.update_button = QPushButton("Update")
        #lambda run self.parent_.Refresh()
        self.update_button.clicked.connect(self.handle_update)
        #grid
        tgrid = QGridLayout()
        tgrid.setSpacing(0)
        tgrid.setContentsMargins(0, 0, 0, 0)
        tgrid.setObjectName("tgrid")
        tgrid.addWidget(self.update_button,     0, 0, 0, 1)
        tgrid.addWidget(self.rightplusbutton,   0, 1, 1, 1)
        tgrid.addWidget(self.rightminusbutton,  0, 2, 1, 1)
        tgrid.addWidget(self.save_button,       0, 3, 2, 1)

        self.layout.addRow(tgrid)   

    def handle_update(self):
        self.handle_tab_layout()
        self.parent_.Refresh(layout_Mode=True)
        #enumerate
    def change_order(self, buttons):
        #logger.debug(buttons)
        cur_seq = 1
        for i, button in enumerate(buttons):
            #update button set buttonsequence  where formname, tab, buttonname
            self.WriteSQL(f"update buttons set buttonsequence = {cur_seq} where formname = '{self.title}' and tab = '{button[2]}' and buttonname = '{button[1]['buttonname']}'")
            cur_seq += 1
        self.resetlayout(self.SM_Tabs.currentIndex())


    def save_layout(self):
        self.handle_tab_layout()
        #refresh
        self.parent_.Refresh(layout_Mode=True)
        self.close()
    def add_grid_x(self):
        #get current tab obj
        #find current_tab object in tab_data_dict
        curtab = self.SM_Tabs.currentWidget()
        for item in self.tab_data:  
            if item[3] == curtab:
                if item[2] == None:
                    item[2] = 2
                else:
                    item[2] += 1
                self.resetlayout(self.SM_Tabs.currentIndex())
                break
        #updaten database
        self.WriteSQL(f"update tabs set grid = {item[2]} where formname = '{self.title}' and tab = '{item[0]}'")



        #logger.debug("add_x")

    def remove_grid_x(self):
        #logger.debug("remove_x")
        curtab = self.SM_Tabs.currentWidget()
        for item in self.tab_data:
            if item[3] == curtab:
                if item[2] == None:
                    item[2] = 2
                else:
                    item[2] -= 1
                self.resetlayout(self.SM_Tabs.currentIndex())
                break
        #updaten database
        self.WriteSQL(f"update tabs set grid = {item[2]} where formname = '{self.title}' and tab = '{item[0]}'")

    def handle_tab_layout(self):    
        orig_dict = self.tab_data_dict
        self.tab_names = []
        for i in range(self.SM_Tabs.count()):
            for item in orig_dict:  
                if orig_dict[item]["tab_obj"] == self.SM_Tabs.widget(i):
                    #logger.debug(f"{item}")
                    #change self.tab_names to reflect new tab order
                    self.tab_names.append(item)

                    break
        for i, item in enumerate(self.tab_names):
            self.WriteSQL(f"update tabs set tabsequence = {i+1} where formname = '{self.title}' and tab = '{item}'")
                 #tab_data_dict
    def leftbutton(self, object_):

        for item in self.tab_data_dict:
                for item2 in self.tab_data_dict[item]["buttons"]:
                    if item2["leftarrow"] == object_:
                        tab = self.tab_data_dict[item]["tab"]
                        formname = self.title
                        buttonname = item2["buttonname"]
                        columnum = item2["columnnum"] if item2["columnnum"] not in ( None, 0) else 1
                        if columnum == 1:
                            columnum = 2
                        #update button set columnum = columnum - 1
                        self.ReadSQL(f"update buttons set columnnum = {columnum - 1} where formname = '{formname}' and tab = '{tab}' and buttonname = '{buttonname}'")
                        #logger.debug(f"{buttonname} columnum is {columnum - 1}")

                        self.resetlayout(self.SM_Tabs.currentIndex())
                        object_.setEnabled(False)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        try:
            self.parent_.edit_layout = None
        except:
            pass
        return super().closeEvent(a0)

    def rightbutton(self, object_):
        #logger.debug(f"{object_.objectName()}, {object_.text()}")
        for item in self.tab_data_dict:
                for item2 in self.tab_data_dict[item]["buttons"]:

                    if item2["rightarrow"] == object_:
                        tab = self.tab_data_dict[item]["tab"]
                        formname = self.title
                        buttonname = item2["buttonname"]
                        columnum = item2["columnnum"] if item2["columnnum"] not in (None, 0) else 1

                        #update button set columnum = columnum + 1
                        self.ReadSQL(f"update buttons set columnnum = {columnum + 1} where formname = '{formname}' and tab = '{tab}' and buttonname = '{buttonname}'")
                        #logger.debug(f"{buttonname} columnum is {columnum + 1}")
                        self.resetlayout(self.SM_Tabs.currentIndex())
                        #disable object_
                        object_.setEnabled(False)
    def resetlayout(self, tab_index = None, initial = False):
        
        #update buttons set columnum 0 where columnum null
        #self.parent_.Refresh()

        self.WriteSQL(f"update buttons set columnnum = 0 where columnnum is null and formname = '{self.title}'")
        if initial:
            self.parent_.Refresh(layout_Mode=True)


        self.SM_Tabs.clear()
        self.tab_data_dict = {}
        for item in self.tab_data:
            while len(item) > 3:
                #remove last item from tab_data
                item.pop()

        for i, item in enumerate(self.tab_names):
            #f"Select butonnname, buttonsequence, columnum from buttons where tab = '{item}' and formname = 'formname' order by buttonsequence"
            buttondata = self.ReadSQL(f"Select buttonname, buttonsequence, columnnum from buttons where tab = '{item}' and formname = '{self.title}' order by buttonsequence")
            buttondata_arr = []
            null_buttondata = []
            for button in buttondata:
                dict_info = {"buttonname": button[0], "buttonsequence": button[1], "columnnum": button[2]}

                buttondata_arr.append(dict_info)
            for itemxox in null_buttondata:
                buttondata_arr.append(itemxox)
            #convert buttondata from array to dict
            self.tab_data_dict[item] = {"tab":self.tab_data[i][0], "tabsequence":self.tab_data[i][1], "grid":self.tab_data[i][2], "buttons":buttondata_arr, "tab_obj":None}
        for i, item in enumerate(self.tab_data_dict):
            self.maingrid = QGridLayout()
            startwidget = QWidget()
            startwidget.setLayout(self.maingrid)
            self.tab_data[i].append(startwidget)    

            if self.tab_data_dict[item]["grid"] == None:
                self.tab_data_dict[item]["grid"] = 1
            if self.tab_data_dict[item]["grid"] in (None, ""):
                self.tab_data_dict[item]["grid"] = 1
            for x in range(1, int(self.tab_data_dict[item]["grid"] + 1)):
                self.tab = QWidget()
                self.tab.setLayout  
                self.tab.setObjectName(f"Tab_{i}")
                self.tab_data_dict[item]["tab_obj"] = startwidget
                self.TabGrid = QGridLayout(self.tab)
                self.TabGrid.setObjectName(f"TabGrid_{i}")
                self.SM_ScrollArea = QScrollArea()
                self.SM_ScrollArea.setWidgetResizable(True)
                self.SM_ScrollArea.setObjectName(f"SM_ScrollArea_{i}_{x-1}")
                #cha
                self.SM_ScrollAreaContents = QWidget()
                self.SM_ScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 248, 174))
                self.SM_ScrollAreaContents.setObjectName(f"SM_ScrollAreaContents_{i}_{x-1}")
                self.SM_ScrollGrid = QGridLayout(self.SM_ScrollAreaContents)
                self.SM_ScrollGrid.setObjectName(f"SM_ScrollGrid_{i}_{x-1}")
                #align grid to top

                
                self.SM_Grid =  QGridLayout()
                self.SM_Grid.setObjectName(f"SM_Grid_{i}_{x-1}")
                self.SM_Grid.setRowStretch(1000, 3)


                for x1, button in enumerate(self.tab_data_dict[item]["buttons"]):
                    bname = button["buttonname"]
                    bcolumn = button["columnnum"] if button["columnnum"] else 0
                    if bcolumn > self.tab_data_dict[item]["grid"]:
                        bcolumn = self.tab_data_dict[item]["grid"]
                    if x == 0:
                        x = 1
                    if bcolumn == 0:
                        bcolumn = 1
                    if bcolumn != x:
                        continue
                    widget = DragButton_XY(self)
                    widget.fake_init(self, bname)
                    widget.setObjectName(f"{bname}")
                    widget.setText(bname)
                    leftarrowbutton = QPushButtonHandler()
                    leftarrowbutton.fake_init(self, True)
                    leftarrowbutton.setText("<")
                    leftarrowbutton.setFixedSize(20, 20)
                    leftarrowbutton.setObjectName(f"leftarrow_{item}_{x}_{x1}")


                    rightarrowbutton = QPushButtonHandler()
                    rightarrowbutton.fake_init(self, False)

                    rightarrowbutton.setText(">")
                    #make rightarrowbutton small
                    rightarrowbutton.setFixedSize(20, 20)
                    rightarrowbutton.setObjectName(f"rightarrow_{item}_{x}_{x1}")

                    #connect

                    newgrid = QGridLayout()
                    newgrid.addWidget(leftarrowbutton, 0, 0)
                    newgrid.addWidget(rightarrowbutton, 0, 2)
                    newgrid.addWidget(widget, 0, 1)
                    self.SM_Grid.addLayout(newgrid, x1, bcolumn)
                    self.tab_data_dict[item]["buttons"][x1]["buttonmain"] = widget
                    self.tab_data_dict[item]["buttons"][x1]["leftarrow"] = leftarrowbutton
                    self.tab_data_dict[item]["buttons"][x1]["rightarrow"] = rightarrowbutton



                self.SM_ScrollGrid.addLayout(self.SM_Grid, 0, 0, 1, 1)
                self.SM_ScrollArea.setWidget(self.SM_ScrollAreaContents)
                self.TabGrid.addWidget(self.SM_ScrollArea, 0, x, 1, 1)
                self.maingrid.addWidget(self.tab, 0, x, 1, 1)

            self.SM_Tabs.addTab(startwidget, item)
            self.SM_Tabs.setTabText(self.SM_Tabs.indexOf(self.tab), item)
        if tab_index != None:
            self.SM_Tabs.setCurrentIndex(tab_index)
        else:
            self.SM_Tabs.setCurrentIndex(self.curtab)
        

