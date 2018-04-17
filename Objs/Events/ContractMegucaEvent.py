import random
from Objs.Events.Event import *

class ContractMegucaEvent(Event):
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)

    def Run(self, state, vote_result):
        if vote_result==1:
            return EventResponse(self.event_name, self.event_display_name, "We decided this girl was not worth contracting, and move on.")
        new_meguca_id = state.GetEventData("Objs.Events.NewContractableMegucaEvent")["new_meguca_id"]
        new_meguca = self.city.GetMegucaById(new_meguca_id)
        # TODO: Add exception handling/verification that said meguca exists
        # TODO: Maybe each function in meguca city should check and throw exceptions if necessary, and the class that manages the events handles them
        # TODO: That will mean we won't have to do exception handling in every event.
        meguca_name = new_meguca.GetFullName()
        meguca_wish = new_meguca.wish_type
        self.event_display_name = f"{meguca_name} contracted"

        self.city.ContractMeguca(new_meguca.id)

        output_text = self.GenerateOutputText(meguca_name, meguca_wish)

        lost = self.city.PotentialDecay()
        
        if lost:
            output_text += f"\n\nWhile investigating this girl, it comes to your attention that some other girls have lost potential: {', '.join(l.GetFullName() for l in lost)}.\n\nUnfortunate."
        
        return EventResponse(self.event_name, self.event_display_name, output_text)

    # TODO: Make it so they can turn down contracts sometimes?
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

        return "\n".join([first_paragraph, second_paragraph, third_paragraph, fourth_paragraph])




























