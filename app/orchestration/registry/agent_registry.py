"""
AI Summarizer V9.x

Agent registry.

Maintains the runtime registry of orchestration agents while supporting
dependency injection for V8 compatibility and V9 runtime dependencies.
"""

from __future__ import annotations

from app.orchestration.agents.actions import ActionsAgent
from app.orchestration.agents.insights import InsightsAgent
from app.orchestration.agents.summary import SummaryAgent
from app.orchestration.registry.agent_specs import AgentSpec
from app.orchestration.state.state_contracts import DEFAULT_CONTRACT
from app.prompts.value_objects import PromptId, PromptVersion


class AgentRegistry:
    """
    Registry of orchestration agents.

    The registry is also the composition point for agent dependencies.

    V8 compatibility:
        AgentRegistry() continues to construct the legacy-compatible
        summary agent when no V9 runtime dependencies are supplied.

    V9 runtime:
        Prompt management, LLM service, prompt identity, prompt version,
        and model configuration can be injected into the summary agent.
    """

    def __init__(
        self,
        *,
        summary_agent: SummaryAgent | None = None,
        insights_agent: InsightsAgent | None = None,
        actions_agent: ActionsAgent | None = None,
        prompt_manager=None,
        llm_service=None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
        model: str | None = None,
    ) -> None:
        """
        Initialize the agent registry.

        Explicit agent instances take precedence over automatic
        construction.

        When no summary agent is supplied:

        1. If V9 runtime dependencies are supplied, construct a
           V9-configured SummaryAgent.
        2. Otherwise, construct the V8-compatible legacy SummaryAgent.
        """

        if summary_agent is None:
            if (
                prompt_manager is not None
                and llm_service is not None
                and prompt_id is not None
                and prompt_version is not None
                and model is not None
            ):
                summary_agent = SummaryAgent(
                    prompt_manager=prompt_manager,
                    llm_service=llm_service,
                    prompt_id=prompt_id,
                    prompt_version=prompt_version,
                    model=model,
                )
            else:
                summary_agent = SummaryAgent.legacy()

        if insights_agent is None:
            insights_agent = InsightsAgent()

        if actions_agent is None:
            actions_agent = ActionsAgent()

        self._specs: dict[str, AgentSpec] = {
            "summary": AgentSpec(
                name="summary",
                function_name="summary",
                agent=summary_agent,
                contract=DEFAULT_CONTRACT,
                dependencies=(),
                reads={"text"},
                writes={"summary"},
            ),
            "insights": AgentSpec(
                name="insights",
                function_name="insights",
                agent=insights_agent,
                contract=DEFAULT_CONTRACT,
                dependencies=("summary",),
                reads={"summary"},
                writes={"insight"},
            ),
            "actions": AgentSpec(
                name="actions",
                function_name="actions",
                agent=actions_agent,
                contract=DEFAULT_CONTRACT,
                dependencies=("summary",),
                reads={"summary"},
                writes={"actions"},
            ),
        }

    def get(
        self,
        name: str,
    ) -> AgentSpec:
        """
        Return an agent specification by name.
        """

        return self._specs[name]

    def resolve(
        self,
        function_name: str,
    ):
        """
        Resolve an agent by function name.
        """

        for spec in self._specs.values():
            if spec.function_name == function_name:
                return spec.agent

        raise ValueError(function_name)

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Return whether an agent is registered.
        """

        return name in self._specs

    def list_agents(
        self,
    ) -> list[str]:
        """
        Return all registered agent names.
        """

        return list(self._specs.keys())
