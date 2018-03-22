from collections import namedtuple

from Objs.Utils.GlobalDefines import *

FIRST_NAME_POOL = {"Oriko", "Kirika", "Yuma", "Iroha", "Yachiyo", "Tsuruno"}

LAST_NAME_POOL = {"Mikuni", "Kure", "Chitose", "Tamaki", "Nanami", "Yui"}

EITHER_NAME_POOL = { 
"Kaname",
"Akemi",
"Miki",
"Sakura",
"Tomoe",
"Shizuki",
"Madoka",
"Homura",
"Sayaka",
"Kyouko",
"Mami",
"Hitomi"
}


# This defines the Meguca table and table row format.
MEGUCA_TABLE_NAME = "MagicalGirlsTable"

MEGUCA_TABLE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),
                       ("MagicalGirlID", SqliteAffinityType.INTEGER, True),
                       ("IsWitch", SqliteAffinityType.INTEGER, False),
                       ("IsContracted", SqliteAffinityType.INTEGER, False),
                       ("IsDead", SqliteAffinityType.INTEGER, False),
                       ("PersonalName", SqliteAffinityType.TEXT, False),
                       ("Surname", SqliteAffinityType.TEXT, False),
                       ("WishType", SqliteAffinityType.TEXT, False),
                       ("Stats", SqliteAffinityType.TEXT, False),  # Serialized Json
                       ("Friends", SqliteAffinityType.TEXT, False),  # Serialized Json
                       ("Family", SqliteAffinityType.TEXT, False))  # Serialized Json

MEGUCA_PRIMARY_KEYS = [x[0] for x in MEGUCA_TABLE_FIELDS if x[2]]                  
                       
MEGUCA_ROW = namedtuple("MEGUCA_ROW", [x[0] for x in MEGUCA_TABLE_FIELDS])