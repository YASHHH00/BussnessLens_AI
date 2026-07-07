"""
BusinessLens AI — Explainability API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser
from app.schemas.explainability import ExplanationResponse
from app.services.explainability_service import ExplainabilityService

router = APIRouter(prefix="/explain", tags=["Explainability Engine"])


@router.get("/{artifact_type}/{artifact_id}", response_model=ExplanationResponse)
async def explain_artifact(
    artifact_type: str,
    artifact_id: UUID,
    current_user: CurrentUser = None,
):
    """
    Explain how an AI insight, mapping, or query was computed.
    Provides data lineage, formula, rule evaluation, and confidence score.
    generated_sql is role-gated (hidden for non Data Analyst / Admin roles).
    """
    svc = ExplainabilityService()
    ctx = await svc.explain(artifact_type, str(artifact_id), current_user.role)
    return ExplanationResponse.model_validate(ctx.to_dict())
