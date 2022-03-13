PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS modifierfib(brokerid char(10) NOT NULL,acctnum INTEGER NOT NULL,sym CHAR(20) NOT NULL,zone CHAR(63) NOT NULL,strategy CHAR(24) NOT NULL,timestamp DATETIME,swing INTEGER,swingtype CHAR(63),swinglvl DOUBLE,swingprice DOUBLE,activeswing DOUBLE,PRIMARY KEY(brokerid,acctnum,sym,zone,strategy)); PRAGMA foreign_keys = on;

CREATE TABLE IF NOT EXISTS modifierfibdet(brokerid CHAR(10) NOT NULL,acctnum INTEGER NOT NULL,sym CHAR(20) NOT NULL,zone CHAR(63) NOT NULL,strategy CHAR(24) NOT NULL,timestamp DATETIME,swing INTEGER,swingtype CHAR(63),swinglvl DOUBLE NOT NULL,swingprice DOUBLE,PRIMARY KEY(brokerid,acctnum,sym,zone,strategy,swinglvl)); PRAGMA foreign_keys = on;

ALTER TABLE zonesalgoeye RENAME TO _zonesalgoeye_old;

CREATE TABLE zonesalgoeye

(brokerid CHAR(10) NOT NULL,acctnum INTEGER NOT NULL,sym CHAR(20) NOT NULL,zone CHAR(63) NOT NULL,highwinks INTEGER,highstamp DATETIME,highprice DOUBLE,lowwinks INTEGER,lowstamp DATETIME,lowprice DOUBLE,server CHAR(15),datapath CHAR(255),PRIMARY KEY(brokerid,acctnum,sym,zone));

INSERT INTO zonesalgoeye(brokerid,acctnum,sym,zone,highwinks,highstamp,highprice,lowwinks,lowstamp,lowprice,server,datapath)

SELECT brokerid,acctnum,sym,zone,highwinks,highstamp,highprice,lowwinks,lowstamp,lowprice,server,datapath

FROM _zonesalgoeye_old;

DROP TABLE _zonesalgoeye_old;

ALTER TABLE zonesalgoeyehis RENAME TO _zonesalgoeyehis_old;

CREATE TABLE zonesalgoeyehis

(brokerid CHAR(10) NOT NULL,acctnum INTEGER NOT NULL,sym CHAR(20) NOT NULL,zone CHAR(63) NOT NULL,highwinks INTEGER,highstamp DATETIME,highprice DOUBLE,lowwinks INTEGER,lowstamp DATETIME,lowprice DOUBLE,server CHAR(15),datapath CHAR(255),PRIMARY KEY(brokerid,acctnum,sym,zone));

INSERT INTO zonesalgoeyehis(brokerid,acctnum,sym,zone,highwinks,highstamp,highprice,lowwinks,lowstamp,lowprice,server,datapath)

SELECT brokerid,acctnum,sym,zone,highwinks,highstamp,highprice,lowwinks,lowstamp,lowprice,server,datapath

FROM _zonesalgoeyehis_old;

DROP TABLE _zonesalgoeyehis_old;

ALTER TABLE zonespricedelay RENAME TO _zonespricedelay_old;

CREATE TABLE zonespricedelay

(brokerid CHAR(10) NOT NULL,acctnum INTEGER NOT NULL,sym CHAR(20) NOT NULL,zone CHAR(63) NOT NULL,price DOUBLE,server CHAR(15),datapath CHAR(255),PRIMARY KEY(brokerid,acctnum,sym,zone));

INSERT INTO zonespricedelay(brokerid,acctnum,sym,zone,price,server,datapath)

SELECT brokerid,acctnum,sym,zone,price,server,datapath

FROM _zonespricedelay_old;

DROP TABLE _zonespricedelay_old;

ALTER TABLE zonesxy RENAME TO _zonesxy_old;

CREATE TABLE zonesxy

(brokerid CHAR(10) NOT NULL,acctnum INTEGER NOT NULL,sym CHAR(20) NOT NULL,zone CHAR(63) NOT NULL,time1 DATETIME,price1 DOUBLE,time2 DATETIME,price2 DOUBLE,server CHAR(15),datapath CHAR(255),PRIMARY KEY(brokerid,acctnum,sym,zone));

INSERT INTO zonesxy(brokerid,acctnum,sym,zone,time1,price1,time2,price2,server,datapath)

SELECT brokerid,acctnum,sym,zone,time1,price1,time2,price2,server,datapath

FROM _zonesxy_old;

DROP TABLE _zonesxy_old;

COMMIT;

PRAGMA foreign_keys=on;



