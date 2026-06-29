from copy import deepcopy
from app.services.logging.logger import logger

def build_execution_context(
    state
):
    #logger.info(f"****CONTEXT BUILDER agent_graph: {deepcopy(state.get('selected_agents',[]))}")
                
    return {

        "context": {

            "text":
                state["text"],

            "summary_length":
                state["summary_length"],

            "selected_agents":
                deepcopy(
                    state.get(
                        "selected_agents",
                        []
                    )
                )
        },
        
        "state":
            deepcopy(
                state
            ),

        "runtime": {

            "timings": {},

            "executed": []
        },

        "artifacts": deepcopy(
            state.get(
                "artifacts",
                {}
            )
        )
    }