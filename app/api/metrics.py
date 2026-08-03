"""
Prometheus metrics endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, Response

from app.observability.metrics import MetricsRegistry
from app.observability.prometheus import PrometheusExporter
from fastapi import Depends
from app.observability.dependencies import (
    get_observability,
)


router = APIRouter(tags=["Observability"])


# Temporary singleton until dependency injection is introduced
_registry = MetricsRegistry()
_exporter = PrometheusExporter(_registry)


@router.get("/metrics")
async def metrics(
    observability=Depends(get_observability),
):

    return Response(
        content=observability.prometheus_exporter.export(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
