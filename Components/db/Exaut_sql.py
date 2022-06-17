from csv import Dialect
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, func, and_, or_, select, update, insert, delete
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CreateTable



from sqlalchemy.orm import declarative_base
Base = declarative_base()



#forms ddl: CREATE TABLE forms(formname char (63),formdesc TEXT,primary key(formname));
class forms(Base):
    __tablename__ = 'forms'
    formname = Column(String(63), primary_key=True)
    formdesc = Column(String(255))


#tabs ddl: CREATE TABLE "tabs" ("formname" char (63),  "tab" char (63),  "tabsequence" INTEGER,  "grid" INTEGER,  "tabdesc" TEXT,  "treepath" CHAR (1023),  "tabgroup" CHAR (63),  "tabsize" INTEGER,  "taburl" TEXT,  PRIMARY KEY ("formname", "tab"));
class tabs(Base):
    __tablename__ = 'tabs'
    formname = Column(String(63), primary_key=True)
    tab = Column(String(63), primary_key=True)
    tabsequence = Column(Integer)
    grid = Column(Integer)
    tabdesc = Column(String(255))
    treepath = Column(String(1023))
    tabgroup = Column(String(63))
    tabsize = Column(Integer)
    taburl = Column(String(255))

#buttons ddl: CREATE TABLE buttons(formname char (63),tab char (63),buttonname char (63),buttonsequence INTEGER,columnnum INTEGER,buttondesc TEXT,buttongroup CHAR (63),active CHAR (63),treepath CHAR (1023),primary key(formname,tab,buttonname));
class buttons(Base):
    __tablename__ = 'buttons'
    formname = Column(String(63), primary_key=True)
    tab = Column(String(63), primary_key=True)
    buttonname = Column(String(63), primary_key=True)
    buttonsequence = Column(Integer)
    columnnum = Column(Integer)
    buttondesc = Column(String(255))
    buttongroup = Column(String(63))
    active = Column(String(63))
    treepath = Column(String(1023))



#CREATE TABLE batchsequence(formname char (63),tab char (63),buttonname char (63),runsequence INTEGER,folderpath char (1023),filename char (255),type char (63),source char (1023),target char (1023),databasepath char (1023),databasename char (255),keypath char (1023),keyfile char (255),treepath CHAR (1023),primary key(formname,tab,buttonname,runsequence));
class batchsequence(Base):
    __tablename__ = 'batchsequence'
    formname = Column(String(63), primary_key=True)
    tab = Column(String(63), primary_key=True)
    buttonname = Column(String(63), primary_key=True)
    runsequence = Column(Integer, primary_key=True)
    folderpath = Column(String(1023))
    filename = Column(String(255))
    type = Column(String(63))
    source = Column(String(1023))
    target = Column(String(1023))
    databasepath = Column(String(1023))
    databasename = Column(String(255))
    keypath = Column(String(1023))
    keyfile = Column(String(255))
    treepath = Column(String(1023))


#CREATE TABLE buttonseries(formname char(63),tab char(63),buttonname char(63),assignname char(63),runsequence INTEGER,primary key(formname,tab,buttonname,assignname,runsequence));
class buttonseries(Base):
    __tablename__ = 'buttonseries'
    formname = Column(String(63), primary_key=True)
    tab = Column(String(63), primary_key=True)
    buttonname = Column(String(63), primary_key=True)
    assignname = Column(String(63), primary_key=True)
    runsequence = Column(Integer, primary_key=True)

def queries():
    tab = "Builds_new_"
    form = "COPY"
    replace = batchsequence.filename
    oldtext = "PICAT_SGX.exe"
    newtext = "Exaut.exe"
    #for batchsequence in batchsequence.tab = tab and batchsequence.formname = form:
    #if replace is oldtext
    #replace = newtext

    query = update(batchsequence).where(and_(batchsequence.tab == tab, batchsequence.formname == form, batchsequence.filename == oldtext)).values(filename=newtext)
    #print query sql
    print(query.compile(compile_kwargs={"literal_binds": True}))

queries()

