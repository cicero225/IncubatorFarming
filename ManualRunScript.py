"""Runs a command line version of the Incubator Farming game."""

import argparse

from Objs.Utils.GlobalDefines import *
from Objs.DBManager.DBManager import DBManager
from IncubatorFarming import Main

parser = argparse.ArgumentParser(description='Incubator Farming Manual Run Script')
parser.add_argument('city_id', type=int,
                    help='An id that defines the city for this run.')
parser.add_argument('db_path',
                    help='The location of the db file this game is stored in.')
parser.add_argument('--restart', action='store_true',
                    help='Dummy Argument for Manual Running, do not use.')
                    
                    
if __name__ == '__main__':
    args = parser.parse_args()
    manager = DBManager(args.city_id, args.db_path)                    
    while True:
        main = Main(args, manager)
        main.Run()
        while True:
            try:
                string_vote = input("Vote? ")
                if (string_vote == "q"):
                    raise AssertionError("There is no other way to exit this program >_>")
                vote = int(string_vote)
                break
            except (TypeError, ValueError):
                print("Invalid input!")
        vote_row = manager.ReadTable(VOTING_ROW, VOTING_PRIMARY_KEYS,
                                     {"CityId": args.city_id, "MostRecentEvent": 1},
                                     table=VOTING_TABLE_NAME, read_flag="expected_modification")
        # Get what should be the only value
        assert(len(vote_row) == 1)
        for key, single_row in vote_row.items():
            vote_row[key] = (single_row[0]._replace(VoteResultInteger=vote), True)
        manager.WriteTable(vote_row, [x[0] for x in VOTING_TABLE_FIELDS],
                           table=VOTING_TABLE_NAME)
        manager.Commit()                   