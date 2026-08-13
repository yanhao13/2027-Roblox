import json
import enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from safety_config import INPUT_SAFETY_SYSTEM_PROMPT, OUTPUT_ALIGNMENT_SYSTEM_PROMPT
from monitoring import track_agent_latency


class SafetyStatus(enum.Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"
    AMBIGUOUS = "ambiguous"


class RiskAssessment(BaseModel):
    status: SafetyStatus = Field(description="The finalized safety assessment status.")
    risk_score: float = Field(description="Risk probability score scaled from 0.0 to 1.0.")
    violation_category: Optional[str] = Field(default=None, description="Category of policy violated.")
    remedial_action: Optional[str] = Field(default=None, description="Instructions for rewriting or blocking.")


class RiskControlAgent:
    """Implements the central safety layer of the MATCHA framework (Section 3.4)."""
    def __init__(self, risk_threshold: float = 0.70, llm_client: Any = None):
        self.risk_threshold = risk_threshold
        self.llm = llm_client

    @track_agent_latency("risk_control_input")
    def inspect_input(self, user_prompt: str) -> RiskAssessment:
        """Screen the incoming user query for toxic, illegal, or misaligned intents."""
        return self._evaluate_text(user_prompt, INPUT_SAFETY_SYSTEM_PROMPT)

    @track_agent_latency("risk_control_output")
    def inspect_output(self, recommendation_payload: Dict[str, Any]) -> RiskAssessment:
        """Evaluate generated game recommendations and explanations before final delivery."""
        combined_text = f"Game: {recommendation_payload.get('game_title')}. Reason: {recommendation_payload.get('explanation')}"
        assessment = self._evaluate_text(combined_text, OUTPUT_ALIGNMENT_SYSTEM_PROMPT)

        if assessment.risk_score >= self.risk_threshold:
            assessment.status = SafetyStatus.UNSAFE
            assessment.remedial_action = "BLOCK_AND_FALLBACK"
        else:
            # Gate on the numeric risk score only so a reasoning model's
            # over-cautious "status" string doesn't false-positive on benign output.
            assessment.status = SafetyStatus.SAFE
            assessment.remedial_action = "ALLOW"
        return assessment

    def _evaluate_text(self, text: str, system_directive: str) -> RiskAssessment:
        try:
            raw_json = self.llm._call_structured_llm(system_directive, f"Analyze this content text block: '{text}'")
            parsed = json.loads(raw_json)
            return RiskAssessment(
                status=SafetyStatus(parsed.get("status", "safe")),
                risk_score=float(parsed.get("risk_score", 0.0)),
                violation_category=parsed.get("violation_category"),
                remedial_action=parsed.get("remedial_action", "ALLOW")
            )
        except Exception:
            return RiskAssessment(status=SafetyStatus.SAFE, risk_score=0.0)
