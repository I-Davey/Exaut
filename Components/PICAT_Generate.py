#from PyQt6.QtWidgets import QApplication, QMainWindow

from PyQt6 import QtCore,QtGui,QtWidgets
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
import os,sys,time,ctypes,shutil,winshell,win32api,subprocess,psutil
import glob,ctypes,openpyxl,apsw,csv,math,win32api
from openpyxl import load_workbook
from subprocess import call
from functools import partial
from win32com.client import Dispatch
import win32api
import Components.PICAT_gui as PICAT_gui
from Components.PICAT_gui import Ui_PICAT_SM
#
# SQLite Functions
def ReadSQL(query,attempts=12,sec=0.2):
    val = []
    try:
        results = cursor.execute(query)
        for result in results:
            val.append(list(result))
        return(val)
    except apsw.SQLError as e:
        err = str(e)
        for i in range(0,attempts):
            try:
                results = cursor.execute(query)
                for result in results:
                    val.append(list(result))
                return(val)
            except apsw.SQLError as e:
                if err.find("database is locked")>=0:
                    time.sleep(sec)
                    i -= 1
                if i==attempts-1:
                    print(query)
                    print(str(e))
                    return(val)
                else:
                    time.sleep(sec)
                    continue
    except apsw.ConstraintError as e2:
        err = str(e2)
        for i in range(0,attempts):
            try:
                results = cursor.execute(query)
                for result in results:
                    val.append(list(result))
                return(val)
            except apsw.ConstraintError as e2:
                if i==attempts-1:
                    print(query)
                    print(str(e2))
                    return(val)
                else:
                    time.sleep(sec)
                    continue
    except apsw.BusyError as e3:
        err = str(e3)
        while err.find("database is locked")>=0:
            time.sleep(sec)
    
def WriteSQL(query,attempts=12,sec=0.2):
    try:
        cursor.execute(query)
    except apsw.SQLError as e:
        err = str(e)
        for i in range(0,attempts):
            try:
                cursor.execute(query)
                break
            except apsw.SQLError as e:
                if err.find("database is locked")>=0:
                    time.sleep(sec)
                    i -= 1
                if i==attempts-1:
                    print(query)
                    print(str(e))
                    break
                else:
                    time.sleep(sec)
                    continue
    except apsw.ConstraintError as e2:
        err = str(e2)
        for i in range(0,attempts):
            try:
                cursor.execute(query)
                break
            except apsw.ConstraintError as e2:
                if i==attempts-1:
                    print(query)
                    print(str(e2))
                    break
                else:
                    time.sleep(sec)
                    continue
    except apsw.BusyError as e3:
        err = str(e3)
        while err.find("database is locked")>=0:
            time.sleep(sec)

def aReadSQL(a,query,attempts=12,sec=0.2):
    val = []
    try:
        results = a.execute(query)
        for result in results:
            val.append(list(result))
        return(val)
    except apsw.SQLError as e:
        err = str(e)
        for i in range(0,attempts):
            try:
                results = a.execute(query)
                for result in results:
                    val.append(list(result))
                return(val)
            except apsw.SQLError as e:
                if err.find("database is locked")>=0:
                    time.sleep(sec)
                    i -= 1
                if i==attempts-1:
                    print(query)
                    print(str(e))
                    return(val)
                else:
                    time.sleep(sec)
                    continue
    except apsw.ConstraintError as e2:
        err = str(e2)
        for i in range(0,attempts):
            try:
                results = a.execute(query)
                for result in results:
                    val.append(list(result))
                return(val)
            except apsw.ConstraintError as e2:
                if i==attempts-1:
                    print(query)
                    print(str(e2))
                    return(val)
                else:
                    time.sleep(sec)
                    continue
    except apsw.BusyError as e3:
        err = str(e3)
        while err.find("database is locked")>=0:
            time.sleep(sec)
    
def aWriteSQL(a,query,attempts=12,sec=0.2):
    try:
        a.execute(query)
    except apsw.SQLError as e:
        err = str(e)
        for i in range(0,attempts):
            try:
                a.execute(query)
                break
            except apsw.SQLError as e:
                if err.find("database is locked")>=0:
                    time.sleep(sec)
                    i -= 1
                if i==attempts-1:
                    print(query)
                    print(str(e))
                    break
                else:
                    time.sleep(sec)
                    continue
    except apsw.ConstraintError as e2:
        err = str(e2)
        for i in range(0,attempts):
            try:
                a.execute(query)
                break
            except apsw.ConstraintError as e2:
                if i==attempts-1:
                    print(query)
                    print(str(e2))
                    break
                else:
                    time.sleep(sec)
                    continue
    except apsw.BusyError as e3:
        err = str(e3)
        while err.find("database is locked")>=0:
            time.sleep(sec)

scriptpath = os.path.realpath(__file__)
scriptpath = os.path.dirname(scriptpath)+"\\"
scriptpath = scriptpath.replace("\\","\\\\")
print("scriptpath = "+scriptpath)

