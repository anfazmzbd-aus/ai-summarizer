from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace

from typing import Any
from typing import Mapping
from typing import Optional

from copy import deepcopy


# -----------------------------
# Context
# -----------------------------

@dataclass(frozen=True)
class GlobalContext:

    values: Mapping[
        str,
        Any
    ] = field(
        default_factory=dict
    )


# -----------------------------
# Artifacts
# -----------------------------

@dataclass(frozen=True)
class ArtifactStore:

    values: Mapping[
        str,
        Any
    ] = field(
        default_factory=dict
    )


# -----------------------------
# Node Outputs
# -----------------------------

@dataclass(frozen=True)
class NodeOutputs:

    values: Mapping[
        str,
        dict
    ] = field(
        default_factory=dict
    )


# -----------------------------
# State
# -----------------------------

@dataclass(frozen=True)
class State:

    global_context: GlobalContext

    artifacts: ArtifactStore

    node_outputs: NodeOutputs

    version: str = "7.7"

    metadata: Mapping[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    # ------------------

    @classmethod
    def empty(
        cls,
    ):

        return cls(

            global_context=(
                GlobalContext()
            ),

            artifacts=(
                ArtifactStore()
            ),

            node_outputs=(
                NodeOutputs()
            ),
        )

    # ------------------

    def write_output(
        self,
        node_name: str,
        output: dict,
    ):

        existing = dict(
            self.node_outputs.values
        )

        if (
            node_name
            in existing
        ):

            raise ValueError(
                f"{node_name} already committed"
            )

        existing[
            node_name
        ] = deepcopy(
            output
        )

        return replace(

            self,

            node_outputs=(
                NodeOutputs(
                    values=existing
                )
            )
        )

    # ------------------

    def get_output(
        self,
        node_name: str,
    ):

        return deepcopy(

            self
            .node_outputs
            .values
            .get(
                node_name
            )

        )

    # ------------------

    def update_artifact(
        self,
        key: str,
        value: Any,
    ):

        updated = dict(
            self.artifacts.values
        )

        updated[
            key
        ] = deepcopy(
            value
        )

        return replace(

            self,

            artifacts=(
                ArtifactStore(
                    values=updated
                )
            )
        )

    # ------------------

    def update_context(
        self,
        key: str,
        value: Any,
    ):

        updated = dict(
            self.global_context.values
        )

        updated[
            key
        ] = deepcopy(
            value
        )

        return replace(

            self,

            global_context=(
                GlobalContext(
                    values=updated
                )
            )
        )

    # ------------------

    def snapshot(
        self,
    ):

        return deepcopy(
            self
        )

    # ------------------

    def contains(
        self,
        node_name: str,
    ):

        return (

            node_name

            in

            self
            .node_outputs
            .values

        )