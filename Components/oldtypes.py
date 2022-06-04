
import os
import ctypes
import shutil
from loguru import logger
import time
from .PICAT_ini import Ui_Dialog
from .PICAT_dialog import Ui_ButtonDialog
from PyQt6 import QtWidgets
import math
from functools import partial

def run(parent_, bseq, bname, pname, tname, ReadSQL):
    logger.debug("running in old type")
    for pf in range(len(bseq)):
        if str(bseq[pf][2])=="move":
            # If doing a folder, directory can be created
            if bseq[pf][1]==None or bseq[pf][1]=="" or bseq[pf][1]=="None":
                if os.path.exists(bseq[pf][3])==False:
                    ctypes.windll.user32.MessageBoxW(0,bseq[pf][3]+" source does not exist?","Failed move: "+bname+"! \\"+str(bseq[pf][9]),0)
                else:
                    try:
                        shutil.move(bseq[pf][3],bseq[pf][4])
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem moving "+bseq[pf][3]+" to "+bseq[pf][4]+"?","Failed move: "+bname+"! \\"+str(bseq[pf][9]),0)
            elif os.path.exists(bseq[pf][3]+"\\"+bseq[pf][1])==False:
                if os.path.exists(bseq[pf][3])==False:
                    ctypes.windll.user32.MessageBoxW(0,bseq[pf][3]+" source does not exist?","Failed move: "+bname+"! \\"+str(bseq[pf][9]),0)
                else:
                    try:
                        shutil.move(bseq[pf][3],bseq[pf][4])
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem moving "+bseq[pf][3]+" to "+bseq[pf][4]+"?","Failed move: "+bname+"! \\"+str(bseq[pf][9]),0)
            else:
                # If doing a file, directory must already exist
                if os.path.exists(bseq[pf][4])==False:
                    ctypes.windll.user32.MessageBoxW(0,bseq[pf][4]+" target does not exist?","Failed move: "+bname+"! \\"+str(bseq[pf][9]),0)
                else:
                    try:
                        shutil.move(bseq[pf][3]+"\\"+bseq[pf][1],bseq[pf][4]+"\\"+bseq[pf][1])
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem moving "+bseq[pf][3]+"\\"+bseq[pf][1]+" to "+bseq[pf][4]+"\\"+bseq[pf][1]+"?","Failed move: "+bname+"! \\"+str(bseq[pf][9]),0)
        elif str(bseq[pf][2])=="delfile":
            if os.path.exists(bseq[pf][3]+"\\"+bseq[pf][1])==True:
                try:
                    os.remove(bseq[pf][3]+"\\"+bseq[pf][1])
                except:
                    ctypes.windll.user32.MessageBoxW(0,"Problem deleting "+bseq[pf][3]+"\\"+bseq[pf][1]+"?","Failed delfile: "+bname+"! \\"+str(bseq[pf][9]),0)       
        elif str(bseq[pf][2])=="tabto":
            if str(bseq[pf][1])!="" and bseq[pf][1]!=None:
                parent_.lasttab = parent_.SM_Tabs.tabText(parent_.SM_Tabs.currentIndex())
                print(str(bseq[pf][1]))
                index = [index for index in range(parent_.SM_Tabs.count()) if str(bseq[pf][1]) == parent_.SM_Tabs.tabText(index)]
                if len(index)>0:
                    print(str(index[0]))
                    parent_.SM_Tabs.setCurrentIndex(index[0])
        elif str(bseq[pf][2])=="tablast":
            if parent_.lasttab!="":
                index = [index for index in range(parent_.SM_Tabs.count()) if str(parent_.lasttab) == parent_.SM_Tabs.tabText(index)]
                if len(index)>0:
                    parent_.SM_Tabs.setCurrentIndex(index[0])
        elif str(bseq[pf][2])=="buttondialog":
            Create_Button_Dialog(parent_, pname,tname,bname,bseq[pf][0],bseq[pf][1],1)
        elif str(bseq[pf][2])=="buttontask":
            Create_Button_Dialog(parent_, pname,tname,bname,bseq[pf][0],bseq[pf][1],2)
        elif str(bseq[pf][2])=="srtg":
            if os.path.exists(str(bseq[pf][0])+"\\$Srtg.bat")==True:
                os.system("rm "+str(bseq[pf][0])+"\\$Srtg.bat")
            if os.path.exists(str(bseq[pf][0])+"\\"+str(bseq[pf][1]))==True:
                txt = open(str(bseq[pf][0])+"\\"+str(bseq[pf][1])).read()
                txt = txt.replace("%Source%",str(bseq[pf][3]))
                txt = txt.replace("%Target%",str(bseq[pf][4]))
                os.system("type NUL > "+str(bseq[pf][0])+"\\$Srtg.bat")
                if os.path.exists(str(bseq[pf][0])+"\\$Srtg.bat")==True:
                    newtxt = open(str(bseq[pf][0])+"\\$Srtg.bat",'w')
                    newtxt.write(txt)
                    newtxt.close()
                    os.system(str(bseq[pf][0])+"\\$Srtg.bat")
                else:
                    ctypes.windll.user32.MessageBoxW(0,str(bseq[pf][0])+"\\$Srtg.bat did not create?","Failed srtg: "+bname+"! \\"+str(bseq[pf][9]),0)
            else:
                ctypes.windll.user32.MessageBoxW(0,str(bseq[pf][0])+"\\"+str(bseq[pf][1])+" does not exist?","Failed srtg: "+bname+"! \\"+str(bseq[pf][9]),0)
        else:
            logger.error(f"Cannot find Button type {str(bseq[pf][2])}  for {bname} on tab {tname}")