# Format Functions
def FormatMR(x,d,comma=True):
    neg = ""
    if x<0:
        neg = "-"
        x = -x
    val = str(x)
    val = val.split(".")

    if comma==True:
        temp = ""
        frag = val[0]
        while len(frag)>0:
            if len(frag)-3>0:
                temp = ","+frag[-3:]+temp
                frag = frag[0:len(frag)-3]
            else:
                temp = frag+temp
                frag = ""
        if temp!="":
            val[0] = temp
    
    if len(val)>1:
        dec = float("0."+val[1])
        dec = '{:.{prec}f}'.format(dec,prec=d)
        dec = str(dec)
        dec = dec.split(".")[1]
        #print("a = "+dec)
    else:
        dec = "0"*d
        #print("b = "+str(dec))
    val = neg+val[0]+"."+dec
    return(val)

# Connect to DB
if os.path.exists(scriptpath+"PICAT_SQL_connect.db")==True:
    connection = apsw.Connection(scriptpath+"PICAT_SQL_connect.db")
else:
    result = ctypes.windll.user32.MessageBoxW(0,scriptpath+"PICAT_SQL_connect.db does not exist?","",1)
    if result==1:
        sys.exit()

cursor = connection.cursor()

print("PICAT_SQL_connect connected...")
WriteSQL("create table if not exists connection(connectionpath char(1023) "+
         "not null,connection char(255) not null,primary key(connectionpath,"+
         "connection)); pragma foreign_keys = on")

record = ReadSQL("select count(connection) from connection")

print("Existing record?")
print(record)

record = ReadSQL("select connectionpath,connection from connection")
print("Existing record?")
print(record)

# Disconnect from DB
connection.close(True)

print("PICAT_connect disconnected...")
print("Database in record above connecting...")

# Connect to DB
if len(record)>0:
    if os.path.exists(str(record[0][0])+str(record[0][1]))==True:
        connection = apsw.Connection(str(record[0][0])+str(record[0][1]))
    else:
        result = ctypes.windll.user32.MessageBoxW(0,str(record[0][0])+str(record[0][1])+" does not exist?","",1)
        if result==1:
            sys.exit()
else:
    result = ctypes.windll.user32.MessageBoxW(0,str(record[0][0])+str(record[0][1])+" not found in PICAT_SQL_connect.db?","",1)
    if result==1:
        sys.exit()

cursor = connection.cursor()

WriteSQL("create table if not exists pyexcelmenu(type char(6) not null,runsequence "+
         "integer,excelsqlpath char(1023),excelfile char(255),databasepath char(1023),"+
         "databasefile char(255),enginepathfile char(1023)); pragma foreign_keys = on")

WriteSQL("create table if not exists mastdbs(databasepath char(1023),databasefile "+
         "char(255) not null,primary key(databasepath,databasefile)); pragma foreign_keys = on")

WriteSQL("create table if not exists masttbls(tbl_name char(63) not null primary key,sql "+
         "char(1000000),fields char(1000000),reqpopulate char(1000000)); pragma foreign_keys = on")

WriteSQL("create table if not exists mastdbtbls(databasefile char(255),tbl_name char(63),"+
         "primary key(databasefile,tbl_name)); pragma foreign_keys = on")

'''
WriteSQL("create table if not exists mastdbtbls(databasefile char(255) not null references "+
         "mastertables(databasefile) on delete cascade on update cascade,tbl_name char(63),"+
         "sql char(1000000),fields char(1000000),reqpopulate char(1000000),foreign key("+
         "tbl_name,sql,fields) references mastertablesrec(tbl_name,sql,fields) on delete cascade "+
         "on update cascade); pragma foreign_keys = on")
'''

def writeTable(path,file):
    temp00 = path
    if os.path.exists(temp00)==True:
        if path[0:1]=="\\":
            path = path[1:]
        newpath = path.replace("\\","\\\\")
        WriteSQL("attach database '"+newpath+"\\\\"+file+"' as DB")
        sql_state = ReadSQL("select tbl_name,sql as sql_create from DB.sqlite_master "+
                            "where type = 'table'")
        WriteSQL("begin")
        for i in range(len(sql_state)):
            get_fields = ReadSQL("pragma table_info('"+sql_state[i][0]+"')")
            fields = ""
            for j in range(len(get_fields)):
                if j>0:
                    fields += ","+get_fields[j][1]
                else:
                    fields += get_fields[j][1]
            WriteSQL("insert or replace into masttbls values('"+sql_state[i][0]+"','"+
                     sql_state[i][1]+"','"+fields+"',null)")
            WriteSQL("insert or replace into mastdbtbls values('"+file+"','"+
                    sql_state[i][0]+"')")
        WriteSQL("commit")
        WriteSQL("detach database DB")
    else:
        ctypes.windll.user32.MessageBoxW(0,temp00+" does not exist?","",1)

result = ctypes.windll.user32.MessageBoxW(0,"Confirm (re)population of\nmasttbls & mastdbtbls?","Warning",4)
if result==6:
    WriteSQL("delete from masttbls")
    WriteSQL("delete from mastdbtbls")
    all_dbs = ReadSQL("select * from mastdbs")
    for i in range(len(all_dbs)):
        writeTable(all_dbs[i][0],all_dbs[i][1])

# Disconnect from DB
connection.close(True)


