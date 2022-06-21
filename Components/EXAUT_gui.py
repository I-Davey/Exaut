
from PyQt6 import QtCore,QtGui,QtWidgets
from PyQt6.QtCore import QPoint, Qt

from PyQt6.QtWidgets import *
from PyQt6 import QtGui



class Ui_EXAUT_GUI():
    def setupUi(self, EXAUT_GUI):




        EXAUT_GUI.setObjectName("EXAUT_GUI")
        EXAUT_GUI.resize(650, 300)
        self.titlebar  = QVBoxLayout()
        self.titlebar.addWidget(MyBar(EXAUT_GUI))
        self.titlebar.setContentsMargins(0,0,0,0)
        self.titlebar.addStretch(-1)
        self.pressing = False
        #EXAUT_GUI.setMenuWidget(MyBar(self))


        #emove all padding centralwidget




        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.Main_ScrollArea = QtWidgets.QScrollArea(self.tab)
        self.Main_ScrollArea.setWidgetResizable(True)
        self.Main_ScrollArea.setObjectName("Main_ScrollArea")



        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)


        font = QtGui.QFont()
        font.setPointSize(12)




        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)

        self.Main_HorLay_InsDel = QtWidgets.QHBoxLayout()
        self.Main_HorLay_InsDel.setObjectName("Main_HorLay_InsDel")



        self.gridLayout_2.addWidget(self.Main_ScrollArea, 0, 0, 1, 1)



        self.Tab1_Grid = QtWidgets.QGridLayout()
        self.Tab1_Grid.setObjectName("Tab1_Grid")


        self.menubar = QtWidgets.QMenuBar(EXAUT_GUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 650, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuEdit_form = QtWidgets.QMenu(self.menubar)
        self.menuEdit_form.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        EXAUT_GUI.setMenuBar(self.menubar)
        #place menubar below the title bar
        #self.menubar.setNativeMenuBar(False)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 650, 26))
        self.menubar.setCornerWidget(QtWidgets.QWidget(self.menubar), QtCore.Qt.Corner.TopRightCorner)

        self.actionImport_from_Excel = QtGui.QAction(EXAUT_GUI)
        self.actionImport_from_Excel.setObjectName("actionImport_from_Excel")
        self.actionExport_to_Excel = QtGui.QAction(EXAUT_GUI)
        self.actionExport_to_Excel.setObjectName("actionExport_to_Excel")
        self.actionRefresh = QtGui.QAction(EXAUT_GUI)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionTabsize = QtGui.QAction(EXAUT_GUI)
        self.actionTabsize.setObjectName("actionTabsize")
        self.actionstaticsize = QtGui.QAction(EXAUT_GUI)
        self.actionOpen_Files_Explorer = QtGui.QAction(EXAUT_GUI)
        self.actionOpen_Files_Explorer.setObjectName("actionOpen_Files_Explorer")


        self.actionAdd_exe = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_exe.setObjectName("actionAdd_exe")

        self.actionAdd_tabto = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_tabto.setObjectName("actionAdd_tabto")
        self.actionAdd_tablast = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_tablast.setObjectName("actionAdd_tablast")


        self.actionAdd_url = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_url.setObjectName("actionAdd_url")

        self.actionAdd_Folder = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_Folder.setObjectName("actionAdd_Folder")

        self.actionAdd_Seq = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_Seq.setObjectName("actionAdd_Seq")

        self.actionAdd_Proc = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_Proc.setObjectName("actionAdd_Proc")

        self.actionAdd_Desc = QtGui.QAction(EXAUT_GUI)
        self.actionAdd_Desc.setObjectName("actionAdd_Desc")

        self.actionEdit_layout = QtGui.QAction(EXAUT_GUI)
        self.actionEdit_layout.setObjectName("actionEdit_layout")

        self.actionCopy = QtGui.QAction(EXAUT_GUI)
        self.actionCopy.setObjectName("actionCopy")

        self.customimportexport = QtGui.QAction(EXAUT_GUI)
        self.customimportexport.setObjectName("customimportexport")

        self.sht2tbl = QtGui.QAction(EXAUT_GUI)
        self.sht2tbl.setObjectName("sht2tbl")

        self.actionCopy_folder = QtGui.QAction(EXAUT_GUI)
        self.actionCopy_folder.setObjectName("actionCopy_folder")

        self.actionTab = QtGui.QAction(EXAUT_GUI)
        self.actionTab.setObjectName("actionTab")

        self.actionTabUrl = QtGui.QAction(EXAUT_GUI)
        self.actionTabUrl.setObjectName("actionTabUrl")


        self.actionTabFolder = QtGui.QAction(EXAUT_GUI)
        self.actionTabFolder.setObjectName("actionTabFolder")

        self.actionOpenTabUrl = QtGui.QAction(EXAUT_GUI)
        self.actionOpenTabUrl.setObjectName("actionOpenTabUrl")


        self.actionAbout = QtGui.QAction(EXAUT_GUI)
        self.actionAbout.setObjectName("actionAbout")

        self.actionHidden_mode = QtGui.QAction('View Hidden Tabs', EXAUT_GUI, checkable=True)


        self.actionTab_Copy = QtGui.QAction(EXAUT_GUI)
        self.actionTab_Copy.setObjectName("actionTab_Copy")

        self.actionTab_Move = QtGui.QAction(EXAUT_GUI)
        self.actionTab_Move.setObjectName("actionTab_Move")

        self.menuFile.addAction(self.actionOpen_Files_Explorer)
        self.menuFile.addAction(self.actionOpenTabUrl)

        

        self.menuEdit.addAction(self.actionAdd_Seq)
        self.menuEdit.addAction(self.actionAdd_Proc)
        self.menuEdit.addAction(self.actionAdd_Desc)

        self.menuEdit_form.addAction(self.actionEdit_layout)
        self.menuEdit_form.addAction(self.actionHidden_mode)
        self.menuEdit_form.addAction(self.actionTab_Copy)
        self.menuEdit_form.addAction(self.actionTab_Move)
        self.menuEdit_form.addAction(self.actionTab)
        self.menuEdit_form.addAction(self.actionTabUrl)
        self.menuEdit_form.addAction(self.actionTabFolder)
        self.menuEdit_form.addAction(self.actionAdd_tabto)
        self.menuEdit_form.addAction(self.actionAdd_tablast)


        self.menuView.addAction(self.actionRefresh)
        self.menuTools.addAction(self.actionImport_from_Excel)
        self.menuTools.addAction(self.actionExport_to_Excel)
        self.menuTools.addAction(self.customimportexport)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuEdit_form.menuAction())


        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        #add self.actionTabsize to menubar
        self.menubar.addAction(self.actionTabsize)
        self.menubar.addAction(self.actionstaticsize)


        self.retranslateUi(EXAUT_GUI)
        QtCore.QMetaObject.connectSlotsByName(EXAUT_GUI)

    def retranslateUi(self, EXAUT_GUI):
        _translate = QtCore.QCoreApplication.translate
        #set self.titlebar as the first widget
        EXAUT_GUI.setWindowTitle(_translate("EXAUT_GUI", "EXAUT Server Manager"))


        self.menuFile.setTitle(_translate("EXAUT_GUI", "File"))
        self.menuEdit.setTitle(_translate("EXAUT_GUI", "Edit"))
        self.menuEdit_form.setTitle(_translate("EXAUT_GUI","Tab"))
        self.menuView.setTitle(_translate("EXAUT_GUI", "View"))
        self.menuTools.setTitle(_translate("EXAUT_GUI", "Tools"))
        self.menuHelp.setTitle(_translate("EXAUT_GUI", "Help"))
        self.actionImport_from_Excel.setText(_translate("EXAUT_GUI", "Import from Excel"))
        self.actionImport_from_Excel.setShortcut(_translate("EXAUT_GUI", "Ctrl+I"))
        self.actionExport_to_Excel.setText(_translate("EXAUT_GUI", "Export to Excel"))
        self.actionExport_to_Excel.setShortcut(_translate("EXAUT_GUI", "Ctrl+E"))
        self.customimportexport.setText(_translate("EXAUT_GUI", "Custom Import/Export"))
        self.actionRefresh.setText(_translate("EXAUT_GUI", "Refresh"))
        self.actionRefresh.setShortcut(_translate("EXAUT_GUI", "Ctrl+R"))
        self.actionTabsize.setText(_translate("EXAUT_GUI", "S"))
        self.actionstaticsize.setText(_translate("EXAUT_GUI", "Static"))

        #make actionTabsize text bold
        tf = QtGui.QFont()
        tf.setBold(True)
        tf.setFamily("Times")
        tf.setPointSize(10)
        self.actionTabsize.setFont(tf)
        #set background very light grey
        self.actionOpen_Files_Explorer.setText(_translate("EXAUT_GUI", "Open Files Explorer"))
        self.actionOpen_Files_Explorer.setShortcut(_translate("EXAUT_GUI", "Ctrl+O"))
        self.actionOpenTabUrl.setText(_translate("EXAUT_GUI", "Open Tab URL"))
        self.actionOpenTabUrl.setShortcut(_translate("EXAUT_GUI", "Ctrl+U"))
        self.actionAdd_exe.setText(_translate("EXAUT_GUI", "Add .exe"))
        self.actionAdd_exe.setShortcut(_translate("EXAUT_GUI", "Ctrl+A"))
        self.actionAdd_tabto.setText(_translate("EXAUT_GUI", "Add Tabto"))
        self.actionAdd_tablast.setText(_translate("EXAUT_GUI", "Add Tablast"))
        self.actionAbout.setText(_translate("EXAUT_GUI", "About"))
        self.actionCopy.setText(_translate("EXAUT_GUI", "Copy File"))
        self.sht2tbl.setText(_translate("EXAUT_GUI", "add sht2tbl"))

        self.actionCopy_folder.setText(_translate("EXAUT_GUI", "Copy Folder"))

        self.actionTab.setText(_translate("EXAUT_GUI", "Add Tab"))
        self.actionAdd_Folder.setText(_translate("EXAUT_GUI", "Add Folder"))
        
        self.actionTab_Move.setText(_translate("EXAUT_GUI", "Move Tab -> Form"))
        self.actionTab_Copy.setText(_translate("EXAUT_GUI", "Copy Tab -> Form"))

        self.actionTabUrl.setText(_translate("EXAUT_GUI", "Add Tab URL"))

        self.actionTabFolder.setText(_translate("EXAUT_GUI", "Add Tab Folder"))
        self.actionHidden_mode.setText(_translate("EXAUT_GUI", "Show Hidden Tabs"))

        self.actionAdd_url.setText(_translate("EXAUT_GUI", "Add URL"))
        self.actionAdd_Seq.setText(_translate("EXAUT_GUI", "Add Sequence"))
        self.actionAdd_Proc.setText(_translate("EXAUT_GUI", "Add New Button"))

        self.actionAdd_Desc.setText(_translate("EXAUT_GUI", "Add Description"))

        self.actionEdit_layout.setText(_translate("EXAUT_GUI", "Edit Layout"))


class MyBar(QWidget):

    def __init__(self, parent):
        super(MyBar, self).__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.title = QLabel("My Own Bar")

        btn_size = 24

        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.btn_close.setFixedSize(btn_size,btn_size)
        self.btn_close.setStyleSheet("background-color: red;")

        self.btn_min = QPushButton("-")
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.setStyleSheet("background-color: gray;")

        self.btn_max = QPushButton("+")
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size, btn_size)
        self.btn_max.setStyleSheet("background-color: gray;")

        self.title.setFixedHeight(35)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)

        self.title.setStyleSheet("""
            background-color: black;
            color: white;
        """)
        self.setLayout(self.layout)

        self.start = QPoint(0, 0)
        self.pressing = False

    def resizeEvent(self, QResizeEvent):
            super(MyBar, self).resizeEvent(QResizeEvent)
            self.title.setFixedWidth(self.parent.width())

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.parent.move(self.parent.pos() + event.globalPosition().toPoint() - self.start)
                self.start = event.globalPosition().toPoint()
                event.accept()


    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False


    def btn_close_clicked(self):
        self.parent.close()

    def btn_max_clicked(self):
        self.parent.showMaximized()

    def btn_min_clicked(self):
        self.parent.showMinimized()
