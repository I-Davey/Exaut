from asyncore import write
from sqlalchemy import Column, Integer, String, func, and_, null, update

from sqlalchemy.orm import declarative_base
Base = declarative_base()

tables = ["forms", "tabs", "buttons", "batchsequence", "buttonseries", "pluginmap", "actions", "actions_categories", "variables"]


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
    #batchseqence runsequence can be null

    __tablename__ = 'batchsequence'
    formname = Column(String(63), primary_key=True)
    tab = Column(String(63), primary_key=True)
    buttonname = Column(String(63), primary_key=True)
    runsequence = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
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

#CREATE TABLE pluginmap (	plugin TEXT NOT NULL,	types TEXT NOT NULL,	color TEXT, 	color TEXT, "generated" INTEGER,	CONSTRAINT pluginmap_PK PRIMARY KEY (plugin),	CONSTRAINT pluginmap_UN UNIQUE (types));
class pluginmap(Base):
    __tablename__ = 'pluginmap' #unique constraint on plugin and types
    plugin = Column(String(63), primary_key=True)
    types = Column(String(63), primary_key=True)
    color = Column(String(63))
    color2 = Column(String(63))
    generated = Column(Integer)


    
class actions(Base):
    __tablename__ = 'actions'
    action = Column(String(63), primary_key=True)
    plugin = Column(String(63), primary_key=True)
    category = Column(String(63))
    sequence = Column(Integer, nullable=False)
    generated = Column(Integer)

#create table actions_categories category TEXT position INTEGER category_short TEXT
class actions_categories(Base):
    __tablename__ = 'actions_categories'
    category = Column(String(63), primary_key=True)
    #sequence not null
    sequence = Column(Integer, nullable=False)


#CREATE TABLE variables (	loc VARCHAR(63) NOT NULL,	form VARCHAR(63) NOT NULL, 	"key" VARCHAR(63) NOT NULL, 	value VARCHAR(255), location TEXT NOT NULL, 	PRIMARY KEY (loc, form, "key"));
class variables(Base):
    __tablename__ = 'variables'
    loc = Column(String(63), primary_key=True)
    form = Column(String(63), primary_key=True)
    key = Column(String(63), primary_key=True)
    value = Column(String(255))
    