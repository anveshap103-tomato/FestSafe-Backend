"""
Agent schemas.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class AgentObservation(BaseModel):
    """Observation input for agents."""
    hospital_id: UUID
    event_id: Optional[UUID] = None
    current_metrics: Dict[str, Any]
    environmental_context: Dict[str, Any]


class AgentAction(BaseModel):
    """Agent action output."""
    agent_type: str
    action: Dict[str, Any]
    reasoning_trace: List[str]
    confidence: float


class ActionPlan(BaseModel):
    """Multi-agent action plan."""
    recommended_staffing: Dict[str, int]
    recommended_supplies: Dict[str, Any]
    confidence: float
    messages_for_public: List[str]
    suggested_triage_templates: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    agent_actions: List[AgentAction]


class AgentAskRequest(BaseModel):
    """Request schema for agent query."""
    observation: AgentObservation


class AgentAskResponse(BaseModel):
    """Response schema for agent query."""
    action_plan: ActionPlan
    created_at: datetime


