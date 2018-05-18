from collections import namedtuple

from Objs.Utils.GlobalDefines import *

# This defines the IncubatorFarmingGameState table and table row format.
STATE_TABLE_NAME = "IncubatorFarmingGameState"

STATE_TABLE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),
                      ("EntryName", SqliteAffinityType.TEXT, True),
                      ("EntryData", SqliteAffinityType.TEXT, False))  # Serialized Json

STATE_PRIMARY_KEYS = [x[0] for x in STATE_TABLE_FIELDS if x[2]]                  
                       
STATE_ROW = namedtuple("STATE_ROW", [x[0] for x in STATE_TABLE_FIELDS])