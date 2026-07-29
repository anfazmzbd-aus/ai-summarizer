from dataclasses import dataclass
from typing import List

from app.orchestration.graph.graph_builder import GraphBuilder
from app.orchestration.graph.graph_schema import ExecutionGraph

# ---------------------------------------------------------
# Schedule Result
# ---------------------------------------------------------


@dataclass(frozen=True)
class ScheduleResult:
    graph: ExecutionGraph
    selected_agents: List[str]
    strategy: str


# ---------------------------------------------------------
# Scheduler
# ---------------------------------------------------------


class Scheduler:
    def __init__(self, registry, contracts):
        self.registry = registry
        self.contracts = contracts
        self.graph_builder = GraphBuilder(registry)

    # -----------------------------------------------------
    # Agent Selection
    # -----------------------------------------------------

    def _select_agents(
        self,
        text: str,
    ) -> List[str]:

        text = text.lower()

        agents = ["summary"]

        if "revenue" in text:
            agents.append("insights")

        if "trend" in text:
            agents.append("trend")

        if "action" in text or "should" in text:
            agents.append("actions")

        # Preserve order while removing duplicates
        return list(dict.fromkeys(agents))

    # -----------------------------------------------------
    # Strategy Selection
    # -----------------------------------------------------

    def _build_strategy(
        self,
        selected_agents: List[str],
    ) -> str:

        if len(selected_agents) <= 2:
            return "simple"

        return "business_report"

    # -----------------------------------------------------
    # Schedule
    # -----------------------------------------------------

    def schedule(
        self,
        text: str,
        contracts=None,
    ) -> ScheduleResult:

        selected_agents = self._select_agents(text)

        strategy = self._build_strategy(selected_agents)

        graph = self.graph_builder.build(selected_agents)

        return ScheduleResult(
            graph=graph,
            selected_agents=selected_agents,
            strategy=strategy,
        )
