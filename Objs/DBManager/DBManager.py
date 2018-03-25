from functools import wraps
from typing import Any, List, Dict
import sqlite3

from Objs.Utils.GlobalDefines import *
from Objs.DBManager.Defines import *

def read_method(input_func):
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
            self.WriteExceptionState("read_flag " + str(flag) + " is not valid!")
            raise Exception("read_flag " + str(flag) + " is not valid!")
        return input_func(self, *args, **kwargs)
    return wraps(input_func)(output_func)

# Holy shit Python why this.    
def write_method(default_forced=False):
    def wow_decorator(input_func):
        def output_func(self, *args, **kwargs):
            if "table" not in kwargs:
                self.WriteExceptionState("table must be set!")
                raise Exception("table must be set!")
            if not kwargs.get("forced", default_forced):
                if kwargs["table"] not in self.valid_write_tables:
                    self.WriteExceptionState("table " + kwargs["table"] + " not valid write table!")
                    raise Exception("table " + kwargs["table"] + " not valid write table!")
            return input_func(self, *args, **kwargs)
        return wraps(input_func)(output_func)
    return wow_decorator

    
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
    def __init__(self, city_id: int, db_path=":memory:"):
        self.db_path = db_path
        self.city_id = city_id
        self.connection = sqlite3.connect(db_path)
        self.valid_write_tables = set()
        self.must_write_tables = set()
        self.written_tables = set()
        self.statement_queue = []    
        self.CreateTableIfDoesNotExist(EXCEPTION_TABLE_FIELDS, table=EXCEPTION_TABLE_NAME)
        
    def __del__(self):
        self.connection.close()        
    
    # row_names is an iterable of tuples of (Column Name, SqliteAffinityType, Bool(is primary key?))
    # Note that this is a highly INSECURE call, since it uses the text in row_names and table directly as part of the call.
    # Name sanitization is its own adventure we won't be going through; suffice to say don't use this function
    # with user inputs, and ideally input only literal strings into the arguments.
    @write_method(default_forced=True)
    def CreateTableIfDoesNotExist(self, row_names, table):
        c = self.connection.cursor()
        sql_template_list = []
        primary_key_list = []
        sql_insert_list = [table]
        primary_insert_list = []
        for col_name, affinity, primary in row_names:
            sql_template_list.append("{} {}")
            sql_insert_list.extend([col_name, affinity.name])
            if primary is True:
                primary_key_list.append("{}")
                primary_insert_list.append(col_name)
        sql_template_list.append(" PRIMARY KEY (" + ", ".join(primary_key_list) + ")")
        sql_insert_list.extend(primary_insert_list)
        sql_string = "CREATE TABLE IF NOT EXISTS {} (" + ", ".join(sql_template_list) + ")"
        c.execute(sql_string.format(*sql_insert_list))
    
    # Pulls the contents of a sqlite3 table into a more familiar and convenient Python format.
    # For best performance (and verification), it expects the caller to know the structure of the table.
    # It is NOT the intention to support pulling arbitrarily structured tables.
    # row_namedtuple: a namedtuple class appropriate for this table
    # primary_key_names: a list of the names of the primary keys.
    # set_keys: Fields we want to select for (equivalent to WHERE key IS value)
    # Some arguments (at the end) must be named arguments for proper processing.
    # return value: A Dict of frozenset(primary_key_values) (row_namedtuple, bool), where bool will be used to indicate whether a row has 
    # been modified, if this table is being written to later.
    @read_method
    def ReadTable(self, row_namedtuple, primary_key_names: List[str], set_keys: Dict[str, Any]=None, *args, table: str, read_flag):
        if set_keys is None:
            set_keys = []
        c = self.connection.cursor()
        base_string = "SELECT * FROM {}".format(table)
        if set_keys:
            where_string = "WHERE "
            where_string_list = []
            for key, value in set_keys:
                where_string_list.append("{} IS ?".format(key))
            where_string += " AND ".join(where_string_list)
            base_string += where_string
        this_table = c.execute(base_string)
        return_dict = {}
        for row in this_table:
            new_entry = [None]*len(row_namedtuple._fields)
            primary_key_list = []
            for idx, col in enumerate(c.description):
                new_entry[row_namedtuple._fields.index(col[0])] = row[idx]
                if col[0] in primary_key_names:
                    primary_key_list.append(row[idx])
            return_dict[frozenset(primary_key_list)] = (row_namedtuple(*new_entry), False)
        return return_dict
   
    # As discussed in the class description, does not commit a write action until Commit() is called.
    # write_dict should be the same format as the output of ReadTable
    # field_names must be an object with order.
    @write_method()
    def WriteTable(self, write_dict, field_names, *args, table: str, forced=False):
        c = self.connection.cursor()
        sql_base_string = "INSERT OR REPLACE INTO {} (".format(table) + ", ".join(field_names) + ") VALUES ("
        for value in write_dict.values():
            if value[1]:
                sql_base_string += ", ".join(["?"]*len(field_names)) + ")"
                c.execute(sql_base_string, tuple(getattr(value[0], name) for name in field_names))
   
    def WriteExceptionState(self, exception_text: str, has_failed=True):
        c = self.connection.cursor()
        c.execute(
            "INSERT OR REPLACE INTO {} ({}, {}, {}) values (?, ?, ?)".format(
                EXCEPTION_TABLE_NAME, *(x[0] for x in EXCEPTION_TABLE_FIELDS)),
            (self.city_id, int(has_failed), exception_text))
        self.connection.commit()
    
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
        self.WriteExceptionState("", False)
        