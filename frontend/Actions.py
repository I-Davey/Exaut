from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys


class sidebar_frame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(u"QFrame{\n"
        "	background-color: #000;\n"
        "}\n"
        "QPushButton{\n"
        "	padding: 20px 10px;\n"
        "	border: none;\n"
        "	border-radius: 10px;\n"
        "	background-color: #000;\n"
        "	color: #fff;\n"
        "}\n"
        "QPushButton:hover{\n"
        "	background-color: rgb(0, 92, 157);\n"
        "}")
    def handle_anim(self, width, new_width):
        self.anim_show = QPropertyAnimation(self, b"minimumWidth")

        self.anim_show.setDuration(300)
        self.anim_show.setStartValue(width)
        self.anim_show.setEndValue(new_width)

        self.setMaximumSize(QSize(50, 16777215))
       

        self.anim_show.start()


class sidebar(QWidget):
    def __init__(self, parent, anim_frame):
        super().__init__(anim_frame)
        self.parent = parent
        self.hidden = False
        self.anim_frame = anim_frame
        self.show()
    
    def hide_handler(self):
        if self.hidden:
            self.show()
            self.hidden = False
        else:
            self.hide()
            self.hidden = True

    def slideLeftMenu(self):
        width = self.width()
        parent_width = self.parent.width()

        # If minimized
        if width == 50:
            # Expand menu
            newWidth = 150
        # If maximized
        else:
            # Restore menu
            newWidth = 50


            self.anim_frame.handle_anim(width, newWidth)




class Actions(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # set the title of main window

        # set the size of window
        self.Width = 800
        self.height = int(0.618 * self.Width)
        self.resize(self.Width, self.height)
		
		# add all widgets
       

        self.searchbar = QLineEdit(self)
        self.searchbar.setPlaceholderText('Search')

        self.searchbar.setStyleSheet("background-color: #f5f5f5; border: 1px solid #e5e5e5; border-radius: 5px; padding: 0px 10px;")


        self.initUI()

    def initUI(self):
        self.menubar = self.menuBar()

        #sidebar_anim.handle_anim(50, 150)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        self.sidebar_qframe = sidebar_frame(main_widget)



        self.setMenuBar(self.menubar)
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction('Quit', self.close)
        self.setWindowTitle('Actions')



        #add a button to qframe
        self.button = QPushButton('Actions', self.sidebar_qframe )
        self.button.setStyleSheet("QPushButton{\n"
        "	padding: 20px 10px;\n"
        "	border: none;\n"
        "	border-radius: 10px;\n"
        "	background-color: rgb(0, 92, 157);\n"
        "	color: #fff;\n"
        "}\n"
        "QPushButton:hover{\n"
        "	background-color: rgb(0, 92, 157);\n"
        "}")


        #self.button.clicked.connect(self.hide_handler)
        main_layout = QHBoxLayout(main_widget)
        main_layout.addWidget(self.sidebar_qframe)
        main_layout.addWidget(self.searchbar)
        main_layout.addWidget(self.button)
        self.setLayout(main_layout)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)

        #main_widget.setLayout(main_layout)


        """

        self.btn_1 = QPushButton('1', sidebar_anim)
        self.btn_2 = QPushButton('2', sidebar_anim)
        self.btn_3 = QPushButton('3', sidebar_anim)
        self.btn_4 = QPushButton('4', sidebar_anim)

        self.hidebtn = QPushButton('Hide', sidebar_anim)


        left_widget = sidebar(self, sidebar_anim)


        left_layout = QVBoxLayout(sidebar_anim)
        left_layout.addWidget(self.hidebtn)
        self.hidebtn.clicked.connect(left_widget.slideLeftMenu)

        left_layout.addWidget(self.searchbar)
        left_layout.addWidget(self.btn_1)
        left_layout.addWidget(self.btn_2)
        left_layout.addWidget(self.btn_3)
        left_layout.addWidget(self.btn_4)
        left_layout.addStretch(5)
        left_layout.setSpacing(20)

        left_widget.setLayout(left_layout)


        


        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)

        main_layout.addWidget(sidebar_anim)
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Actions()
    window.show()
    sys.exit(app.exec())


    

