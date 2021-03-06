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
        self.truth_level = self.GetParsedDataOrDefault("TruthLevel", 0)
        self.energy_accumulated = self.GetParsedDataOrDefault("EnergyAccumulated", 0)
        self.current_phase = self.GetParsedDataOrDefault("CurrentPhase", "INITIAL")
        self.event_data = {}
    
    def ChangeTruth(self, change: float) -> None:
        self.truth_level = min(max(self.truth_level + change, 0), 1)
    
    # Return value indicates whether we've hit Incubator bankruptcy.
    def ChangeEnergy(self, change: int, forced: bool=False) -> bool:
        is_valid = (change > -self.energy_accumulated)
        if not is_valid and not forced:
            return False
        self.energy_accumulated = max(self.energy_accumulated + change, 0)
        return is_valid
    
    def ChangeSensors(self, sensor_type: str, increment: int):
        curlevel = self.sensors[sensor_type]
        self.sensors[sensor_type] = min(max(curlevel, MEGUCA_STATS[sensor_type].full_range[0]),  MEGUCA_STATS[sensor_type].full_range[1])
    
    def CheckSensorIsMax(self, sensor_type: str):
        return MEGUCA_STATS[sensor_type].full_range[1] == self.sensors[sensor_type]
   
    def GetEventData(self, event_name: str):
        event_data = self.event_data.get(event_name, None)
        if event_data is None:
            # Try getting it from table instead
            event_data = self.GetParsedDataOrDefault(event_name, None)
            if event_data is None:
                event_data = {}
            self.event_data[event_name] = event_data
        return event_data
    
    def GetEventDone(self, event_name: str):
        assert("." in event_name)  # covers a common programming error elsewhere. Awkward.
        event_data = self.GetEventData(event_name)
        done = event_data.get("Done", None)
        if done is None:
            # Only run this after running the event once.
            # single-stage events have stage=0 but are always done.
            # multi-stage events are done if their stage have cycled around to 0
            # events can also provide their own value optionally.
            return (self.GetEventStage(event_name) == 0)
        return done
    
    # If you use this, make sure you set it to False or True in every return path.
    def SetEventDone(self, event_name: str, done: bool):
        self.GetEventData(event_name)["Done"] = done
    
    def GetEventStage(self, event_name: str):
        event_data = self.GetEventData(event_name)
        stage =  event_data.get("Stage", None)
        if stage is None:
            event_data["Stage"] = 0
            stage = 0
        return stage
        
    def SetEventStage(self, event_name: str, stage: int):
        self.GetEventData(event_name)["Stage"] = stage
        
    def IncrementEventStage(self, event_name: str, last_stage: int):
        event_data = self.GetEventData(event_name)
        stage =  event_data.get("Stage", 0)
        event_data["Stage"] = (stage + 1) % (last_stage + 1)
        
    def GetAndIncrementEventStage(self, event_name: str, last_stage: int):
        event_data = self.GetEventData(event_name)
        stage =  event_data.get("Stage", 0)
        event_data["Stage"] = (stage + 1) % (last_stage + 1)
        return stage
     
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
                      (STATE_ROW(self.city_id, "targets", json.dumps(self.targets)), True),
                      frozenset((self.city_id, "CurrentPhase")):
                      (STATE_ROW(self.city_id, "CurrentPhase", json.dumps(self.current_phase)), True),
                      frozenset((self.city_id, "TruthLevel")):
                      (STATE_ROW(self.city_id, "TruthLevel", json.dumps(self.truth_level)), True),
                      frozenset((self.city_id, "EnergyAccumulated")):
                      (STATE_ROW(self.city_id, "EnergyAccumulated", json.dumps(self.energy_accumulated)), True)}
        for event_name, event_data in self.event_data.items():
            write_dict[frozenset((self.city_id, event_name))] = (STATE_ROW(self.city_id, event_name, json.dumps(event_data)), True)
        self.manager.WriteTable(write_dict, [x[0] for x in STATE_TABLE_FIELDS], table=STATE_TABLE_NAME)