from array import array
from asyncio.log import logger
from pathlib import Path
from sqlalchemy import insert, delete, update, select, and_, or_, not_, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey
from .__orm import *
import typing

  



class DBHandler:
    def __init__(self, db_loc:Path):
        db_url = URL(drivername='sqlite', database=db_loc.__str__())  # type: ignore #convert db_loc to string here because sqlalchemy doesnt handle Path objects :\
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)
    
    def writesql(self, queries):
        if type(queries) is not list:
            queries = [queries]

        with self.session_factory.begin() as sess:
                for query in queries:
                    #log query
                    try:
                        #self.logger.info(query.compile(dialect=self.engine.dialect)))
                        sess.execute(query).all()
                    except Exception as e:
                        if "result object does not return rows." not in str(e):
                            logger.error(e)
                sess.commit()
                return True

    #return either a dict or bool
    def readsql(self, query, one:bool=False) -> typing.Union[typing.Dict, bool]:
        try:
            x = self.session.execute(query).all()
            x = [dict(item._mapping) for item in x]
            self.session.commit()
            if one:
                return x[0] if len(x) > 0 else False
            return x if len(x) != 0 else False


        except Exception as e:
            if "result object does not return rows." not in str(e):
                self.session.rollback()
                return False    
            else:
                return True  

    def reconnect(self):
        self.session.close()
        self.session = scoped_session(self.session_factory)

    #close function
    def __del__(self):
        self.session.close()
        self.engine.dispose()

class gw_db(DBHandler):
    def __init__(self, db_loc:Path):
        self.check_db_exists(db_loc)
        super().__init__(db_loc)
        self.query = self.session.query
        self.check_tables_exist()

    def check_db_exists(self, path:Path) -> bool:
        if not path.exists():
            path.touch()
        return True

    def check_tables_exist(self) -> bool:
        for table in tables:
            if not  self.engine.dialect.has_table(self.engine.connect(), table):
                curtable = eval(table)
                curtable.__table__.create(self.engine)
        return True
