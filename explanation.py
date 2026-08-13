from typing import Dict, Any
from state import GameCandidate
from monitoring import track_agent_latency


class ExplanationAgent:
    """Implements the Human-Aligned Explanation Module (Section 3.5)."""
    def __init__(self, llm_client: Any):
        self.llm = llm_client

    @track_agent_latency("explanation_generator")
    def generate_explanation(self, user_intent: str, top_game: GameCandidate) -> Dict[str, Any]:
        """Synthesizes localized text highlighting alignment traits."""
        system_instruction = (
            "You are an empathetic, expert gaming assistant. "
            "Explain exactly why the selected game satisfies the user's request using clear, universal language."
        )

        user_prompt = (
            f"User Profile Request: '{user_intent}'\n"
            f"Recommended Target Game: '{top_game.title}'\n"
            f"Game Metadata Details: Genre={top_game.genres}, Platform={top_game.platforms}.\n"
            f"Game Summary: {top_game.description}\n\n"
            f"Provide a 2-3 sentence personalized justification response:"
        )

        generated_text = self.llm._call_generation_api(system_instruction, user_prompt)
        return {
            "game_title": top_game.title,
            "game_id": top_game.game_id,
            "explanation": generated_text,
            "platforms": top_game.platforms
        }
