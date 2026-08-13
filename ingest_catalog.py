import httpx
from database import GameVectorDatabase


class GameCatalogMigrator:
    """Connects to external dataset feeds to populate and index the ChromaDB library."""
    def __init__(self, db_wrapper: GameVectorDatabase):
        self.db = db_wrapper

    async def fetch_and_migrate_rawg(self, api_key: str = "sample_rawg_key", pages_to_pull: int = 1):
        # NOTE: corrected the RAWG endpoint — the public API lives at
        # api.rawg.io/api/games (not the rawg.io marketing homepage).
        base_url = "https://api.rawg.io/api/games"
        async with httpx.AsyncClient() as client:
            for page in range(1, pages_to_pull + 1):
                try:
                    params = {"key": api_key, "page": page, "page_size": 10}
                    response = await client.get(base_url, params=params, timeout=10.0)
                    if response.status_code != 200:
                        continue

                    games_list = response.json().get("results", [])
                    for game in games_list:
                        game_id = f"rawg_{game.get('id')}"
                        title = game.get("name", "Unknown Game")
                        genres = [g.get("name") for g in game.get("genres", []) if g.get("name")]
                        platforms = [p.get("platform", {}).get("name") for p in game.get("platforms", []) if p.get("platform", {}).get("name")]
                        description_blob = f"{title}. Genres: {', '.join(genres)}. Platforms: {', '.join(platforms)}."

                        if not genres or not platforms:
                            continue

                        self.db.collection.add(
                            ids=[game_id],
                            documents=[description_blob],
                            metadatas=[{
                                "title": title,
                                "genre": genres[0],
                                "platform": platforms[0],
                                "score": float(game.get("rating", 4.0) / 5.0),
                                "release_date": game.get("released", "2025-01-01"),
                                "monthly_clicks": int(game.get("ratings_count", 500))
                            }]
                        )
                except Exception as e:
                    print(f"[!] Migration Anomaly: {str(e)}")
