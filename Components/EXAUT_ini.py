# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\MT4\Python\EXAUT_GUI\EXAUT_GUI_ini.ui'
#
# Created by: PyQt6 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(220, 150)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.Ini_VerLay = QtWidgets.QVBoxLayout()
        self.Ini_VerLay.setObjectName("Ini_VerLay")
        self.Ini_Broker = QtWidgets.QComboBox(Dialog)
        self.Ini_Broker.setMinimumSize(QtCore.QSize(0, 25))
        self.Ini_Broker.setMaximumSize(QtCore.QSize(16777215, 25))
        self.Ini_Broker.setObjectName("Ini_Broker")
        self.Ini_Broker.addItem("")
        self.Ini_VerLay.addWidget(self.Ini_Broker)
        self.Ini_AcctNum = QtWidgets.QComboBox(Dialog)
        self.Ini_AcctNum.setMinimumSize(QtCore.QSize(0, 25))
        self.Ini_AcctNum.setMaximumSize(QtCore.QSize(16777215, 25))
        self.Ini_AcctNum.setObjectName("Ini_AcctNum")
        self.Ini_AcctNum.addItem("")
        self.Ini_VerLay.addWidget(self.Ini_AcctNum)
        self.Ini_ServerName = QtWidgets.QLabel(Dialog)
        self.Ini_ServerName.setMinimumSize(QtCore.QSize(0, 25))
        self.Ini_ServerName.setMaximumSize(QtCore.QSize(16777215, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.Ini_ServerName.setFont(font)
        self.Ini_ServerName.setObjectName("Ini_ServerName")
        self.Ini_VerLay.addWidget(self.Ini_ServerName)
        self.Ini_OKCancel = QtWidgets.QDialogButtonBox(Dialog)
        self.Ini_OKCancel.setOrientation(QtCore.Qt.Horizontal)
        self.Ini_OKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.Ini_OKCancel.setObjectName("Ini_OKCancel")
        self.Ini_VerLay.addWidget(self.Ini_OKCancel)
        self.gridLayout.addLayout(self.Ini_VerLay, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.Ini_OKCancel.accepted.connect(Dialog.accept)
        self.Ini_OKCancel.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "start.ini Dialog"))
        self.Ini_Broker.setItemText(0, _translate("Dialog", "* Broker"))
        self.Ini_AcctNum.setItemText(0, _translate("Dialog", "* AcctNum"))
        self.Ini_ServerName.setText(_translate("Dialog", "SomeText"))

