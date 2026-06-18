from app.services.graph.dependency_resolver import (
    resolve_execution_order
)

from app.services.graph.graph_validator import (
    validate_execution_graph
)

from app.services.graph.parallel_groups import (
    build_parallel_groups
)

from app.services.logging.logger import (
    logger
)


class Scheduler:

    @staticmethod
    def build_execution_plan(
        selected_agents,
        registry
    ):

        execution_order = (
            resolve_execution_order(
                selected_agents,
                registry
            )
        )

        # preserve dependency closure
        execution_order = list(
            dict.fromkeys(
                execution_order
            )
        )

        validate_execution_graph(
            execution_order,
            registry
        )

        groups = (
            build_parallel_groups(
                execution_order,
                registry
            )
        )

        metadata = {
            "resolved": True,
            "validated": True,
            "deterministic": True
        }

        logger.info(
            f"****EXECUTION ORDER: "
            f"{execution_order}"
        )

        logger.info(
            f"****PARALLEL GROUPS (scheduler): "
            f"{groups}"
        )

        return {

            "selected_agents":
                execution_order,

            "execution_order":
                execution_order,

            "parallel_groups":
                groups,

            "metadata":
                metadata
        }