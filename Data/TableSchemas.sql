-- This sql file suffices to make the tables needed for this game; however this is mainly intended as
-- indirect documentation, as the code itself makes the tables if they're missing.

-- Error table containing the last fatal error encountered by the Python code. If everything was fine, IsError is 0.
CREATE TABLE IF NOT EXISTS PythonGameError (CityID INTEGER, IsError INTEGER, ErrorText TEXT,  PRIMARY KEY (CityID))

CREATE TABLE IF NOT EXISTS MagicalGirlsTable (CityID INTEGER, MagicalGirlID INTEGER, IsWitch, INTEGER, IsContracted INTEGER,
                                              IsDead INTEGER, PersonalName TEXT, Surname TEXT, WishType TEXT, Stats TEXT,
                                              Friends TEXT, Family TEXT, PRIMARY KEY(CityID, MagicalGirlID))

                                              CREATE TABLE IF NOT EXISTS IncubatorFarmingGameState (CityID INTEGER, EntryName TEXT, EntryData TEXT,                                                      PRIMARY KEY(CityID, EntryName))

CREATE TABLE IF NOT EXISTS FarmingGameRunning (CityID INTEGER, PRIMARY KEY(CityID))

CREATE TABLE IF NOT EXISTS VoteEventTable (CityID INTEGER, TimestampString TEXT, OutputText TEXT,
                                           VotableOptions TEXT, VoteResultInteger INTEGER,
                                           MostRecentEvent INTEGER, PRIMARY KEY(CityID, TimestampString))