#from PyQt6.QtWidgets import QApplication, QMainWindow

from PyQt6 import QtCore,QtGui,QtWidgets
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
import os,sys,time,ctypes,shutil,winshell,win32api,subprocess,psutil
import glob,ctypes,openpyxl,apsw,csv,math,win32api,psycopg2
from openpyxl import load_workbook
from subprocess import call
from subprocess import PIPE,Popen
from functools import partial
from win32com.client import Dispatch
import win32api
import Components.EXAUT_gui as EXAUT_gui
from Components.EXAUT_gui import Ui_EXAUT_GUI
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
if os.path.exists(scriptpath+"EXAUT_SQL_connect.db")==True:
    connection = apsw.Connection(scriptpath+"EXAUT_SQL_connect.db")
else:
    result = ctypes.windll.user32.MessageBoxW(0,scriptpath+"EXAUT_SQL_connect.db does not exist?","",1)
    if result==1:
        sys.exit()

cursor = connection.cursor()

print("EXAUT_SQL_connect connected...")
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

print("EXAUT_connect disconnected...")
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
    result = ctypes.windll.user32.MessageBoxW(0,str(record[0][0])+str(record[0][1])+" not found in EXAUT_SQL_connect.db?","",1)
    if result==1:
        sys.exit()

cursor = connection.cursor()

def ReadPG(connection,cur,query,attempts=12,sec=1):
    val = []
    try:
        cur.execute(query)
        results = cur.fetchall()
        for result in results:
            val.append(list(result))
        return(val)
    except Exception as e4:
        for i in range(0,attempts):
            try:
                cur.execute(query)
                results = self.cur.fetchall()
                for result in results:
                    val.append(list(result))
                return(val)
            except Exception as e4:
                if i==attempts-1:
                    print(query)
                    print(str(e4))
                    return(val)
                else:
                    time.sleep(sec)
                    continue

# Write to Postgres
def WritePG(connection,cur,query,attempts=12,sec=1,box=False):
    try:
        cur.execute(query)
        connection.commit()
    except Exception as e4:
        for i in range(0,attempts):
            try:
                cur.execute(query)
                connection.commit()
            except Exception as e4:
                if i==attempts-1:
                    print(query)
                    print(str(e4))
                    return(val)
                else:
                    time.sleep(sec)
                    continue

