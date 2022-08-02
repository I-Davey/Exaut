"""
Here is an interface for Plugin classes.
"""
import re
from .MethodInterface import MethodInterface


class readsql(MethodInterface):

    load = True
    hooks = ["Sqlite", "log"]
    types = {"queries":object}
    
    
    def load_self(self, hooks):
        self.logger = hooks["log"]
        self.session = hooks["Sqlite"].session
        self.tables = hooks["Sqlite"].tables
        return True

    def main(self, query) -> bool:
        with self.session.begin() as session:
            try:
                x = session.execute(query).all()
                x = [dict(item._mapping) for item in x]
                return x

            except Exception as e:
                if "result object does not return rows." not in str(e):
                    self.logger.error(e)
                    return False      
        

            
