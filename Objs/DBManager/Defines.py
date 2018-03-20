from Objs.Utils.GlobalDefines import *

EXCEPTION_TABLE_NAME = "PythonGameError"

EXCEPTION_TABLE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),
                          ("IsError", SqliteAffinityType.INTEGER, False),
                          ("ErrorText", SqliteAffinityType.TEXT, False))