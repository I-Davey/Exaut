
CREATE TABLE IF NOT EXISTS strategyfib(swing INTEGER NOT NULL,strategy CHAR(24) NOT NULL REFERENCES strategy(strategy),PRIMARY KEY(swing,strategy)); PRAGMA foreign_keys = on;