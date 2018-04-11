from Objs.Events.Event import *

class NewContractableMegucaEvent(Event):
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)

    # TODO: Put the proper text here.
    def Run(self, state, vote_result=None):
        new_meguca = self.city.NewSensorMeguca(state.targets, state.sensors)
        state.GetEventData(self.event_name)["new_meguca_id"] = new_meguca.id
        return EventResponse(self.event_name, self.event_display_name,
                             "New Contractable Meguca: " + new_meguca.__repr__(),
                             votable_options=("Offer Contract", "Ignore this girl"))