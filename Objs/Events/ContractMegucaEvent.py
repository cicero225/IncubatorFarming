import random
from Objs.Events.Event import *

class ContractMegucaEvent(Event):

    def __init__(self, meguca_city: MegucaCity, is_multistage_event: bool, event_display_name: str= None):
        # See the Event class for documentation
        super().__init__(self, meguca_city, is_multistage_event=False, event_display_name="ContractMegucaEvent")


    # TODO(Itaywex): I don't think it's wise to require this to take meguca_id_to_contract as an argument,
    # as it needs a consistent function signature to every other event.
    # For now I'm changing this to make a new random guca (as this was the expectation megucacity was
    # coded with)
    def Run(self, state):
        new_meguca = self.meguca_city.NewSensorMeguca(state["targets"], state["sensors"])
        # TODO: Add exception handling/verification that said meguca exists
        # TODO: Maybe each function in meguca city should check and throw exceptions if necessary, and the class that manages the events handles them
        # TODO: That will mean we won't have to do exception handling in every event.
        meguca_name = new_meguca.GetFullName()
        meguca_wish = new_meguca.wish_type
        self.event_display_name = f"{meguca_name} contracted"

        self.city.ContractMeguca(new_meguca.id)

        output_text = self.GenerateOutputText(meguca_name, meguca_wish)

        return EventResponse(self.event_name, self.event_display_name, output_text)

    def GenerateOutputText(self, meguca_name, wish_type):
        # TODO: Maybe we should have different output text based on the girl's stats?
        # TODO: Also, I'm pretty sure that there is a better way to do this. I should do that later.

        first_paragraph = f"You approached {meguca_name} and offered the contract."

        second_paragraph_options = ["As your analysis suggested, she immediately consented.",
                                    "After some deliberation, she accepted the contract.",
                                    "After some time of thinking about it in secret, you approached her once again and she accepted the contract."]

        second_paragraph = random.choice(second_paragraph_options)

        third_paragraph = f"She wished for {wish_type}"

        fourth_paragraph = "Entropy has been reduced!"

        return [first_paragraph, second_paragraph, third_paragraph, fourth_paragraph]




























