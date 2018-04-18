from Objs.Events.Phase import Phase
from Objs.Events.ContractMegucaEvent import ContractMegucaEvent
from Objs.MegucaCity.MegucaCity import MegucaCity

# Handles the phase of the game where a new random meguca is spawned and offered a contract.


class ContractPhase(Phase):
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name

    def __init__(self, meguca_city: MegucaCity):
        super().__init__(meguca_city, valid_events =
                         {"ContractMegucaEvent": ContractMegucaEvent})
                          
    def Run(self, state, vote_result):
        # Get the current event stage
        stage = state.GetEventStage(self.event_name)
        output = self.RunEvent("ContractMegucaEvent", state, vote_result)
        # Check whether event is done and freeze this phase waiting for the next phase if not.
        if not Phase.CheckIfEventDone(state, ContractMegucaEvent.event_name):
            state.SetEventDone(self.event_name, False)
            return output
        state.SetEventDone(self.event_name, True)
        return output