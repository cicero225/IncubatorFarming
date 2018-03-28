from collections import namedtuple

from Objs.Utils.GlobalDefines import *

VOTE_TABLE_NAME = "VotesTable"

# Tuple of tuples, where the inner tuples are (name, type and is_primary_key)
VOTE_TABLE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),
                     ("CurrentEvent", SqliteAffinityType.TEXT, False),      # The event the vote is a part of
                     ("EventSubIndex", SqliteAffinityType.INTEGER, False),  # In case for events with multiple stages, this indicates the stage
                     ("VoteResult", SqliteAffinityType.INTEGER, False))     # The result of the vote (as an index of the given vote options)


GAME_EVENTS_STATE_TABLE = "GameEventsState"

GAME_EVENTS_STATE_FIELDS = (("CityID", SqliteAffinityType.INTEGER, True),
                            ("IsMostRecentEvent", SqliteAffinityType.INTEGER, False),  # A boolean that indicates whether or not the event is the most recent one
                            ("EventName", SqliteAffinityType.TEXT, False),             # The event
                            ("EventDisplayName", SqliteAffinityType.TEXT, False),      # The name of event to display
                            ("EventSubIndex", SqliteAffinityType.INTEGER, False),      # In case for events with multiple stages, this indicates the stage
                            ("OutputText", SqliteAffinityType.TEXT, False),            # The text that will be displayed to the players
                            ("VoteableOptions", SqliteAffinityType.TEXT, False),       # The actions the players can take
                            ("Timestamp", SqliteAffinityType.TEXT, False))             # The time in which the event was played


