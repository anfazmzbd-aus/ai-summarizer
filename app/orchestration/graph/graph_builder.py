from collections import defaultdict
from collections import deque
from uuid import uuid4

from app.orchestration.graph.graph_schema import (
    ExecutionGraph,
    GraphNode,
    GraphEdge,
    ExecutionLayer,
)

from app.core.exceptions import (
    ValidationError,
)

from app.orchestration.registry.agent_registry import (
    AgentRegistry,
)


class GraphBuilder:

    def __init__(
        self,
        registry: AgentRegistry,
    ):

        self.registry = registry

    def build(
        self,
        selected_agents: list[str],
    ) -> ExecutionGraph:

        selected_agents = (
            self._normalize_agents(
                selected_agents
            )
        )

        nodes = (
            self._build_nodes(
                selected_agents
            )
        )

        edges = (
            self._build_edges(
                nodes
            )
        )

        roots = (
            self._derive_roots(
                nodes
            )
        )

        leaves = (
            self._derive_leaves(
                nodes
            )
        )

        layers = (
            self._build_layers(
                nodes,
                edges,
            )
        )

        return ExecutionGraph(

            execution_id=(
                str(
                    uuid4()
                )
            ),

            version="7.7",

            nodes=nodes,

            edges=tuple(
                edges
            ),

            layers=tuple(
                layers
            ),

            selected_agents=tuple(
                selected_agents
            ),

            root_nodes=tuple(
                roots
            ),

            leaf_nodes=tuple(
                leaves
            ),

            metadata={}
        )

    def _normalize_agents(
        self,
        agents: list[str],
    ) -> list[str]:

        seen = set()

        ordered = []

        for agent in agents:

            if agent in seen:
                continue

            seen.add(agent)

            ordered.append(agent)

        return sorted(
            ordered
        )

    def _build_nodes(
        self,
        selected_agents: list[str],
    ) -> dict[str, GraphNode]:

        nodes = {}

        for agent in selected_agents:

            spec = (
                self.registry
                .get(
                    agent
                )
            )

            node = GraphNode(

                name=spec.name,

                function_name=(
                    spec.function_name
                ),

                stage="dag",

                depends_on=tuple(
                    sorted(
                        spec.dependencies
                    )
                ),

                reads=frozenset(
                    spec.reads
                ),

                writes=frozenset(
                    spec.writes
                ),

                retryable=(
                    spec.retryable
                ),

                timeout_seconds=(
                    spec.timeout_seconds
                ),

                max_retries=(
                    spec.max_retries
                ),

                metadata=(
                    spec.metadata
                )
            )

            nodes[
                node.name
            ] = node

        return nodes

    def _build_edges(
        self,
        nodes: dict,
    ) -> list[GraphEdge]:

        edges = []

        for node in nodes.values():

            for dep in node.depends_on:

                if dep not in nodes:

                    raise (
                        ValidationError(
                            f"Unknown dependency: {dep}"
                        )
                    )

                edges.append(

                    GraphEdge(
                        source=dep,
                        target=node.name
                    )

                )

        return sorted(
            edges,
            key=lambda e: (
                e.source,
                e.target
            )
        )

    def _derive_roots(
        self,
        nodes,
    ):

        roots = []

        for node in nodes.values():

            if not node.depends_on:

                roots.append(
                    node.name
                )

        return sorted(
            roots
        )

    def _derive_leaves(
        self,
        nodes,
    ):

        consumed = set()

        for node in nodes.values():

            consumed.update(
                node.depends_on
            )

        leaves = []

        for name in nodes:

            if name not in consumed:

                leaves.append(
                    name
                )

        return sorted(
            leaves
        )

    def _build_layers(
        self,
        nodes,
        edges,
    ):

        indegree = defaultdict(
            int
        )

        outgoing = (
            defaultdict(
                list
            )
        )

        for edge in edges:

            indegree[
                edge.target
            ] += 1

            outgoing[
                edge.source
            ].append(
                edge.target
            )

        queue = deque(

            sorted(

                node
                for node in nodes
                if indegree[node] == 0

            )

        )

        layers = []

        layer_idx = 0

        visited = set()

        while queue:

            current = []

            count = len(
                queue
            )

            for _ in range(
                count
            ):

                node = (
                    queue.popleft()
                )

                visited.add(
                    node
                )

                current.append(
                    node
                )

                for child in sorted(

                    outgoing[
                        node
                    ]

                ):

                    indegree[
                        child
                    ] -= 1

                    if (
                        indegree[
                            child
                        ]
                        == 0
                    ):

                        queue.append(
                            child
                        )

            layers.append(

                ExecutionLayer(
                    index=layer_idx,
                    nodes=tuple(
                        current
                    )
                )

            )

            layer_idx += 1

        if (
            len(
                visited
            )
            != len(
                nodes
            )
        ):

            raise ValidationError(
                "Cycle detected"
            )

        return layers