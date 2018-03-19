from functools import wraps
from typing import Any
import sqlite3



# TODO: Use this to write an Exception if anything in the main fails?

# This class handles reading and writing data to the sqlite3 db for the Incubator Farming game.
# It has the following properties:
# 1) When created, it takes ownership of a Connection object to the database. Do not make more than one object for the same db unless you want trouble.
# 2) "Writes" to the db are not actually executed until the db is committed (which must be done MANUALLY).
# 3) If during commitment, it discovers that one of the behavior flags has been violated, it will refuse to make any changes and raise an Exception instead,
#    writing only to a special exception table.
# 4) When asked for data, the user must provide the table name to the keyword "table" and behavior flags for the expected use of the data
#    to the string argument read_flag
#    a) read_only -> the user will not make any changes to this table. Any attempts to write to this table (unless another read is carried out) will be rejected.
#    b) may_be_modified -> the most permissive. The user may queue writes or not.
#    c) expected_modification -> the db will refuse finalization unless a write back to this table has been carried out.
# 5) When writing, the user must provide the table name to the keyword "table" and the keyword flag forced may be set to True, which will bypass all checks. Use with care.

# This class is paranoid, rather than robust - it raises or allows Exceptions rather than attempting to work its way around.

# This class will execute write statements in the order they were provided. As such, it is not robust to write commands provided in illogical order. Since
# Python connection is deliberately not thread-safe (and will in fact raise and Exception), neither is this object.
class DBManager:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.valid_write_tables = set()
        self.must_write_tables = set()
        self.written_tables = set()
        self.statement_queue = []    
        
    def __del__(self):
        self.connection.close()        
    
    # TODO: Change these exceptions to be a bit more informative.
    @staticmethod
    def read_method(input_func)
        def output_func(self, *args, **kwargs):
            if "read_flag" not in kwargs:
                self.WriteExceptionState("read_flag argument must be set!")
                raise Exception("read_flag argument must be set!")
            if "table" not in kwargs:
                self.WriteExceptionState("table must be set!")
                raise Exception("table must be set!")
            flag = kwargs["read_flag"]
            table = kwargs["table"]
            if flag == "read_only":
                pass
            elif flag == "may_be_modified":
                self.valid_write_tables.add(table)
            elif flag == "expected_modification":
                self.valid_write_tables.add(table)
                self.must_write_tables.add(table)
            else:
                self.WriteExceptionState("read_flag is not valid!")
                raise Exception("read_flag is not valid!")
            return input_func(self, *args, **kwargs)
        return wraps(input_func)(output_func)
        
    @staticmethod
    def write_method(input_func):
        def output_func(self, *args, **kwargs):
            if "table" not in kwargs:
                self.WriteExceptionState("table must be set!")
                raise Exception("table must be set!")
            if not kwargs.get("forced", False):
                if kwargs["table"] not in self.valid_write_tables:
                    self.WriteExceptionState("table not valid write table!")
                    raise Exception("table not valid write table!")
            return input_func(self, *args, **kwargs)
        return wraps(input_func)(output_func)
    
    def WriteExceptionState(self, exception_text: str):
        pass
    
    def Commit(self):
        # Behavior Checking 
        if not self.must_write_tables.issubset(self.written_tables):
            not_written = self.must_write_tables - self.written_tables
            exception_str = "The following tables still need to be written to: " + str(not_written)
            self.WriteExceptionState(exception_str)
            raise Exception(exception_str)
        c = self.connection.cursor()
        for statement in self.statement_queue:
            c.execute(statement)
        self.connection.commit()
        