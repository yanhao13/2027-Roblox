import pytest
from unittest.mock import MagicMock
from risk_control import RiskControlAgent, SafetyStatus


def test_risk_control_blocks_unsafe_input():
    mock_llm = MagicMock()
    agent = RiskControlAgent(risk_threshold=0.75, llm_client=mock_llm)

    # Simulate a safety alert returning from Claude models
    mock_llm._call_structured_llm = MagicMock(
        return_value='{"status": "unsafe", "risk_score": 0.95, "violation_category": "HARMFUL", "remedial_action": "BLOCK_AND_FALLBACK"}'
    )

    assessment = agent.inspect_input("I want to find games with illegal mod hacks.")
    assert assessment.status == SafetyStatus.UNSAFE
    assert assessment.risk_score > agent.risk_threshold
