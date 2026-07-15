# app/orchestration/observability/execution_trace.py

from dataclasses import dataclass, field
from typing import Dict, List, Any
import uuid
from datetime import datetime


@dataclass
class NodeTrace:
    trace_id: str
    node_name: str
    status: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ExecutionTrace:
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    node_traces: List[NodeTrace] = field(default_factory=list)

    def record(
        self,
        trace_id: str,
        node_name: str,
        status: str,
    ) -> None:
        """
        Record a node-level execution event.
        """
        self.node_traces.append(
            NodeTrace(
                trace_id=trace_id,
                node_name=node_name,
                status=status,
            )
        )

    def export(self) -> List[Dict[str, Any]]:
        """
        Export trace as serializable structure.
        """
        return [
            {
                "trace_id": t.trace_id,
                "node_name": t.node_name,
                "status": t.status,
                "timestamp": t.timestamp,
            }
            for t in self.node_traces
        ]
