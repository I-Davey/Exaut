from PyQt6 import QtGui, QtCore
#import QVBoxLayout
from functools import partial
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout,  QScrollArea, QTabWidget, QPushButton, QWidget,  QFormLayout, QVBoxLayout, QMainWindow
from PyQt6.QtGui import QDrag, QPixmap, QAction
from PyQt6.QtCore import QMimeData, Qt

from PyQt6 import QtWidgets

class CustomDropLayout(QWidget):
    def __init__(self, parent, update_function, button_layout, tab, column):
        super(CustomDropLayout, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAcceptDrops(True)
        self.update_function = update_function
        self.button_layout = button_layout
        self.tab = tab
        self.column = column
        self.button_array = []
    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        widget = event.source()
        position = event.position()
        if widget is not None:
            widget.setParent(None)
            self.button_layout.addWidget(widget)
            self.update_function(self.tab, self.column,position, widget.from_column, widget.text(), self.button_array)

        
class DragButton(QPushButton):
    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)


            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(e.pos())

            drag.exec(Qt.DropAction.MoveAction)

class QTabWidgetHandler(QTabWidget):
    def fake_init(self, parent_):
        self.parent_ = parent_
    

class Edit_Layout(QMainWindow):
    signal_save = QtCore.pyqtSignal(dict)

    def __init__(self, parent_):
        super(Edit_Layout, self).__init__(parent_)
        self.updating = False
        self.refreshing = False
        self.tablist = []
        self.tab_buttons = {}
        self.static = False
        self.start = True
        self.SM_Tabs = QtWidgets.QTabWidget()
        centralwdgt = QtWidgets.QWidget(self)
        self.cur_layout = QFormLayout(centralwdgt)
        self.setCentralWidget(centralwdgt)

        #add a menu bar
        self.menubar = self.menuBar()
        self.filemenu = self.menubar.addAction("Refresh")
        self.filemenu.triggered.connect(self.refresh_data)
        self.static_action = QAction(self, checkable=True)
        self.static_action.setText("Static (off)")
        self.menubar.addAction(self.static_action)
        self.static_action.triggered.connect(self.handle_static)

        #add widget
        self.SM_Tabs.setObjectName("SM_Tabs")
        self.SM_Tabs.setMovable(True)
        self.SM_Tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.SM_Tabs.setDocumentMode(True)

        self.parent_ = parent_
        self.curtabtext = parent_.SM_Tabs.tabText(parent_.SM_Tabs.currentIndex())
        self.curtab = None
        self.curtabindex = 0
        self.title = parent_.title
        self.tablist = parent_.tablist
        self.tab_buttons = parent_.tab_buttons
        self.refresh = parent_.refresh
        self.pointer = parent_.edit_layout


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
        self.x_items_grid.setContentsMargins(0, 0, 0, 0)
        self.x_items_grid.setObjectName("y_items_grid")

        self.y_items_grid = QGridLayout()
        self.y_items_grid.setContentsMargins(0, 0, 0, 0)
        self.y_items_grid.setObjectName("y_items_grid")
        
        self.items_grid_centre = QGridLayout()
        self.items_grid_centre.setContentsMargins(0, 0, 0, 0)
        self.items_grid_centre.setObjectName("x_items_grid_centre")

        self.items_grid_centre.addWidget(self.SM_Tabs, 0, 0, 1, 1)
        self.items_grid_centre.addLayout(self.x_items_grid, 0, 1, 1, 1)

        self.cur_layout.addRow(self.items_grid_centre)

        self.setWindowTitle("Edit Layout")
        #add save button
        self.save_button = QPushButton("Update and Exit")
        self.save_button.clicked.connect(partial(self.handle_save, exit_=True))
        self.update_button = QPushButton("Update")
        #lambda run self.parent_.Refresh()
        self.update_button.clicked.connect(self.handle_save)
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
          

        self.SM_Tabs.currentChanged.connect(self.ontabchange)

        #if self.edit_layout and layout_mode == False:
            #self.edit_layout.resetlayout(initial=True)
        self.handle_refresh(self.curtab)
        self.start = False

    def handle_static(self):
        self.static = not self.static
        if self.static:
            self.static_action.setText("Static (on)")
        else:
            self.static_action.setText("Static (off)")



    def clear_all(self):
        for i in reversed(range(0,self.SM_Tabs.count())):
            self.SM_Tabs.removeTab(i)
        
    #on close handler
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.parent_.edit_layout = None
        self.pointer = None
        return super().closeEvent(a0)

    def handle_save(self, exit_=False):
        tab_order = []
        for i in range(0, self.SM_Tabs.count()):
            #append text of tabs in order
            tab_order.append(self.SM_Tabs.tabText(i))

        print(tab_order)

        for i in range(0, len(tab_order)):
            self.tab_buttons[tab_order[i]]["tabsequence"] = i + 1

        self.signal_save.emit(self.tab_buttons)
        self.refresh()
        if exit_:
            self.pointer = None
            self.deleteLater()
            self.close()

    def refresh_data(self):
        self.refreshing = True
        curtab = self.SM_Tabs.currentIndex()

        self.title = self.parent_.title
        self.tablist = self.parent_.tablist
        self.tab_buttons = self.parent_.tab_buttons
        self.refresh = self.parent_.refresh
        self.pointer = self.parent_.edit_layout
        self.handle_refresh(self.curtab)
        self.SM_Tabs.setCurrentIndex(curtab)
        self.SM_Tabs.currentChanged.connect(self.ontabchange)
        self.refreshing = False

    def handle_refresh(self, curtab = None):
        
        self.clear_all()
        self.button_to_fake_array = []
        for i, item in enumerate(self.tablist):
            #self.SM_Tabs.addTab(item, item.title)
            #self.SM_Tabs.setTabText(i, item.title)
            tab_data = self.tab_buttons[item]
            if tab_data["grid"] in ("", None):
                tab_data["grid"] = 1
            columns = tab_data["grid"]
            buttons = tab_data["buttons"] #[button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc]
            tab_grid = QGridLayout()
            
            #grid_map = grid of size columns
            grid_map =  [*([] for i in range(columns + 1))] #[item, *([] for i in range(columns))]

            for button in buttons:
                column_num = button[2]
                if not column_num:
                    column_num = 0
                if column_num > len(grid_map) -  1:
                    column_num = len(grid_map) - 1
                elif column_num < 0:
                    column_num = 0
                grid_map[column_num].append(button[1])

            grid_of_scrollareas = []
            for i, column  in enumerate(grid_map):
                scrollarea = QScrollArea()
                scrollarea.setWidgetResizable(True)
                ScrollAreaContents = CustomDropLayout(self, self.update_column, None, item, i)
                ScrollAreaContents.setObjectName("ScrollAreaContents")
                if i == 0:
                    ScrollAreaContents.setStyleSheet("background-color: rgb(90, 90, 90);")
                #set scrollareacontents color to red
                #ScrollAreaContents.setStyleSheet("background-color: rgb(255, 0, 0);")
                ScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 248, 174))
                scrollarea.setWidget(ScrollAreaContents)
                ScrollGrid = QVBoxLayout(ScrollAreaContents)
                ScrollGrid.setObjectName("ScrollGrid")
                ScrollGrid.setSpacing(0)
                ScrollGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                
                if len(column) == 0:
                    button_layout = QVBoxLayout()
                    ScrollGrid.addLayout(QVBoxLayout())
                    ScrollAreaContents.button_layout = button_layout

                for button in column:
                    button_layout = QVBoxLayout()
                    button_layout.setContentsMargins(0, 3, 0, 3 )
                    #set spacing between elements in qvboxlayout
                    ScrollAreaContents.button_layout = button_layout

        
                    new_button = DragButton(button)
                    color_default = QtGui.QColor(225, 225, 225)
                    color_border = QtGui.QColor(160, 160, 160)
                    new_button.setStyleSheet(f"""QPushButton{{
                            border-style: solid;
                            background-color: {color_default.name()};
                            border-width: 1px 1px 1px 1px;
                            border-radius: 2px;
                            border-color: {color_border.name()};
                            padding: 4px;
                            }}
                            """)
                    new_button.setContentsMargins(0, 3, 0, 3)
                    new_button.from_column = i
                    
                    button_layout.addWidget(new_button)

                    new_button.setText(button)
                    new_button.isVisible = True


                    ScrollGrid.addLayout(button_layout)
                    ScrollAreaContents.button_array.append(new_button)


                    #new_button.setStyleSheet("background-color: rgb(255, 255, 255);")
                    if i == 0:
                        new_button.setStyleSheet("""background-color: red;
                        border-style: outset;
                        border-width: 2px;
                        border-radius: 15px;
                        border-color: black;
                        padding: 4px;""")
                tab_grid.addWidget(scrollarea, 0, i)
            
            tab_widget = QTabWidget()
            tab_widget.setLayout(tab_grid)
            
            self.SM_Tabs.addTab(tab_widget, item)

        if not curtab:
            for i in range(0, self.SM_Tabs.count()):
                if self.SM_Tabs.tabText(i) == self.curtabtext:
                    self.SM_Tabs.setCurrentIndex(i)
                    self.curtabindex = i
                    
                    break
        else:
            #find the index of the tabtext
            self.SM_Tabs.setCurrentIndex(curtab)
            self.curtabindex = curtab
        
    def ontabchange(self, index):
        if not self.start:
            self.curtabtext = self.SM_Tabs.tabText(index)
        if self.refreshing:
            return

                #get curtabdata for current tab using curtabindex
        curtabdata = self.tab_buttons[self.tablist[index]]
        curtabsize = curtabdata["tabsize"]
        if self.updating or self.static:
            return
        if curtabsize:
            curtabsize = curtabsize.split(",")
            self.resize(int(int(curtabsize[0])*1.3), int(int(curtabsize[1])*1.2))
        else:
            self.resize(650,300)
        
    def add_grid_x(self):
        self.updating = True
        curtab = self.SM_Tabs.currentIndex()
        curtabtext = self.SM_Tabs.tabText(curtab)
        self.tab_buttons[curtabtext]["grid"] += 1
        self.handle_refresh(curtab)
        self.updating = False

    def remove_grid_x(self):
        self.updating = True
        curtab = self.SM_Tabs.currentIndex()
        curtabtext = self.SM_Tabs.tabText(curtab)
        if not self.tab_buttons[curtabtext]["grid"]:
            self.tab_buttons[curtabtext]["grid"] = 1
        if self.tab_buttons[curtabtext]["grid"] > 1:
            self.tab_buttons[curtabtext]["grid"] -= 1
            self.handle_refresh(curtab)
        self.updating = False

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
                if not curtab_items[i][1]:
                    curtab_items[i][1] = 0
                if curtab_items[i][1] > item[1]:
                    curtab_items[i][0] += 1
            
    def change_tab(self, tab_name:str):
        for i in range(self.SM_Tabs.count()):
            if self.SM_Tabs.tabText(i) == tab_name:
                self.SM_Tabs.setCurrentIndex(i)
                self.curtabindex = i
                break
    
    def update_column(self, tab_name, column_num, pos, from_column, text, button_array):
        current_tab_text = self.SM_Tabs.tabText(self.SM_Tabs.currentIndex())
        position_array = []
        current_item_desc = ""
        other_items_desc = []
        tab_data = self.tab_buttons[current_tab_text]
        for button in button_array:
            globaly = self.mapToGlobal(button.pos()).y()
            #get height of button
            height = int(button.height() / 2)
            y = globaly + height
            position_array.append([button.text(), y])

        for i,j in enumerate(position_array):
            if position_array[i][0] == text:
                #delete item from position_array
                position_array.pop(i)



        final_item_array = []

        tab_dict = self.tab_buttons[tab_name]  #[button.buttonsequence, button.buttonname, button.columnnum, button.buttondesc]
        for i, item in enumerate(tab_dict["buttons"]):
            if item[1] == text:
                current_item_desc = item[3]
                tab_dict["buttons"].pop(i)
                break

        
        #delete all tab_dict["buttons"] as i with i[2] == column_num
        for i in reversed(range(len(tab_dict["buttons"]))):
            if tab_dict["buttons"][i][2] == column_num:
                other_items_desc.append(tab_dict["buttons"][i][1])
                tab_dict["buttons"].pop(i)
        other_items_desc.reverse()
        
        final_item_array.append([self.mapToGlobal(pos).y(), text, column_num, current_item_desc])
        for i, item_desc in enumerate(other_items_desc):
            final_item_array.append([position_array[i][1], position_array[i][0], column_num, item_desc])
        
        final_item_array.sort(key=lambda x: x[0])
        for i, item in enumerate(final_item_array):
            final_item_array[i][0] = i
        tab_dict["buttons"].extend(final_item_array)
        print(tab_dict["buttons"])
        self.handle_refresh(curtab = self.SM_Tabs.currentIndex() )

