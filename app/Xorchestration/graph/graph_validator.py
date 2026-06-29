from dataclasses import dataclass
from collections import defaultdict
from collections import deque

from app.orchestration.graph.graph_schema import (
    ExecutionGraph,
)

from app.core.exceptions import (
    ValidationError,
)


# -------------------------
# Validation Result
# -------------------------

@dataclass(frozen=True)
class ValidationResult:

    valid: bool

    errors: tuple[str, ...]


# -------------------------
# Validator
# -------------------------

class GraphValidator:

    def validate(
        self,
        graph: ExecutionGraph,
    ) -> ValidationResult:

        errors = []

        validators = [

            self._validate_unique_nodes,

            self._validate_edges,

            self._validate_dependencies,

            self._validate_cycle,

            self._validate_layers,

            self._validate_preprocessing,

            self._validate_reads,

            self._validate_layer_writes,

            self._validate_retry,

            self._validate_roots,

            self._validate_leaves,

            self._validate_connectivity,

        ]

        for validator in validators:

            try:

                validator(
                    graph
                )

            except Exception as e:

                errors.append(
                    str(e)
                )

        return ValidationResult(

            valid=(
                len(errors)
                == 0
            ),

            errors=tuple(
                errors
            )
        )

    # ------------------

    def _validate_unique_nodes(
        self,
        graph,
    ):

        if (
            len(graph.nodes)
            != len(
                set(
                    graph.nodes.keys()
                )
            )
        ):

            raise ValidationError(
                "Duplicate node names"
            )

    # ------------------

    def _validate_edges(
        self,
        graph,
    ):

        nodes = (
            set(
                graph.nodes.keys()
            )
        )

        for edge in graph.edges:

            if (
                edge.source
                not in nodes
            ):

                raise ValidationError(
                    f"Missing source node: {edge.source}"
                )

            if (
                edge.target
                not in nodes
            ):

                raise ValidationError(
                    f"Missing target node: {edge.target}"
                )

    # ------------------

    def _validate_dependencies(
        self,
        graph,
    ):

        for node in graph.nodes.values():

            for dep in node.depends_on:

                if (
                    dep
                    not in graph.nodes
                ):

                    raise ValidationError(
                        f"{node.name} depends on missing node {dep}"
                    )

    # ------------------

    def _validate_cycle(
        self,
        graph,
    ):

        indegree = defaultdict(
            int
        )

        outgoing = defaultdict(
            list
        )

        for edge in graph.edges:

            indegree[
                edge.target
            ] += 1

            outgoing[
                edge.source
            ].append(
                edge.target
            )

        queue = deque(

            node

            for node
            in graph.nodes

            if indegree[node]
            == 0
        )

        visited = 0

        while queue:

            node = (
                queue.popleft()
            )

            visited += 1

            for nxt in outgoing[node]:

                indegree[
                    nxt
                ] -= 1

                if (
                    indegree[nxt]
                    == 0
                ):

                    queue.append(
                        nxt
                    )

        if (
            visited
            != len(
                graph.nodes
            )
        ):

            raise ValidationError(
                "Cycle detected"
            )

    # ------------------

    def _validate_layers(
        self,
        graph,
    ):

        layer_map = {}

        for layer in graph.layers:

            for node in layer.nodes:

                if node in layer_map:

                    raise ValidationError(
                        f"{node} appears multiple times"
                    )

                layer_map[
                    node
                ] = (
                    layer.index
                )

        for edge in graph.edges:

            src = (
                layer_map[
                    edge.source
                ]
            )

            dst = (
                layer_map[
                    edge.target
                ]
            )

            if dst <= src:

                raise ValidationError(
                    f"Invalid layer order {edge.source}->{edge.target}"
                )

    # ------------------

    def _validate_preprocessing(
        self,
        graph,
    ):

        for layer in graph.layers:

            for node_name in layer.nodes:

                node = (
                    graph.nodes[
                        node_name
                    ]
                )

                if (
                    node.stage
                    == "preprocessing"
                    and layer.index != 0
                ):

                    raise ValidationError(
                        f"{node_name} preprocessing outside layer0"
                    )

    # ------------------

    def _validate_reads(
        self,
        graph,
    ):

        produced = set()

        for node in graph.nodes.values():

            produced.update(
                node.writes
            )

        for node in graph.nodes.values():

            missing = (
                node.reads
                - produced
            )

            if missing:

                raise ValidationError(

                    f"{node.name} unresolved reads {missing}"

                )

    # ------------------

    def _validate_layer_writes(
        self,
        graph,
    ):

        for layer in graph.layers:

            seen = set()

            for node_name in layer.nodes:

                node = (
                    graph.nodes[
                        node_name
                    ]
                )

                overlap = (
                    seen
                    &
                    node.writes
                )

                if overlap:

                    raise ValidationError(

                        f"Layer collision {overlap}"

                    )

                seen.update(
                    node.writes
                )

    # ------------------

    def _validate_retry(
        self,
        graph,
    ):

        for node in graph.nodes.values():

            if (
                node.max_retries < 0
            ):

                raise ValidationError(
                    f"{node.name} invalid retry"
                )

            if (
                not node.retryable
                and node.max_retries > 0
            ):

                raise ValidationError(
                    f"{node.name} retry mismatch"
                )

    # ------------------

    def _validate_roots(
        self,
        graph,
    ):

        expected = sorted(

            n.name

            for n
            in graph.nodes.values()

            if not n.depends_on

        )

        if (
            tuple(expected)
            != graph.root_nodes
        ):

            raise ValidationError(
                "Root mismatch"
            )

    # ------------------

    def _validate_leaves(
        self,
        graph,
    ):

        consumed = set()

        for n in graph.nodes.values():

            consumed.update(
                n.depends_on
            )

        expected = sorted(

            n

            for n
            in graph.nodes

            if n not in consumed

        )

        if (
            tuple(expected)
            != graph.leaf_nodes
        ):

            raise ValidationError(
                "Leaf mismatch"
            )

    # ------------------

    def _validate_connectivity(
        self,
        graph,
    ):

        if not graph.nodes:

            raise ValidationError(
                "Empty graph"
            )

        connected = set()

        for edge in graph.edges:

            connected.add(
                edge.source
            )

            connected.add(
                edge.target
            )

        isolated = (

            set(
                graph.nodes.keys()
            )

            -

            connected

        )

        allowed = set(
            graph.root_nodes
        )

        if (

            isolated

            and

            isolated
            != allowed

        ):

            raise ValidationError(

                f"Isolated nodes {isolated}"

            )