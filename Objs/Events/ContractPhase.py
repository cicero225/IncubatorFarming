from Objs.Event.Phase import Phase
from Objs.Events.ContractMegucaEvent import ContractMegucaEvent
from Objs.Events.NewContractableMegucaEvent import NewContractableMegucaEvent


# Handles the phase of the game where a new random meguca is spawned and offered a contract.


def ContractPhase(Phase):
    def __init__(self, meguca_city: MegucaCity, is_multistage_event: bool, event_display_name: str,
                 valid_events: Dict[str, type]):
        super().__init__(self, meguca_city, True, "ContractPhase", last_stage=1
                         valid_events =
                         {"ContractMegucaEvent": ContractMegucaEvent,
                          "NewContractableMegucaEvent": NewContractableMegucaEvent})
                          
    def Run(self, state, vote_result):
        # Get the current event stage
        stage = state.GetEventStage(self.event_name)
        # Awkward-looking but fine.
        if stage == 0:
            output = self.RunEvent("NewContractableMegucaEvent", state, vote_result)
            # Here we know this always ends in a vote, so we return immediately. This is hardcoded logic
            # that will not work for the other phases.
            return output
        if stage == 1:
            output = self.RunEvent("ContractMegucaEvent", state, vote_result)
            # Here we know the phase is over, so return. This has no vote, so main should continue to next
            # phase.
            return output