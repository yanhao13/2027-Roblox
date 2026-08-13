import math
from datetime import datetime, timezone
from typing import List
from state import GameCandidate


class TrendingRanker:
    """Implements a custom score modifier calculating popularity velocity and exponential time-decay weights."""
    def __init__(self, half_life_days: float = 180.0, popularity_weight: float = 0.25):
        self.half_life_days = half_life_days
        self.decay_constant = math.log(2) / self.half_life_days
        self.popularity_weight = popularity_weight

    def apply_trending_boost(self, candidates: List[GameCandidate], metadatas: List[dict]) -> List[GameCandidate]:
        """Formula: Final Score = Semantic Score * Time Decay * (1 + (Popularity Weight * log(Clicks)))"""
        now = datetime.now(timezone.utc)

        for idx, candidate in enumerate(candidates):
            meta = metadatas[idx]
            release_str = meta.get("release_date", "2026-01-01")
            try:
                release_date = datetime.strptime(release_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                release_date = now

            age_days = max(0, (now - release_date).days)
            time_decay = math.exp(-self.decay_constant * age_days)

            clicks = max(1, meta.get("monthly_clicks", 1))
            popularity_boost = 1.0 + (self.popularity_weight * math.log10(clicks))

            candidate.score = round(candidate.score * time_decay * popularity_boost, 4)

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates
