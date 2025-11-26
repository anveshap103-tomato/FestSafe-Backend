"""
Multi-agent orchestration service.
"""

from typing import Dict, Any, List
from datetime import datetime
from app.schemas.agent import AgentObservation, ActionPlan, AgentAction
from app.services.forecast_service import ForecastService
from app.db import models


class ForecastAgent:
    """Agent for forecasting and resource needs."""
    
    def __init__(self):
        self.forecast_service = ForecastService()
    
    def process(self, observation: AgentObservation, hospital: models.Hospital) -> AgentAction:
        """Process observation and generate forecast-based recommendations."""
        # Get forecast
        observations = []  # Would fetch from DB in real implementation
        forecast_result = self.forecast_service.predict(
            hospital=hospital,
            observations=observations,
            event_id=str(observation.event_id) if observation.event_id else None,
            horizon_hours=24
        )
        
        # Calculate resource needs
        predicted_arrivals = forecast_result["predicted_arrivals"]
        recommended_doctors = max(1, int(predicted_arrivals * 0.1))
        recommended_nurses = max(2, int(predicted_arrivals * 0.3))
        recommended_beds = max(5, int(predicted_arrivals * 0.8))
        recommended_oxygen = max(100, int(predicted_arrivals * 50))
        
        return AgentAction(
            agent_type="forecast",
            action={
                "predicted_arrivals": predicted_arrivals,
                "recommended_staffing": {
                    "doctors": recommended_doctors,
                    "nurses": recommended_nurses
                },
                "recommended_supplies": {
                    "beds": recommended_beds,
                    "oxygen_liters": recommended_oxygen
                }
            },
            reasoning_trace=[
                f"Predicted {predicted_arrivals:.1f} arrivals in next 24h",
                f"Risk category: {forecast_result['risk_category']}",
                f"Based on historical patterns and current capacity"
            ],
            confidence=forecast_result["confidence"]
        )


class TriageAgent:
    """Agent for triage recommendations."""
    
    def process(self, observation: AgentObservation) -> AgentAction:
        """Process observation and generate triage recommendations."""
        complaint_codes = observation.current_metrics.get("primary_complaint_codes", [])
        
        # Simple triage logic based on complaint codes
        triage_templates = []
        if "R50.9" in complaint_codes:  # Fever
            triage_templates.append({
                "priority": "medium",
                "suggested_assessment": "Temperature, vital signs, symptom duration",
                "note": "Monitor for dehydration"
            })
        if "R06.02" in complaint_codes:  # Shortness of breath
            triage_templates.append({
                "priority": "high",
                "suggested_assessment": "Oxygen saturation, respiratory rate, chest exam",
                "note": "Consider environmental factors (AQI)"
            })
        
        # Safety disclaimer
        suggestions = {
            "triage_templates": triage_templates,
            "disclaimer": "These are suggestions only. All decisions require clinician review.",
            "refer_to_clinician": True
        }
        
        return AgentAction(
            agent_type="triage",
            action=suggestions,
            reasoning_trace=[
                f"Analyzed {len(complaint_codes)} complaint codes",
                "Generated triage templates based on common patterns",
                "All suggestions require clinician approval"
            ],
            confidence=0.7
        )


class CommunicationAgent:
    """Agent for public health communication."""
    
    def process(self, observation: AgentObservation, forecast_result: Dict[str, Any]) -> AgentAction:
        """Generate public health advisories."""
        risk_category = forecast_result.get("risk_category", "low")
        aqi = observation.environmental_context.get("aqi", 50)
        
        messages = []
        if risk_category == "high":
            messages.append(
                "High patient volume expected. Consider alternative care options for non-emergencies."
            )
        if aqi > 100:
            messages.append(
                "Air quality is poor. Those with respiratory conditions should limit outdoor exposure."
            )
        if risk_category in ["medium", "high"]:
            messages.append(
                "Hospital capacity may be limited. Please use emergency services for true emergencies only."
            )
        
        return AgentAction(
            agent_type="communication",
            action={
                "messages": messages,
                "target_audience": "public",
                "urgency": risk_category
            },
            reasoning_trace=[
                f"Risk category: {risk_category}",
                f"Environmental factors considered (AQI: {aqi})",
                "Messages tailored for public health communication"
            ],
            confidence=0.8
        )


class AgentOrchestrator:
    """Orchestrates multiple agents."""
    
    def __init__(self):
        self.forecast_agent = ForecastAgent()
        self.triage_agent = TriageAgent()
        self.communication_agent = CommunicationAgent()
    
    def orchestrate(self, observation: AgentObservation, hospital: models.Hospital) -> ActionPlan:
        """Orchestrate all agents and merge results."""
        # Run forecast agent
        forecast_action = self.forecast_agent.process(observation, hospital)
        
        # Run triage agent
        triage_action = self.triage_agent.process(observation)
        
        # Run communication agent
        forecast_result = {
            "risk_category": forecast_action.action.get("predicted_arrivals", 0) > 10 and "high" or "medium"
        }
        communication_action = self.communication_agent.process(observation, forecast_result)
        
        # Merge actions
        action_plan = ActionPlan(
            recommended_staffing=forecast_action.action.get("recommended_staffing", {}),
            recommended_supplies=forecast_action.action.get("recommended_supplies", {}),
            confidence=forecast_action.confidence,
            messages_for_public=communication_action.action.get("messages", []),
            suggested_triage_templates=triage_action.action.get("triage_templates", []),
            evidence=[
                {"source": "forecast_agent", "data": forecast_action.action},
                {"source": "triage_agent", "data": triage_action.action},
                {"source": "communication_agent", "data": communication_action.action}
            ],
            agent_actions=[forecast_action, triage_action, communication_action]
        )
        
        return action_plan


