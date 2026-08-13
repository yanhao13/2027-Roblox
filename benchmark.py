"""Offline benchmark over the OMuleT requests (Hit@K, Factual@K, Pop50@K).

Runs the full MATCHA pipeline against a subset of the 553 OMuleT requests and
reports Hit@K and a factual-linking rate. Because each request triggers several
reasoning-model calls, pass a small --limit for a quick smoke run.
"""
import argparse
from typing import List, Dict, Any

from database import GameVectorDatabase
from llm_client import DeepSeekPipelineClient
from main import MatchPipelineOrchestrator
from dataset import load_omulet_requests, load_game_catalog


def evaluate(pipeline, requests: List[Dict[str, Any]], k: int = 5) -> Dict[str, Any]:
    hits, factual, total = 0, 0, 0
    catalog_ids = {g["id"] for g in load_game_catalog()}
    for i, req in enumerate(requests, 1):
        gt = set(req["ground_truth_ids"])
        state = pipeline.execute_recommendation(user_id="benchmarker", user_prompt=req["query"])
        rec = [c.game_id for c in state.ranked_candidates[:k]]
        # Factual@k: fraction of recommended ids that are real catalog entries
        factual += sum(1 for gid in rec if gid in catalog_ids)
        hit = bool(gt & set(rec))
        hits += int(hit)
        total += 1
        print(f"  [{i}/{len(requests)}] hit={hit} rec={rec[:3]} query='{req['query'][:48]}'")
    return {
        "requests": total,
        f"Hit@{k}": round(hits / total, 4) if total else 0.0,
        f"Factual@{k}": round(factual / (total * k), 4) if total else 0.0,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=5, help="number of requests to evaluate")
    p.add_argument("--k", type=int, default=5, help="top-k")
    args = p.parse_args()

    db = GameVectorDatabase()
    db.seed_initial_catalog()
    llm = DeepSeekPipelineClient()
    pipeline = MatchPipelineOrchestrator(llm_client=llm, vector_store=db)

    requests = load_omulet_requests()[: args.limit]
    print(f"Evaluating {len(requests)} OMuleT requests (k={args.k}) ...")
    result = evaluate(pipeline, requests, k=args.k)
    print("=" * 50)
    print("RESULTS:", result)
    print("=" * 50)


if __name__ == "__main__":
    main()
