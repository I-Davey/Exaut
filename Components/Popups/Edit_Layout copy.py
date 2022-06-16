from asyncore import read
import enum
from tkinter.tix import Tree
from PyQt6 import QtGui, QtCore
from loguru import logger
#import QVBoxLayout
from functools import partial
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout,  QScrollArea, QTabWidget, QComboBox, QLabel, QPushButton, QDialog,  QMessageBox, QFormLayout, QVBoxLayout, QLayout
from PyQt6 import QtWidgets
import math
import random


class DragButton(QPushButton):
    def __init__(self, parent, button_layout, update_function):
        super(DragButton, self).__init__(parent)
        self.setAcceptDrops(True)
        self.parent_ = parent
        self.update_function = update_function
        self.notparent = True
        self.button_layout = button_layout
        #set position of button to be the same as the fake button
    def fake_init(self, parent_, bname):
        self.parent_ = parent_
        self.bname = bname

    #on click


    def mousePressEvent(self, event):
        if self.notparent:
            cursize = self.size()
            curpos = self.pos()

            self.button_layout.setParent(None)
            self.parent_.layout().addWidget(self)
            self.notparent = False
            self.move(curpos)


        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.__mousePressPos = event.globalPosition().toPoint()
            self.__mouseMovePos = event.globalPosition().toPoint()

        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        #if self.parent is not self.parent_

        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            # adjust offset from clicked point to origin of widget
            self.show()
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPosition().toPoint()
            self.raise_()
            diff = globalPos - self.__mouseMovePos

            newPos = self.mapFromGlobal(currPos + diff)
            #logger.trace(f"{newPos.x()}, {newPos.y()}, {self.parent_.height()}")


            self.__mouseMovePos = globalPos
            self.move(newPos)


        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
         
            moved = event.globalPosition().toPoint() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()

        self.update_function()
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


class Edit_Layout(QDialog):
    def __init__(self, parent_):
        super(Edit_Layout, self).__init__(parent_)
        self.tablist = []
        self.tab_buttons = {}

        self.SM_Tabs = QtWidgets.QTabWidget()
        self.cur_layout = QFormLayout()
        self.setLayout(self.cur_layout)

        #add widget
        self.SM_Tabs.setObjectName("SM_Tabs")
        self.SM_Tabs.setMovable(True)
        self.SM_Tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.SM_Tabs.setDocumentMode(True)


        self.curtab = parent_.SM_Tabs.currentIndex()
        self.title = parent_.title
        self.tablist = parent_.tablist
        self.tab_buttons = parent_.tab_buttons


        self.rightplusbutton = QPushButton()
        self.rightplusbutton.setObjectName("rightplusbutton")
        self.rightplusbutton.setText("+")
        self.rightplusbutton.setFixedSize(20, 20)
        self.rightplusbutton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rightplusbutton.clicked.connect(self.add_grid_x)
        #rightminusbutton
        self.rightminusbutton = QPushButton()
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
        
        self.items_grid_centre = QGridLayout()
        self.items_grid_centre.setSpacing(0)
        self.items_grid_centre.setContentsMargins(0, 0, 0, 0)
        self.items_grid_centre.setObjectName("x_items_grid_centre")

        self.items_grid_centre.addWidget(self.SM_Tabs, 0, 0, 1, 1)
        self.items_grid_centre.addLayout(self.x_items_grid, 0, 1, 1, 1)

        self.cur_layout.addRow(self.items_grid_centre)

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

        self.cur_layout.addRow(tgrid)   


        self.buttons_array = []

                
        for h in reversed(range(0,self.SM_Tabs.count())):
            self.SM_Tabs.removeTab(h)
          


        #if self.edit_layout and layout_mode == False:
            #self.edit_layout.resetlayout(initial=True)
        self.handle_refresh()


    def handle_refresh(self):

        self.button_to_fake_array = []
        for i, item in enumerate(self.tablist):
            #self.SM_Tabs.addTab(item, item.title)
            #self.SM_Tabs.setTabText(i, item.title)
            tab_data = self.tab_buttons[item]
            columns = tab_data["grid"]
            buttons = tab_data["buttons"] #[button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc]
            tab_grid = QGridLayout()
            
            #grid_map = grid of size columns
            grid_map =  [*([] for i in range(columns))] #[item, *([] for i in range(columns))]
            for button in buttons:
                column_num = button[2]
                if column_num > len(grid_map) -  1:
                    column_num = len(grid_map) - 1
                elif column_num < 0:
                    column_num = 0
                grid_map[column_num].append(button[1])

            grid_of_scrollareas = []
            for i, column  in enumerate(grid_map):
                scrollarea = QScrollArea()
                scrollarea.setWidgetResizable(True)
                ScrollAreaContents = QtWidgets.QWidget()
                if i == 0:
                    ScrollAreaContents.setStyleSheet("background-color: rgb(90, 90, 90);")
                #set scrollareacontents color to red
                #ScrollAreaContents.setStyleSheet("background-color: rgb(255, 0, 0);")
                ScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 248, 174))
                scrollarea.setWidget(ScrollAreaContents)
                ScrollGrid = QVBoxLayout(ScrollAreaContents)
                ScrollGrid.setSpacing(0)
                ScrollGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

                for button in column:
                    button_layout = QVBoxLayout()

                    new_button = DragButton(self,button_layout, self.update_layout)
                    button_layout.addWidget(new_button)

                    new_button.setText(button)
                    new_button.isVisible = True

                    ScrollGrid.addLayout(button_layout)


                    #new_button.setStyleSheet("background-color: rgb(255, 255, 255);")
                    if i == 0:
                        new_button.setStyleSheet("background-color: rgb(255, 255, 255);")
                tab_grid.addWidget(scrollarea, 0, i)
            
            tab_widget = QTabWidget()
            tab_widget.setLayout(tab_grid)
            
            self.SM_Tabs.addTab(tab_widget, item)
                    



        if self.curtab<0 or self.curtab > self.SM_Tabs.count()-1:
            self.SM_Tabs.setCurrentIndex(0)
        else:
            self.SM_Tabs.setCurrentIndex(self.curtab)

        


    def add_grid_x(self):
        None
    def remove_grid_x(self):
        None
    def handle_update(self):
        None
    def save_layout(self):
        None




    def update_layout(self):
        curtab_items = []
        for item in self.buttons_array:
            if item[0] in (None, ""):
                item[0] = 0
            row = item[0]
            tab_text = item[1]
            x_coord = item[2].pos().x()
            y_coord = item[2].pos().y()
            #if tab is curtab
            if self.SM_Tabs.tabText(self.SM_Tabs.currentIndex()) == tab_text:
                curtab_items.append([row, x_coord, y_coord])

        #change row of curtab items based on x_coord
        for item in curtab_items:
            for i in range(len(curtab_items)):
                if curtab_items[i][1] > item[1]:
                    curtab_items[i][0] += 1


        
            
            
            
