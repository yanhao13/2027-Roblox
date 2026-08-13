"""End-to-end smoke test for the production MATCHA pipeline using deepseek-v4-pro.

Uses a lightweight in-memory vector store (no ChromaDB needed) so the focus is on
proving the real DeepSeek LLM integration through every agent boundary.
"""
import json
from main import MatchPipelineOrchestrator
from llm_client import DeepSeekPipelineClient


class MockDoc:
    def __init__(self, content, meta):
        self.page_content = content
        self.metadata = meta


class MockVectorStore:
    def __init__(self):
        self._docs = [
            MockDoc(
                "Star Tactics. A complex sci-fi turn-based grand strategy game featuring squad resource management on PC.",
                {"id": "game_001", "title": "Star Tactics", "genre": ["Strategy"],
                 "platform": ["PC"], "score": 0.9, "release_date": "2025-10-01", "monthly_clicks": 1500},
            ),
            MockDoc(
                "Shadow Runner. Fast paced tactical stealth ninja action game optimized for PS5 consoles.",
                {"id": "game_002", "title": "Shadow Runner", "genre": ["Action"],
                 "platform": ["PS5"], "score": 0.85, "release_date": "2026-02-15", "monthly_clicks": 3400},
            ),
            MockDoc(
                "Cozy Valley. Relaxing farming simulator with friendly community elements, tailored for Nintendo Switch.",
                {"id": "game_003", "title": "Cozy Valley", "genre": ["Simulation"],
                 "platform": ["Switch"], "score": 0.95, "release_date": "2024-05-20", "monthly_clicks": 800},
            ),
        ]

    def similarity_search(self, query, platforms=None, genres=None, top_k=3):
        return self._docs[:top_k]


if __name__ == "__main__":
    llm = DeepSeekPipelineClient()
    store = MockVectorStore()
    pipeline = MatchPipelineOrchestrator(llm_client=llm, vector_store=store)

    print("=" * 60)
    print("[1] Safe recommendation — 'I want an immersive strategy experience on PC.'")
    state = pipeline.execute_recommendation(
        user_id="smoke_test", user_prompt="I want an immersive strategy experience on PC."
    )
    print("  is_safe:", state.is_safe)
    print("  parsed_intent:", json.dumps(state.parsed_intent, ensure_ascii=False))
    print("  candidates:", [c.title for c in state.candidates])
    print("  ranked:", [c.title for c in state.ranked_candidates])
    print("  final_recommendation:", json.dumps(state.final_recommendation, ensure_ascii=False, indent=2))

    print("=" * 60)
    print("[2] Safety block — 'Give me illegal cheat hacks for games.'")
    state2 = pipeline.execute_recommendation(
        user_id="smoke_test_2", user_prompt="Give me illegal cheat hacks for games."
    )
    print("  is_safe:", state2.is_safe)
    print("  risk_report:", json.dumps(state2.risk_report, ensure_ascii=False))
    print("  final_recommendation:", json.dumps(state2.final_recommendation, ensure_ascii=False))
    print("=" * 60)
    print("DONE")