def writeTable(hostip,portnum,username,passcode,name):
    connpg = psycopg2.connect(dbname=name,user=username,password=passcode,host=hostip,port=portnum)
    cursorpg = connpg.cursor()
    
    WriteSQL("delete from pgtables")

    tbl_pkey_q = get_primary_key(cursorpg)
    fkeyreftbl = get_foreign_key(cursorpg)
    col_q = get_columns(cursorpg)

    all_ddl = []
    WriteSQL("begin")
    for i in col_q:
        #table name and columns
        main_ind = str(i).index('|')
        table_name = str(i[0:main_ind])
        columns = str(i[main_ind+1:])
        
        #primary key/primary keys
        pkeys_q = ""
        for i2 in tbl_pkey_q:
            pkey_ind = str(i2).index('|')
            pkey_table_name = str(i2[0:pkey_ind])
            pkey_columns = str(i2[pkey_ind+1:])
            if table_name == pkey_table_name:
                pkeys_q = pkey_columns
    
        #foreign key/foreign keys
        fkey_query = []
        for i in fkeyreftbl:
            fkey_ind = str(i).index('|')
            main = str(i[0:fkey_ind])
            ind_sep1 = main.index('-')
            main_tbl = main[0:ind_sep1]
            fkey = main[ind_sep1+1:]
            ref = str(i[fkey_ind+1:])
            ind_sep2 = ref.index('-')
            ref_tbl = ref[0:ind_sep2]
            ref_col = ref[ind_sep2+1:]
            if main_tbl == table_name:
                fkey_query.append("FOREIGN KEY ("+fkey+")"+" REFERENCES "+ref_tbl+"("+ref_col+")")
        fkey_query_v2 = ""
        for x2 in range (len(fkey_query)):
            fkey_query_v2+=" "+str(fkey_query[x2])+','
        fkey_query_v2 = fkey_query_v2[1:-1]
        
        #ddl queries
        if len(pkeys_q) > 0 and len(fkey_query_v2) > 0:
            ddl = "create table if not exists "+table_name+"("+columns+","+fkey_query_v2+",primary key("+pkeys_q+"))"
            all_ddl.append(ddl)

            WriteSQL("insert into pgtables values('"+str(hostip)+"',"+str(portnum)+",'"+str(username)+"','"+str(passcode)+"','"+str(name)+"','"+table_name+"','"+ddl+"','"+getFields(connpg,cursorpg,table_name)+"',null)")
            #print(ddl+'\n')
        elif len(pkeys_q) > 0 and len(fkey_query_v2) == 0:
            ddl = "create table if not exists "+table_name+"("+columns+",primary key("+pkeys_q+"))"
            all_ddl.append(ddl)
            
            WriteSQL("insert into pgtables values('"+str(hostip)+"',"+str(portnum)+",'"+str(username)+"','"+str(passcode)+"','"+str(name)+"','"+table_name+"','"+ddl+"','"+getFields(connpg,cursorpg,table_name)+"',null)")
            #print(ddl+'\n')
        elif len(pkeys_q) == 0 and len(fkey_query_v2) > 0:
            ddl = "create table if not exists "+table_name+"("+columns+","+fkey_query_v2+")"
            all_ddl.append(ddl)
            
            WriteSQL("insert into pgtables values('"+str(hostip)+"',"+str(portnum)+",'"+str(username)+"','"+str(passcode)+"','"+str(name)+"','"+table_name+"','"+ddl+"','"+getFields(connpg,cursorpg,table_name)+"',null)")
            #print(ddl+'\n')
        else:
            ddl = "create table if not exists "+table_name+"("+columns+")"
            all_ddl.append(ddl)
            
            WriteSQL("insert into pgtables values('"+str(hostip)+"',"+str(portnum)+",'"+str(username)+"','"+str(passcode)+"','"+str(name)+"','"+table_name+"','"+ddl+"','"+getFields(connpg,cursorpg,table_name)+"',null)")
            #print(ddl+'\n')
    WriteSQL("commit")

    #table_names = ReadPG(connpg,cursorpg,"select distinct table_name from information_schema.tables where table_schema = 'public'")

    #p = Popen("pg_dump --schema-only --table=\"broker\" postgresql://"+username+":"+passcode+"@"+hostip+":"+str(portnum)+"/"+name,stdout=PIPE)
    #a = p.communicate()[0].decode("utf-8")
    #print(a)
    #a.split(' ')

    #pg_dump --schema-only --table="broker" postgresql://postgres:abc123@127.0.0.1:5432/icat > "C:\Users\Matthew\Desktop\some.sql"
    
    '''
    for i in range(len(table_names)):
        #statement = ReadPG(connpg,cursorpg,"select column_name,ordinal_position,data_type,character_maximum_length from information_schema.columns "+
        #                   "where table_schema = 'public' and table_name = '"+table_names[i][0]+"' order by ordinal_position asc")
        #statement = ReadPG(connpg,cursorpg,"select generate_create_table_statement('"+table_names[i][0]+"')")
        print(statement)
    '''
    
    '''
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
                     sql_state[i][1]+"','"+fields+"')")
            WriteSQL("insert or replace into mastdbtbls values('"+file+"','"+
                    sql_state[i][0]+"','"+sql_state[i][1]+"','"+fields+"',null)")
        WriteSQL("commit")
        WriteSQL("detach database DB")
    else:
        ctypes.windll.user32.MessageBoxW(0,temp00+" does not exist?","",1)
    '''
    connpg.close()

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def get_primary_key(cursor):
    tblpkey = []
    pkey_grab = cursor.execute("""select tc.table_schema, tc.table_name, kc.column_name from information_schema.table_constraints 
    tc join information_schema.key_column_usage kc on kc.table_name = tc.table_name and kc.table_schema = tc.table_schema and 
    kc.constraint_name = tc.constraint_name where tc.constraint_type = 'PRIMARY KEY' and kc.ordinal_position is not null
    order by tc.table_schema, tc.table_name, kc.position_in_unique_constraint;""")
    pkey_grab = cursor.fetchall()

    for i in pkey_grab:
        if "public" in str(i[0]):
            pkey_tbl = str(i[1])
            pkey = str(i[2])
            tblpkey.append(pkey_tbl+"|"+pkey)

    all_tbls = cursor.execute("""SELECT * FROM information_schema.tables""")
    all_tbls = cursor.fetchall()

    tbl_pkey_q = []
    for i2 in all_tbls:
        if "public" in str(i2[1]):
            tbl_name = i2[2]
            all_pkeys = ""
            for row in tblpkey:
                ind = str(row).index("|")
                pkey_tblname = str(row)[0:ind]
                pkey = str(row)[ind+1:]
                if tbl_name == pkey_tblname:
                    #print(tbl_name)
                    all_pkeys+=pkey+','
            all_pkeys = tbl_name+"|"+all_pkeys[0:-1]
            if len(all_pkeys) > len(tbl_name)+1:
                tbl_pkey_q.append(all_pkeys)

    #print(tbl_pkey_q[0])
    #print(len(tbl_pkey_q))
    return (tbl_pkey_q)

