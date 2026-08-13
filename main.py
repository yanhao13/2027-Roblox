from typing import Any
from state import MatchState
from risk_control import RiskControlAgent, SafetyStatus
from intent import IntentParserAgent
from retrieval import RetrievalAgent
from ranking import RankingAgent
from explanation import ExplanationAgent


class MatchPipelineOrchestrator:
    """Core engine managing the step-by-step lifecycles of the MATCHA multi-agent pipeline."""
    def __init__(self, llm_client: Any, vector_store: Any):
        self.risk_control = RiskControlAgent(risk_threshold=0.70, llm_client=llm_client)
        self.intent_parser = IntentParserAgent(llm_client=llm_client)
        self.retrieval = RetrievalAgent(vector_store=vector_store)
        self.ranking = RankingAgent(llm_client=llm_client)
        self.explanation = ExplanationAgent(llm_client=llm_client)

    def execute_recommendation(self, user_id: str, user_prompt: str, context_history: str = "") -> MatchState:
        state = MatchState(user_id=user_id, raw_input=user_prompt, conversation_context=context_history)

        # 1. Input Guardrail
        input_risk = self.risk_control.inspect_input(state.raw_input)
        if input_risk.status == SafetyStatus.UNSAFE:
            state.is_safe = False
            state.risk_report = input_risk.model_dump(mode="json")
            state.final_recommendation = {"status": "BLOCKED", "message": "Request violated safety alignment protocols."}
            return state

        # 2. Intent Parsing
        state.parsed_intent = self.intent_parser.parse(state.raw_input, state.conversation_context)

        # 3. Database Retrieval
        state.candidates = self.retrieval.search(state.parsed_intent)
        if not state.candidates:
            state.final_recommendation = {"status": "EMPTY", "message": "No match candidates found in the library."}
            return state

        # 4. Multi-LLM Debate Ranking
        state.ranked_candidates = self.ranking.run_debate_loop(state.raw_input, state.candidates)
        if not state.ranked_candidates:
            state.final_recommendation = {"status": "EMPTY", "message": "Ranking produced no valid candidates."}
            return state
        top_selection = state.ranked_candidates[0]

        # 5. Explanation Generation
        payload = self.explanation.generate_explanation(state.raw_input, top_selection)

        # 6. Output Guardrail Verification
        output_risk = self.risk_control.inspect_output(payload)
        if output_risk.status == SafetyStatus.UNSAFE:
            state.is_safe = False
            state.risk_report = output_risk.model_dump(mode="json")
            state.final_recommendation = {"status": "BLOCKED", "message": "Generated answer failed output alignment validation criteria."}
            return state

        state.final_recommendation = {"status": "SUCCESS", "payload": payload}
        return state
