from asyncore import read
from sys import prefix
from __important.PluginInterface import PluginInterface
from sqlalchemy import insert, select, or_, text, engine
import psycopg2
from backend.db.Exaut_sql import *
import shutil
import os
class createpg(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "createpg","alterpg"
    hooks_handler = ["log"]
    hooks_method = ["writesql", "readsql"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def load_self_methods(self, hooks):
        self.writesql = hooks["writesql"].main
        self.readsql = hooks["readsql"].main


    def WritePG(self,query,attempts=12,sec=1,box=False):
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e4:
            print(query)
            print(str(e4))
            self.conn.rollback()

    def ReadPG(self,query,attempts=12,sec=1):
        val = []
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            for result in results:
                val.append(list(result))
            return(val)
        except Exception as e4:
            print(query)
            print(str(e4))
            return(val)


    def main(self, folderpath,filename,type_,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,bname) -> bool:    

            if str(source)=="" or source==None:
                self.Popups.alert("No Postgres credentials specified in source field.","Failed "+str(type_)+": "+bname+"! \\"+str(runsequence))
            elif str(target)=="" or target==None:
                self.Popups.alert("No Postgres credentials specified in target field.","Failed "+str(type_)+": "+bname+"! \\"+str(runsequence))
            else:
                pg_data_src = str(source)
                pg_data_src = pg_data_src.split('|')
                pg_data_trg = str(target)
                pg_data_trg = pg_data_trg.split('|')
                self.conn = psycopg2.connect(dbname=pg_data_trg[0],user=pg_data_trg[1],password=self.variables["pg_pass"],host=pg_data_trg[2],port=pg_data_trg[3])
                self.cursor = self.conn.cursor()
                statements = self.readsql(select(pgtables).where(pgtables.hostip == str(pg_data_src[2])).where(pgtables.port == str(pg_data_src[3])).where(pgtables.username == str(pg_data_src[1])).where(pgtables.password == str(pg_data_src[4])).where(pgtables.dbname == str(pg_data_src[0])))
                statements = [dict(item._mapping) for item in statements]
                warning = ""
                
                if str(type_)=="alterpg":
                    self.WritePG("begin transaction")
                    all_tables = self.ReadPG("select table_name from information_schema.tables where table_schema = 'public'")
                    all_table_names = []
                    for i in range(len(all_tables)):
                        all_table_names.append(str(all_tables[i][0]))
                        all_constraints = self.ReadPG("select constraint_name from information_schema.table_constraints where table_schema = 'public' and table_name = '"+
                                                        str(all_tables[i][0])+"' and (constraint_type = 'FOREIGN KEY' or constraint_type = 'PRIMARY KEY')")
                        for j in range(len(all_constraints)):
                            self.WritePG("alter table "+str(all_tables[i][0])+" drop constraint if exists "+str(all_constraints[j][0])+" cascade")
                    self.WritePG("commit")
                    self.WritePG("begin transaction")
                    for i in range(len(statements)):
                        if statements[i][5][:1]=="\"" and statements[i][5][-1:]=="\"":
                            temp = str(statements[i][5][1:-1])
                        else:
                            temp = str(statements[i][5])
                        if all_table_names.count("_"+temp+"_old")<1:
                            self.WritePG("alter table if exists "+str(statements[i][5])+" rename to _"+temp+"_old")
                    self.WritePG("commit")
                creation = statements
                self.WritePG("begin transaction")
                while len(creation)>0:
                    references = creation[0][6].split("REFERENCES ")
                    if len(references)>1:
                        all_exist = True
                        references.pop(0)
                        for t in range(len(references)):
                            table_ref = references[t].split('(')[0]
                            does_exist = self.ReadPG("select table_name from information_schema.tables where table_schema = 'public' and table_name = '"+str(table_ref)+"'")
                            if len(does_exist)<1:
                                all_exist = False
                                creation.append(creation[0])
                                creation.pop(0)
                                break
                        if all_exist==True:
                            self.WritePG(creation[0][6])
                            creation.pop(0)
                    else:
                        self.WritePG(creation[0][6])
                        creation.pop(0)
                self.WritePG("commit")

                statements = self.readsql(select(pgtables).where(pgtables.hostip == str(pg_data_src[2])).where(pgtables.port == str(pg_data_src[3])).where(pgtables.username == str(pg_data_src[1])).where(pgtables.password == str(pg_data_src[4])).where(pgtables.dbname == str(pg_data_src[0])))
                statements = [dict(item._mapping) for item in statements]
                if str(type_)=="alterpg":
                    self.WritePG("begin transaction")
                    for i in range(len(statements)):
                        is_fk = statements[i][6].lower()
                        if is_fk.find('foreign key')==-1:
                            if statements[i][5][:1]=="\"" and statements[i][5][-1:]=="\"":
                                temp = str(statements[i][5][1:-1])
                            else:
                                temp = str(statements[i][5])
                            if statements[i][7]!=None:
                                self.WritePG("insert into "+str(statements[i][5])+"("+str(statements[i][7])+") select "+str(statements[i][7])+
                                                " from _"+temp+"_old")
                            if statements[i][8]!=None and statements[i][8]!="" and statements[i][8]!="None":
                                statements[i][8] = str(statements[i][8])
                                self.WritePG(str(statements[i][8]))
                            old_cnt = self.ReadPG("select count(*) from _"+temp+"_old")
                            new_cnt = self.ReadPG("select count(*) from "+str(statements[i][5]))
                            if len(old_cnt)>0 and len(new_cnt)>0:
                                if new_cnt[0][0]<=0 and old_cnt[0][0]>0:
                                    warning += str(target)+": Failed to copy data from _"+temp+"_old to "+str(statements[i][5])+"\n"
                                else:
                                    self.WritePG("drop table if exists _"+temp+"_old")
                            else:
                                self.WritePG("drop table if exists _"+temp+"_old")
                    for i in range(len(statements)):
                        is_fk = statements[i][6].lower()
                        if is_fk.find('foreign key')>=0:
                            if statements[i][5][:1]=="\"" and statements[i][5][-1:]=="\"":
                                temp = str(statements[i][5][1:-1])
                            else:
                                temp = str(statements[i][5])
                            if statements[i][7]!=None:
                                self.WritePG("insert into "+str(statements[i][5])+"("+str(statements[i][7])+") select "+str(statements[i][7])+
                                                " from _"+temp+"_old")
                            if statements[i][8]!=None and statements[i][8]!="" and statements[i][8]!="None":
                                statements[i][8] = str(statements[i][8])
                                self.WritePG(str(statements[i][8]))
                            old_cnt = self.ReadPG("select count(*) from _"+temp+"_old")
                            new_cnt = self.ReadPG("select count(*) from "+str(statements[i][5]))
                            if len(old_cnt)>0 and len(new_cnt)>0:
                                if new_cnt[0][0]<=0 and old_cnt[0][0]>0:
                                    warning += str(target)+": Failed to copy data from _"+temp+"_old to "+str(statements[i][5])+"\n"
                                else:
                                    self.WritePG("drop table if exists _"+temp+"_old")
                            else:
                                self.WritePG("drop table if exists _"+temp+"_old")
                    self.WritePG("commit")
                #if str(type_)=="alterdb":
                #    self.WritePG("vacuum")
                self.conn.close()
