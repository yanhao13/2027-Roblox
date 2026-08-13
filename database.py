import os
import chromadb
from typing import List, Any


class GameVectorDatabase:
    """Manages the persistent catalog storage using ChromaDB. Handles embedding generation tracking and similarity queries."""
    def __init__(self, db_path: str = "./chroma_db"):
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="game_catalog",
            metadata={"hnsw:space": "cosine"}
        )

    CATALOG_CSV = "data/omulet/game_catalog.csv"

    def seed_initial_catalog(self, catalog_path: str = None):
        """Populate the catalog from the OMuleT CSV, falling back to samples.

        The OMuleT dataset (arXiv:2411.19352) provides 2,074 Roblox games; the
        CSV at ``data/omulet/game_catalog.csv`` is the schema-exact stand-in
        (see ``generate_omulet_data.py``). Drop in the real file to replace it.
        """
        if self.collection.count() > 0:
            return

        path = catalog_path or self.CATALOG_CSV
        if os.path.exists(path):
            self._seed_from_csv(path)
        else:
            self._seed_samples()
        print(f"[+] Seed data written to ChromaDB (count={self.collection.count()}).")

    def _seed_from_csv(self, path: str):
        import csv

        ids, documents, metadatas = [], [], []
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                ids.append(row["id"])
                documents.append(row["description"])
                metadatas.append({
                    "title": row["title"],
                    "genre": row["genre"],
                    "platform": row["platform"],
                    "score": float(row["score"]),
                    "release_date": row["release_date"],
                    "monthly_clicks": int(row["monthly_clicks"]),
                })

        batch = 256
        for i in range(0, len(ids), batch):
            self.collection.add(
                ids=ids[i:i + batch],
                documents=documents[i:i + batch],
                metadatas=metadatas[i:i + batch],
            )
        print(f"[+] Loaded {len(ids)} games from {path}.")

    def _seed_samples(self):
        self.collection.add(
            ids=["game_001", "game_002", "game_003"],
            documents=[
                "Star Tactics. A complex sci-fi turn-based grand strategy game featuring squad resource management on PC.",
                "Shadow Runner. Fast paced tactical stealth ninja action game optimized for PS5 consoles.",
                "Cozy Valley. Relaxing farming simulator with friendly community elements, tailored for Nintendo Switch."
            ],
            metadatas=[
                {"title": "Star Tactics", "genre": "Strategy", "platform": "PC", "score": 0.9, "release_date": "2025-10-01", "monthly_clicks": 1500},
                {"title": "Shadow Runner", "genre": "Action", "platform": "PS5", "score": 0.85, "release_date": "2026-02-15", "monthly_clicks": 3400},
                {"title": "Cozy Valley", "genre": "Simulation", "platform": "Switch", "score": 0.95, "release_date": "2024-05-20", "monthly_clicks": 800}
            ]
        )
        print("[+] Loaded 3 sample games (fallback — no OMuleT CSV found).")

    def similarity_search(self, query: str, platforms: List[str] = None, genres: List[str] = None, top_k: int = 3) -> List[Any]:
        conditions = []
        if platforms:
            conditions.append({"platform": {"$in": platforms}})
        if genres:
            conditions.append({"genre": {"$in": genres}})
        if len(conditions) == 1:
            where = conditions[0]
        elif len(conditions) > 1:
            where = {"$and": conditions}
        else:
            where = None

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )

        if (not results or not results["ids"] or len(results["ids"][0]) == 0) and where is not None:
            # Metadata filter may have missed (e.g. genre/platform casing from
            # the intent parser); fall back to pure semantic search.
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
            )

        mock_docs = []
        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            return mock_docs

        class ChromaSyntheticDoc:
            def __init__(self, gid, content, meta):
                self.page_content = content
                self.metadata = {
                    "id": gid,
                    "title": meta.get("title"),
                    "genre": [meta.get("genre")] if isinstance(meta.get("genre"), str) else meta.get("genre"),
                    "platform": [meta.get("platform")] if isinstance(meta.get("platform"), str) else meta.get("platform"),
                    "score": meta.get("score", 0.0),
                    "release_date": meta.get("release_date"),
                    "monthly_clicks": meta.get("monthly_clicks")
                }

        for idx in range(len(results["ids"][0])):
            mock_docs.append(
                ChromaSyntheticDoc(
                    gid=results["ids"][0][idx],
                    content=results["documents"][0][idx],
                    meta=results["metadatas"][0][idx]
                )
            )
        return mock_docs
