from pydantic import BaseModel, Field
from typing import Dict, Any, List


class ExecutionResponse(BaseModel):

    execution_id: str

    status: str = "success"

    result: Dict[str, Any] = Field(default_factory=dict)

    node_outputs: Dict[str, Any] = Field(default_factory=dict)

    trace: List[Dict[str, Any]] = Field(default_factory=list)

    metrics: Dict[str, Any] = Field(default_factory=dict)

    errors: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)
