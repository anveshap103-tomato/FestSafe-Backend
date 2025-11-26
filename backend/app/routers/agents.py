"""
Agents router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.db import crud, models
from app.schemas import agent
from app.core.security import get_current_active_user, require_role
from app.services.agent_service import AgentOrchestrator

router = APIRouter()


@router.post("/ask", response_model=agent.AgentAskResponse)
async def ask_agents(
    request: agent.AgentAskRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Send observation to multi-agent system and get action plan."""
    # Get hospital
    hospital = crud.get_hospital(db, hospital_id=request.observation.hospital_id)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Orchestrate agents
    orchestrator = AgentOrchestrator()
    action_plan = orchestrator.orchestrate(request.observation, hospital)
    
    # Log agent action (optional)
    # Could save to agent_actions table
    
    return agent.AgentAskResponse(
        action_plan=action_plan,
        created_at=datetime.utcnow()
    )

