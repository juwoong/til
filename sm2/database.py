import sqlite3
from libs.parse_tables import parse_create_tables
import typing as t

class Database: 
    version: int = 1

    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.init()


    @staticmethod
    def _load_sqls(file_name) -> t.List[str]:
        with open(file_name) as f:
            result = f.read()
        
        if result is None:
            return []
        
        return parse_create_tables(result)


    def init(self):
        sqls = self._load_sqls('sql/content.sql')

        for sql in sqls:
            self.conn.execute(sql)

        self.conn.commit()
        print(f"Database initialized with {len(sqls)} tables.")