def Create_Button_Dialog(parent_,fname,tname,bname,dimension,dialogname,mode):
    allbuttons = parent_.ReadSQL("select buttonname from buttondialogs where "+
                            "source_formname = '"+fname+"' and source_tab = '"+
                            tname+"' and source_buttonname = '"+bname+
                            "' order by buttonsequence asc")
    if len(allbuttons)>0:
        dto = QtWidgets.QDialog()
        dto.b = Ui_ButtonDialog()
        dto.b.setupDialog(dto)
        if dialogname!=None and dialogname!="":
            print(dialogname)
            dto.setWindowTitle(str(dialogname))
        if dimension!=None and dimension!="":
            dimension = str(dimension)
            dimension = dimension.split(',')
            if len(dimension)>1:
                try:
                    xx = int(dimension[0])
                    yy = int(dimension[1])
                    dto.resize(xx,yy)
                except:
                    pass

        for i in reversed(range(dto.b.gridLayout.count())):
            dto.b.gridLayout.itemAt(i).widget().setParent(None)

        tabgrid = parent_.ReadSQL("select max(columnnum) from buttondialogs where "+
                            "source_formname = '"+fname+"' and source_tab = '"+
                            tname+"' and source_buttonname = '"+bname+"'")
        if len(tabgrid)<1:
            tabgrid = 1
        else:
            tabgrid = int(tabgrid[0][0])

        formbuttons = parent_.ReadSQL("select buttonname,formname,tab from buttondialogs where "+
                                "source_formname = '"+fname+"' and source_tab = '"+
                                tname+"' and source_buttonname = '"+bname+
                                "' and columnnum is null order by buttonsequence asc")
        formbuttons2 = parent_.ReadSQL("select buttonname,formname,tab from buttondialogs where "+
                                "source_formname = '"+fname+"' and source_tab = '"+
                                tname+"' and source_buttonname = '"+bname+
                                "' and columnnum is not null order by buttonsequence asc")
        buttonsordered = []
        for i in range(len(formbuttons)):
            buttonsordered.append(formbuttons[i])
        for i in range(len(formbuttons2)):
            buttonsordered.append(formbuttons2[i])
        buttoncol = parent_.ReadSQL("select columnnum from buttondialogs where "+
                            "source_formname = '"+fname+"' and source_tab = '"+
                            tname+"' and source_buttonname = '"+bname+
                            "' and columnnum is not null order by buttonsequence asc")
        buttoncolordered = []
        for i in range(len(formbuttons)):
            buttoncolordered.append(None)
        for i in range(len(formbuttons2)):
            buttoncolordered.append(buttoncol[i])
        buttonsdesc = parent_.ReadSQL("select buttondesc from buttondialogs where "+
                                "source_formname = '"+fname+"' and source_tab = '"+
                                tname+"' and source_buttonname = '"+bname+
                                "' and columnnum is null order by buttonsequence asc")
        buttonsdesc2 = parent_.ReadSQL("select buttondesc from buttondialogs where "+
                                "source_formname = '"+fname+"' and source_tab = '"+
                                tname+"' and source_buttonname = '"+bname+
                                "' and columnnum is not null order by buttonsequence asc")
        buttondescordered = []
        for i in range(len(buttonsdesc)):
            buttondescordered.append(buttonsdesc[i])
        for i in range(len(buttonsdesc2)):
            buttondescordered.append(buttonsdesc2[i])

        accumbuttons = []
        for bn in range(len(buttonsordered)):
            if bn!=0:
                dto.b.gridLayout.setRowStretch(bn,3)
            dto.b.button = QtWidgets.QPushButton(dto.b.scrollAreaWidgetContents)
            dto.b.button.setToolTip(str(buttondescordered[bn][0]))
            dto.b.button.setObjectName(bname+"_Button_"+str(1)+"_"+str(bn+1))
            dto.b.button.setText(str(buttonsordered[bn][0]))

            if buttoncolordered[bn]==None:
                x = 0
                y = 0
                if tabgrid<1:
                    tabgrid = 1
                    x = bn//tabgrid
                    y = bn%tabgrid
                    while len(accumbuttons)<1:
                        accumbuttons.append(0)
                    accumbuttons[0] += 1
                else:
                    if tabgrid<2:
                        x = bn//tabgrid
                        y = bn%tabgrid
                        while len(accumbuttons)<1:
                            accumbuttons.append(0)
                        accumbuttons[0] += 1
                    else:
                        x = bn%math.ceil(len(buttonsordered)/tabgrid)
                        y = bn//math.ceil(len(buttonsordered)/tabgrid)
                        while len(accumbuttons)<y+1:
                            accumbuttons.append(0)
                        accumbuttons[y] += 1
            else:
                if len(formbuttons2)>0:
                    if len(accumbuttons)<tabgrid:
                        lenaccumbuttons = len(accumbuttons)
                        for i in range(tabgrid):
                            if i>=lenaccumbuttons:
                                accumbuttons.append(0)
                    
                    y = buttoncolordered[bn][0]-1
                    if tabgrid<2:
                        tabgrid = 1
                    if y>tabgrid-1:
                        y = tabgrid-1
                    elif y<0:
                        y = 0
                    x = accumbuttons[y]
                    
                    accumbuttons[y] += 1

            dto.b.gridLayout.addWidget(dto.b.button, x, y, 1, 1)
            dto.b.button.setStyleSheet("QPushButton { background-color: none }"
                                        "QPushButton:hover { background-color: lightblue }"
                                        "QPushButton:focus { background-color: tomato }" )
            dto.b.button.clicked.connect(partial(on_click_button_plus,
                                                    str(buttonsordered[bn][1]),
                                                    str(buttonsordered[bn][2]),
                                                    str(buttonsordered[bn][0]),
                                                    bname+"_Button_"+str(1)+"_"+str(bn+1),dto,mode,2))
    
        result = dto.exec()

def on_click_button_plus(self,pname,tname,bname,objn,d,typemode,mode=0):
    self.on_click_button(pname,tname,bname,objn,mode)
    if typemode==1:
        d.reject()