def get_foreign_key(cursor):
    fkeyreftbl = []
    cursor.execute("""select col.table_schema || '.' || col.table_name as table,
           col.ordinal_position as col_id,
           col.column_name,
           case when kcu.constraint_name is not null then '>-'
                else null
           end as rel,
           rel.table_name as primary_table,
           rel.column_name as primary_column,
           kcu.constraint_name 
    from information_schema.columns col
    left join (select kcu.constraint_schema, 
                      kcu.constraint_name, 
                      kcu.table_schema,
                      kcu.table_name, 
                      kcu.column_name, 
                      kcu.ordinal_position,
                      kcu.position_in_unique_constraint
               from information_schema.key_column_usage kcu
               join information_schema.table_constraints tco
                    on kcu.constraint_schema = tco.constraint_schema
                    and kcu.constraint_name = tco.constraint_name
                    and tco.constraint_type = 'FOREIGN KEY'
              ) as kcu
              on col.table_schema = kcu.table_schema
              and col.table_name = kcu.table_name
              and col.column_name = kcu.column_name
    left join information_schema.referential_constraints rco
              on rco.constraint_name = kcu.constraint_name
              and rco.constraint_schema = kcu.table_schema
    left join information_schema.key_column_usage rel
              on rco.unique_constraint_name = rel.constraint_name
              and rco.unique_constraint_schema = rel.constraint_schema
              and rel.ordinal_position = kcu.position_in_unique_constraint
    where col.table_schema not in ('information_schema','pg_catalog')
    order by col.table_schema,
             col.table_name,
             col_id;""")

    for i in cursor.fetchall():
        if "public." in str(i[0]):
            if ">-" in str(i[3]):
                main_tbl = str(i[0]).replace("public.","")
                fkey = replace_all(str(i[6]),{main_tbl+"_":"","_fkey":""})
                ref_tbl = str(i[4])
                ref_rec = str(i[5])
                fkeyreftbl.append(main_tbl+"-"+fkey+"|"+ref_tbl+"-"+ref_rec)

    #print(fkeyreftbl[0])
    #print(len(fkeyreftbl))
    return(fkeyreftbl)

def get_columns(cursor):
    cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';""")
    tblcol = []
    for i in cursor.fetchall():
        tbl = str(i[0])
        cursor.execute("""SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns
        WHERE table_name = '{t}' AND table_schema = 'public';""".format(t=tbl))
        for col in cursor.fetchall():
            col = list(col)
            col = tuple(col)
            col_n_type = replace_all(str(col[:2]),{"'":"","(":"",")":"",",":"",
                                               "character varying":"varchar("+str(col[2])+")"})
            tblcol.append(tbl+"|"+col_n_type)

    all_tbls = cursor.execute("""SELECT * FROM information_schema.tables""")
    all_tbls = cursor.fetchall()

    col_q = []
    for i2 in all_tbls:
        if "public" in str(i2[1]):
            tbl_name = i2[2]
            all_cols = ""
            for row in tblcol:
                ind = str(row).index("|")
                stan_tblname = str(row)[0:ind]
                stan_col = str(row)[ind+1:]
                if tbl_name == stan_tblname:
                    all_cols+=stan_col+','
            all_cols = tbl_name+"|"+all_cols[0:-1]
            col_q.append(all_cols)   
    #print(col_q[0])
    #print(len(col_q))
    return(col_q)

def getFields(connection,cur,table_name):
    if table_name[-1:]=="\"" and table_name[:1]=="\"":
        table_name = table_name[1:-1]
    tables = ReadPG(connection,cur,"select column_name from information_schema.columns where "+
                    "table_schema = 'public' and table_name = '"+str(table_name)+
                    "' order by ordinal_position asc")
    val = ""
    for i in range(len(tables)):
        val += tables[i][0]+","
    if len(val)>0:
        val = val[:-1]
    return(val)

result = ctypes.windll.user32.MessageBoxW(0,"Confirm (re)population of\nmasttbls & mastdbtbls?","Warning",4)
if result==6:
    WriteSQL("delete from pgtables")
    all_dbs = ReadSQL("select * from pgmaster")
    for i in range(len(all_dbs)):
        writeTable(all_dbs[i][0],all_dbs[i][1],all_dbs[i][2],all_dbs[i][3],all_dbs[i][4])

# Disconnect from DB
connection.close(True)


