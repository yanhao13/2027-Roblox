import json
from typing import List, Any
from state import GameCandidate
from monitoring import track_agent_latency


class RankingAgent:
    """Implements the Multi-LLM Debate / Reflection paradigm (Section 3.3)."""
    def __init__(self, llm_client: Any):
        self.llm = llm_client
        self.personas = {
            "critic": "You are a critical game reviewer focusing on negative flaws and system constraints.",
            "advocate": "You are an enthusiastic gamer focusing on structural alignment and positive matches."
        }

    @track_agent_latency("multi_llm_ranking")
    def run_debate_loop(self, context: str, candidates: List[GameCandidate], rounds: int = 1) -> List[GameCandidate]:
        """Executes an iterative reflection loop where personas debate item rankings."""
        if not candidates:
            return []

        candidate_summary = "\n".join([f"- [{c.game_id}] {c.title}: {c.description}" for c in candidates])
        debate_transcript = []
        current_argument = f"Analyze these options for the following context: '{context}'"

        for round_idx in range(rounds):
            critic_prompt = f"{self.personas['critic']}\nContext: {context}\nGames:\n{candidate_summary}\nPrevious Thread: {current_argument}\nIdentify gaps."
            critic_response = self.llm._call_llm(critic_prompt)
            debate_transcript.append(f"Round {round_idx} [Critic]: {critic_response}")

            advocate_prompt = f"{self.personas['advocate']}\nContext: {context}\nGames:\n{candidate_summary}\nPrevious Thread: {critic_response}\nDefend alignment."
            advocate_response = self.llm._call_llm(advocate_prompt)
            debate_transcript.append(f"Round {round_idx} [Advocate]: {advocate_response}")
            current_argument = advocate_response

        consensus_prompt = (
            f"Review this final multi-agent debate transcript:\n\n{chr(10).join(debate_transcript)}\n\n"
            f"Based on user intent, return a valid JSON array containing ONLY the selected game IDs sorted from best to worst match. "
            f"Format schema: [\"id1\", \"id2\"]"
        )

        try:
            json_output = self.llm._call_structured_llm("You are a consensus aggregation compiler.", consensus_prompt)
            sorted_ids = json.loads(json_output)
            if not isinstance(sorted_ids, list) or not sorted_ids:
                return candidates
            reordered = self._reorder_candidates(candidates, sorted_ids)
            # Append any candidates the consensus omitted, so ranking never
            # drops items when the model returns a partial/imperfect id list.
            seen = {c.game_id for c in reordered}
            remaining = [c for c in candidates if c.game_id not in seen]
            return (reordered + remaining) or candidates
        except Exception:
            return candidates

    def _reorder_candidates(self, candidates: List[GameCandidate], sorted_ids: List[str]) -> List[GameCandidate]:
        id_map = {c.game_id: c for c in candidates}
        return [id_map[gid] for gid in sorted_ids if gid in id_map]
