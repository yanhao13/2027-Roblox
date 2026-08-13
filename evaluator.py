from typing import List, Dict, Any
from main import MatchPipelineOrchestrator
from database import GameVectorDatabase
from llm_client import DeepSeekPipelineClient


class RecommendationEvaluator:
    """Evaluates system accuracy using classic information retrieval metrics (Hit Ratio @ K)."""
    def __init__(self, pipeline_instance: Any):
        self.pipeline = pipeline_instance

    def calculate_hit_ratio(self, evaluation_dataset: List[Dict[str, Any]], k: int = 1) -> float:
        hits = 0
        for test_case in evaluation_dataset:
            try:
                state = self.pipeline.execute_recommendation(user_id="benchmarker", user_prompt=test_case["prompt"])
                recommended_ids = [game.game_id for game in state.ranked_candidates[:k]]
                if test_case["ground_truth_game_id"] in recommended_ids:
                    hits += 1
            except Exception:
                continue
        return round(hits / len(evaluation_dataset), 4) if evaluation_dataset else 0.0
