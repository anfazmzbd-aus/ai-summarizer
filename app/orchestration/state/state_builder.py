from app.orchestration.state.state_model import (
    State,
)


class StateBuilder:

    @staticmethod
    def build(
        text: str,
    ):

        return State(

            global_context={

                "text": text,

            }

        )