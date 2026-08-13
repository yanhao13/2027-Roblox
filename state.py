from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GameCandidate(BaseModel):
    """Schema for retrieved video game items."""
    game_id: str
    title: str
    genres: List[str]
    platforms: List[str]
    description: str
    score: float = 0.0


class MatchState(BaseModel):
    """Global workflow state tracking data across all 5 MATCHA agents."""
    user_id: str
    raw_input: str
    conversation_context: str = ""
    parsed_intent: Dict[str, Any] = Field(default_factory=dict)
    candidates: List[GameCandidate] = Field(default_factory=list)
    ranked_candidates: List[GameCandidate] = Field(default_factory=list)
    debate_history: List[str] = Field(default_factory=list)
    final_explanation: Optional[str] = None
    is_safe: bool = True
    risk_report: Dict[str, Any] = Field(default_factory=dict)
    final_recommendation: Optional[Dict[str, Any]] = None
