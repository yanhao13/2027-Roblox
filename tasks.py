import os
import asyncio
from celery import Celery
from database import GameVectorDatabase
from ingest_catalog import GameCatalogMigrator

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("matcha_workers", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(name="tasks.trigger_catalog_migration")
def trigger_catalog_migration(pages_to_pull: int = 2, api_key: str = "prod_secret_key"):
    """Asynchronous Celery execution wrapper invoking full async catalog migrations."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    db_inst = GameVectorDatabase()
    migrator = GameCatalogMigrator(db_inst)
    loop.run_until_complete(migrator.fetch_and_migrate_rawg(api_key=api_key, pages_to_pull=pages_to_pull))
    return {"status": "COMPLETED", "processed_batches": pages_to_pull}
