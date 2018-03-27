from enum import Enum
import math
from typing import List, Any

# TODO: Consider putting these settings in the DB or something? Not sure if necesssary...
MAXIMUM_RELATIVE_EVENT_WEIGHT = 5
WEIGHT_POWER = math.log(MAXIMUM_RELATIVE_EVENT_WEIGHT, 2)


# Represents a valid affinity type in sqlite3; used to describe column affinities for attempted coercion.
class SqliteAffinityType(Enum):
    TEXT = 1
    NUMERIC = 2
    INTEGER = 3
    REAL = 4
    NONE = 5    

# Hopefully not too big, just used to define how stats work with relation to sensors.
class SensorBehavior:
    """
    The players use the sensor to find girls. The sensor can pick up several stats, and can be upgraded to find
    girls with better stats (upgrades are separate for each stat).
    """

    def __init__(self, full_range, sensor_range: List[int], default_visible: bool, targetable: bool, optimum = None):
        """
        :param full_range: The full range of the stat
        :param sensor_range: How good the sensor is at showing the stat, depending on the sensor's level.
            * -1 = Stat is completely randomized and undisplayed.
            * 1 = The sensor will only show girls with stat that is 1 away from the optimum
                   (if optimum is 4 than it will only show girls with 3, 4, or 5 in the selected stat)
            * 0 = The scanner only shows girls with the optimal value for the stat.
        :param default_visible: Visible no matter what the sensor level
        :param targetable: This field can be targeted by the players.
        :param optimum: The "Optimal" value of the stat. Bigger/Smaller stats are not necessarily better, it depends on the optimum.
        """
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
