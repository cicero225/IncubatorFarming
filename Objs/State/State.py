from Objs.DBManager.DBManager import DBManager
from Objs.Utils.GlobalDefines import *
from Objs.State.Defines import *
from typing import Any
import json

# This class holds game state unrelated to MegucaCity, storing the logic for storing it and retrieving it
# from DB. Note that WriteState must be called at some point or the DB will refuse to write; this class
# enforces its own rewriting back into the DB.

class State:
    def __init__(self, manager: DBManager):
        # Unlike MegucaCity, we rarely ever need more than a few rows of the state table, which means we 
        # can economize by only reading and writing some rows on demand. That is handled here.
        self.manager = manager
        self.city_id = self.manager.city_id
        self.manager.CreateTableIfDoesNotExist(STATE_TABLE_FIELDS, table=STATE_TABLE_NAME)
        self.sensors =  self.GetParsedDataOrDefault("sensors", {stat: 0 for stat in MEGUCA_STATS})
        self.targets =  self.GetParsedDataOrDefault("targets", {stat: 0 for stat in MEGUCA_STATS})
        self.event_data = {}
        
    def GetEventData(self, event_name: str):
        event_data = self.event_data.get(event_name, None)
        if event_data is None:
            # Try getting it from table instead
            event_data = self.GetParsedDataOrDefault(event_name, None)
            if event_data is None:
                event_data = {}
            self.event_data[event_name] = event_data
        return event_data
        
    def GetEventStage(self, event_name: str):
        return self.GetEventData(event_name).get("Stage",None)
        
    def SetEventStage(self, event_name: str, stage: int):
        self.GetEventData(event_name)["Stage"] = stage
     
    def GetDataForStateEntry(self, event_name: str):
        return self.manager.ReadTable(STATE_ROW, STATE_PRIMARY_KEYS,
                                      {"CityID": self.city_id, "EntryName": event_name},
                                      table=STATE_TABLE_NAME, read_flag="expected_modification")
    
    def GetParsedDataOrDefault(self, event_name: str, default):
        row = self.GetDataForStateEntry(event_name)
        if not len(row):
            return default
        elif len(row) == 1:
            for only_row in row.values():
                return json.loads(only_row[0].EntryData)
        else:
            raise AssertionError
                                      
    def WriteState(self):
        # We don't bother to check in detail whether these rows have changed, since this is a small
        # INSERT OR UPDATE anyway.
        write_dict = {frozenset((self.city_id, "sensors")):
                      (STATE_ROW(self.city_id, "sensors", json.dumps(self.sensors)), True),
                      frozenset((self.city_id, "targets")):
                      (STATE_ROW(self.city_id, "targets", json.dumps(self.targets)), True)}
        for event_name, event_data in self.event_data.items():
            write_dict[frozenset((self.city_id, event_name))] = (STATE_ROW(self.city_id, event_name, json.dumps(event_data)), True)
        self.manager.WriteTable(write_dict, [x[0] for x in STATE_TABLE_FIELDS], table=STATE_TABLE_NAME)