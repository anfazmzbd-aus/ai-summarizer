import time
import uuid
from datetime import datetime

from app.services.logging.logger import logger

class TraceLogger:

    def __init__(self):

        self.traces = []

    def start(
        self,
        execution_id,
        agent,
        input_state
    ):
        logger.info(f"****LOGGER TRACE START: {agent}")
        return {
            "trace_id":
                str(
                    uuid.uuid4()
                ),

            "execution_id":
                execution_id,

            "agent":
                agent,

            "started_at":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3],

            "start":
                time.perf_counter(),

            "input":
                input_state,

            "parallel_group":
            input_state.get(
                "current_group"
            )
        }

    def end(
        self,
        trace,
        output,
        status
    ):

        trace[
            "ended_at"
        ] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]
        )

        trace[
            "end"
        ] = (
            time.perf_counter()
        )

        trace["status"] = (
            status
        )

        trace["output"] = (
            output
        )

        self.traces.append(
            trace
        )

        trace["duration"] = (
            round(
                trace["end"]
                - trace["start"],
                6
            )
        )

        logger.info(
            f"****LOGGER TRACE END : "
            f"{trace['agent']} | "
            f"{trace['status']} | "
            f"{trace['duration']}"
        )

    def get_traces(self):

        return self.traces
    
trace_logger = TraceLogger()