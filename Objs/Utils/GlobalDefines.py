from collections import namedtuple
from enum import Enum
import math
from typing import List, Any

# TODO: Consider putting these settings in the DB or something? Not sure if necesssary...
MAXIMUM_RELATIVE_EVENT_WEIGHT = 5
WEIGHT_POWER = math.log(MAXIMUM_RELATIVE_EVENT_WEIGHT, 2)
# Not a strict meguca limit or anything, but calibrates things like the chance of a meguca being a friend with an already
# existing meguca.
MEGUCA_POPULATION = 100

# Initial megucas (potential, contracted, witch, dead)
INITIAL_MEGUCA_POPULATION = (12, 12, 12, 12)

# Chance of decay based on potential. 1 in 6 for potential 5 and 5 in 6 for potential 1, multiplied by this value.
POTENTIAL_DECAY_RATE = 0.1  

# Represents a valid affinity type in sqlite3; used to describe column affinities for attempted coercion.
class SqliteAffinityType(Enum):
    TEXT = 1
    NUMERIC = 2
    INTEGER = 3
    REAL = 4
    NONE = 5    

# A simple table that indicates whether or not a game is running. If an entry exists at all, a game is running.
RUNNING_TABLE_NAME = "FarmingGameRunning"

RUNNING_TABLE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),)

RUNNING_PRIMARY_KEYS = [x[0] for x in RUNNING_TABLE_FIELDS if x[2]]                  
                       
RUNNING_ROW = namedtuple("RUNNING_ROW", [x[0] for x in RUNNING_TABLE_FIELDS]) 

# The voting/event information table.
VOTING_TABLE_NAME = "VoteEventTable"

# OutputText is returned with the most recent text last.
VOTING_TABLE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),
                       ("TimestampString", SqliteAffinityType.TEXT, True),
                       ("OutputText", SqliteAffinityType.TEXT, False), # serialized json list of strings
                       ("VotableOptions", SqliteAffinityType.TEXT, False), # serialized json list of strings
                       ("VoteResultInteger", SqliteAffinityType.INTEGER, False),
                       ("MostRecentEvent", SqliteAffinityType.TEXT, False))

VOTING_PRIMARY_KEYS = [x[0] for x in VOTING_TABLE_FIELDS if x[2]]                  
                       
VOTING_ROW = namedtuple("VOTING_ROW", [x[0] for x in VOTING_TABLE_FIELDS]) 
    
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

# Table of energy changes
ENERGY_CHANGES = {
"BODY_KILLED": -10,
"NEW_WITCH": 10,  # per level of potential.
"NEW_CONTRACT": 1,  # per level of potential
}