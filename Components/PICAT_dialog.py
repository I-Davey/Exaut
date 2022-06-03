# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\MT4\Python\PICAT_SQL\PICAT_SQL_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ButtonDialog(object):
    def setupDialog(self, ButtonDialog):
        ButtonDialog.setObjectName("ButtonDialog")
        ButtonDialog.resize(294, 165)
        self.gridLayout_3 = QtWidgets.QGridLayout(ButtonDialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(ButtonDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 270, 141))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 0, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 1, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(ButtonDialog)
        QtCore.QMetaObject.connectSlotsByName(ButtonDialog)

    def retranslateUi(self, ButtonDialog):
        _translate = QtCore.QCoreApplication.translate
        ButtonDialog.setWindowTitle(_translate("ButtonDialog", "ButtonDialog"))
        self.pushButton.setText(_translate("ButtonDialog", "PushButton"))
        self.pushButton_2.setText(_translate("ButtonDialog", "PushButton"))
        self.pushButton_3.setText(_translate("ButtonDialog", "PushButton"))
        self.pushButton_4.setText(_translate("ButtonDialog", "PushButton"))

