"""
The main for the Incubator Farming game.

usage: IncubatorFarming.py [-h] [--restart] city_id db_path

Incubator Farming Main Script

positional arguments:
  city_id     An id that defines the city for this run.
  db_path     The location of the db file this game is stored in.

optional arguments:
  -h, --help  show this help message and exit
  --restart   Force restart of this game.

city_id is mandatory. restart is only required to restart the game.

TODO: implement restart, which is unimplemented at the moment and will do weird shit.

TODO: Maybe have other arguments for calibration?
"""

import argparse
import json
from typing import Any

from Objs.DBManager.DBManager import DBManager
from Objs.Events.Phase import Phase
from Objs.Events.StartGameEvent import StartGameEvent
from Objs.Meguca.Defines import *
from Objs.MegucaCity.MegucaCity import MegucaCity
from Objs.State.State import State
from Objs.Utils.GlobalDefines import *

# Phases, in their own section because they're special
from Objs.Events.ContractPhase import ContractPhase
from Objs.Events.RandomEventPhase import RandomEventPhase

parser = argparse.ArgumentParser(description='Incubator Farming Main Script')
parser.add_argument('--restart', action='store_true',
                    help='Force restart of this game.')
parser.add_argument('city_id', type=int,
                    help='An id that defines the city for this run.')
parser.add_argument('db_path',
                    help='The location of the db file this game is stored in.')

# Placing these constants here for easy reference. Can be split into own file if necessary.
PHASE_ORDER = [ContractPhase, RandomEventPhase]

class Main:
    PHASE_DICT = {x.__name__: x  for x in PHASE_ORDER}

    def __init__(self, args, manager=None):
        # Initial object set up
        self.city_id = args.city_id
        self.db_path = args.db_path
        self.manager = DBManager(self.city_id, self.db_path) if manager is None else manager
        self.manager.CreateTableIfDoesNotExist(RUNNING_TABLE_FIELDS, table=RUNNING_TABLE_NAME)
        # Check if game is already running. If so, read from existing game. If not, start new game.
        potential_row = self.manager.ReadTable(RUNNING_ROW, RUNNING_PRIMARY_KEYS, {"CityId": self.city_id}, table=RUNNING_TABLE_NAME, read_flag="expected_modification")
        if not potential_row or args.restart:
            # Start New Game
            self.ClearExistingGame()
            self.manager.CreateTableIfDoesNotExist(MEGUCA_TABLE_FIELDS, table=MEGUCA_TABLE_NAME)
            self.manager.CreateTableIfDoesNotExist(VOTING_TABLE_FIELDS, table=VOTING_TABLE_NAME)
            self.city = MegucaCity(self.city_id)
            self.state = State(self.manager)
            for i, pop_count in enumerate(INITIAL_MEGUCA_POPULATION):
                for _ in range(pop_count):
                    new_meguca = self.city.NewSensorMeguca()
                    if i>=1:
                        self.city.ContractMeguca(new_meguca.id)
                    if i==2:
                        self.city.WitchMeguca(new_meguca.id)
                    elif i==3:
                        self.city.KillMeguca(new_meguca.id)
            # TODO: Add an introduction phase.
            self.phase = PHASE_ORDER[0]
            self.state.current_phase = self.phase.__name__
            self.new_game = True
        else:
            # Reload existing game.
            self.city = MegucaCity.ReadCityFromDb(self.city_id, self.manager)
            self.state = State(self.manager)
            self.phase = self.PHASE_DICT[self.state.current_phase]
            self.new_game = False
            
    # TODO: Handle ending a game.
    def Run(self):
        vote_result = -1
        vote_row = None
        results = []
        if self.new_game:
            # Run the game starting phase.
            results.append(StartGameEvent(self.city).Run(self.state, vote_result))
        else:
            # Get voting information.
            # TODO: Put this in the Communication Objects?
            vote_row = self.manager.ReadTable(VOTING_ROW, VOTING_PRIMARY_KEYS, {"CityId": self.city_id, "MostRecentEvent": 1}, table=VOTING_TABLE_NAME, read_flag="expected_modification")
            if vote_row:
                assert(len(vote_row) == 1)
                row_data = tuple(vote_row.values())[0][0]
            vote_result = row_data.VoteResultInteger
            if vote_result == -1:
                raise AssertionError("Vote result not set! Is this correct?")
        # Make an instance of the phase
        this_phase = self.phase(self.city)
        while True:
            result = this_phase.Run(self.state, vote_result)
            results.append(result)
            # Is the phase done? If so, increment our own phase.
            event_done = Phase.CheckIfEventDone(self.state, this_phase.event_name)
            if event_done:
                # We can make this arbitrarily complex, but for now this is fine.
                new_phase_index = (PHASE_ORDER.index(self.phase) + 1) % (len(PHASE_ORDER))
                self.phase = PHASE_ORDER[new_phase_index]
                self.state.current_phase = self.phase.__name__
            # Does this result have a vote?
            if Phase.CheckIfVote(result):
                # If so, we're done and should return output.
                break
            if event_done:
                this_phase = self.phase(self.city)
            vote_result = -1  # We no longer have a vote result if we're continuing events. 
        # Set original voting information to not most recent.
        if vote_row is not None:
            for key, single_row in vote_row.items():
                vote_row[key] = (single_row[0]._replace(MostRecentEvent=0), True)
        else:
            vote_row = {}  
        # Add new voting information
        vote_row[frozenset({self.city_id, results[-1].timestamp})] = (
            VOTING_ROW(
            self.city_id, results[-1].timestamp, json.dumps([r.output_text for r in results]),
            json.dumps(results[-1].votable_options), -1, 1),
            True)
        for result in results:
            print(result.output_text + "\n")  # For readability when running in terminal
        for i, option in enumerate(results[-1].votable_options):
            print(f"{i}: {option}")
        self.manager.WriteTable(vote_row, [x[0] for x in VOTING_TABLE_FIELDS],
                                table=VOTING_TABLE_NAME, forced=self.new_game)
        self.FinalizeGameOutput()
        
    def FinalizeGameOutput(self):
        if self.new_game:
            self.manager.WriteTable({frozenset({self.city_id}): (RUNNING_ROW(self.city_id), True)},
                [x[0] for x in RUNNING_TABLE_FIELDS], table=RUNNING_TABLE_NAME)
        else:
            self.manager.MarkWritten(table=RUNNING_TABLE_NAME)
        self.city.WriteCityToDB(self.manager, forced=True)
        self.state.WriteState()
        self.manager.Commit()
        
    def ClearExistingGame(self):
        pass


if __name__ == '__main__':
    args = parser.parse_args()
    manager = DBManager(args.city_id, args.db_path)
    try:
        main = Main(args, manager)
        main.Run()
    except Exception as e:
        manager.WriteExceptionState(str(e))
        raise e