"""
Tests for agent service.
"""

import pytest
from app.services.agent_service import AgentOrchestrator, ForecastAgent, TriageAgent, CommunicationAgent
from app.schemas.agent import AgentObservation
from app.db import models


def test_forecast_agent():
    """Test forecast agent."""
    agent = ForecastAgent()
    
    hospital = models.Hospital(
        id="test-id",
        name="Test Hospital",
        latitude=37.7749,
        longitude=-122.4194,
        bed_count=100,
        icu_count=10
    )
    
    observation = AgentObservation(
        hospital_id="test-id",
        current_metrics={"current_patients": 50},
        environmental_context={"aqi": 75}
    )
    
    action = agent.process(observation, hospital)
    
    assert action.agent_type == "forecast"
    assert "recommended_staffing" in action.action
    assert len(action.reasoning_trace) > 0


def test_triage_agent():
    """Test triage agent."""
    agent = TriageAgent()
    
    observation = AgentObservation(
        hospital_id="test-id",
        current_metrics={"primary_complaint_codes": ["R50.9", "R06.02"]},
        environmental_context={}
    )
    
    action = agent.process(observation)
    
    assert action.agent_type == "triage"
    assert "triage_templates" in action.action
    assert "disclaimer" in action.action


def test_communication_agent():
    """Test communication agent."""
    agent = CommunicationAgent()
    
    observation = AgentObservation(
        hospital_id="test-id",
        current_metrics={},
        environmental_context={"aqi": 120}
    )
    
    forecast_result = {"risk_category": "high"}
    action = agent.process(observation, forecast_result)
    
    assert action.agent_type == "communication"
    assert "messages" in action.action
    assert len(action.action["messages"]) > 0


def test_agent_orchestrator():
    """Test agent orchestrator."""
    orchestrator = AgentOrchestrator()
    
    hospital = models.Hospital(
        id="test-id",
        name="Test Hospital",
        latitude=37.7749,
        longitude=-122.4194,
        bed_count=100,
        icu_count=10
    )
    
    observation = AgentObservation(
        hospital_id="test-id",
        current_metrics={"current_patients": 50},
        environmental_context={"aqi": 75}
    )
    
    action_plan = orchestrator.orchestrate(observation, hospital)
    
    assert action_plan.recommended_staffing is not None
    assert action_plan.recommended_supplies is not None
    assert len(action_plan.agent_actions) == 3
    assert len(action_plan.messages_for_public) >= 0


