"""
Here is an interface for Plugin classes.
"""
from .MethodInterface import MethodInterface


class writesql(MethodInterface):

    load = True
    hooks = ["Sqlite", "log"]
    types = {"queries":list|object}
    
    
    def load_self(self, hooks):
        self.logger = hooks["log"]
        self.session = hooks["Sqlite"].session
        self.tables = hooks["Sqlite"].tables
        self.engine = hooks["Sqlite"].engine

        return True

    def main(self, queries, log=False) -> bool:

        if type(queries) is not list:
            queries = [queries]

        with self.session.begin() as sess:
                for query in queries:
                    #log query
                    try:
                        #self.logger.info(query.compile(dialect=self.engine.dialect))
                        if log:
                            self.logger.info(query.compile(dialect=self.engine.dialect))
                        sess.execute(query).all()
                    except Exception as e:
                        if "result object does not return rows." not in str(e):
                            self.logger.error(e)
                            sess.rollback()
                            return False     
                sess.commit()
                return True


 


            


"""
from .MethodInterface import MethodInterface


class writesql(MethodInterface):

    load = True
    hooks = ["Sqlite", "log"]
    types = {"queries":list}
    
    
    def load_self(self, hooks):
        self.engine_data = hooks["Sqlite"].engine_data
        self.tables = hooks["Sqlite"].tables
        self.logger = hooks["log"]
        return True

    def main(self, queries) -> bool:
        sessionmaker, create_engine, floc = self.engine_data
        engine = create_engine(floc)
        session = sessionmaker(bind=engine)
        with session.begin() as s:
            try:
                for query in queries:
                    x = s.execute(query).all()
            except Exception as e:
                if "result object does not return rows." not in str(e):
                    self.logger.error(e)
                    s.rollback()
                    return False      
            s.commit()
            return True
                
    """
            