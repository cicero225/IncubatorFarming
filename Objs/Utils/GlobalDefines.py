from enum import Enum
from typing import List, Any

# Represents a valid affinity type in sqlite3; used to describe column affinities for attempted coercion.
class SqliteAffinityType(Enum):
    TEXT = 1
    NUMERIC = 2
    INTEGER = 3
    REAL = 4
    NONE = 5    

# Hopefully not too big, just used to define how stats work with relation to sensors.
class SensorBehavior:
    def __init__(self, full_range, sensor_range: List[int], default_visible: bool, targetable: bool, optimum = None):
        self.full_range = full_range
        self.sensor_range = sensor_range  # set -1 if no range.
        self.sensor_depth = len(sensor_range)
        self.default_visible = default_visible
        self.targetable = targetable
        if not self.targetable:
            assert(optimum is not None)
            self.optimum = optimum

# Also needed by sensors, so this is a broad-reaching dict.
MEGUCA_STATS = {"potential": SensorBehavior((1, 5), (-1, 2, 0), True, True),
                "neuroticism": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "friendships": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "gullibility": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "secretiveness": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "bravery": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "cleverness": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "narcissism": SensorBehavior((1, 5), (-1, 1, 0), False, True),
                "aggression": SensorBehavior((1, 5), (-1, 1, 0), False, True)}
                
WISH_TYPES = ("healing", "revenge",  "wealth", "friends", "romance")