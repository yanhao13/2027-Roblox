from typing import List, Dict, Any
from state import GameCandidate
from ranking_boost import TrendingRanker
from monitoring import track_agent_latency


class RetrievalAgent:
    """Implements the Tool-Augmented Retrieval Layer (Section 3.2)."""
    def __init__(self, vector_store: Any):
        self.vector_store = vector_store
        self.trending_ranker = TrendingRanker()

    @track_agent_latency("retrieval_agent")
    def search(self, parsed_intent: Dict[str, Any], top_k: int = 3) -> List[GameCandidate]:
        """Executes hybrid semantic search with structural metadata filters and custom ranking boosts."""
        query_string = parsed_intent.get("semantic_keywords", "")
        allowed_platforms = parsed_intent.get("platforms", [])
        allowed_genres = parsed_intent.get("genres", [])

        raw_results = self.vector_store.similarity_search(
            query=query_string,
            platforms=allowed_platforms,
            genres=allowed_genres,
            top_k=top_k
        )

        candidates = []
        metadatas = []
        for doc in raw_results:
            candidates.append(
                GameCandidate(
                    game_id=doc.metadata.get("id"),
                    title=doc.metadata.get("title"),
                    genres=doc.metadata.get("genre", []),
                    platforms=doc.metadata.get("platform", []),
                    description=doc.page_content,
                    score=doc.metadata.get("score", 0.5)
                )
            )
            metadatas.append(doc.metadata)

        # Apply the exponential popularity time decay boost calculations
        return self.trending_ranker.apply_trending_boost(candidates, metadatas)
