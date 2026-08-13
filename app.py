from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from main import MatchPipelineOrchestrator
from database import GameVectorDatabase
from llm_client import DeepSeekPipelineClient
from memory import SessionMemoryManager
from tasks import trigger_catalog_migration
from monitoring import PIPELINE_REQUESTS


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., example="player_101")
    prompt: str = Field(..., max_length=500, example="I want an immersive strategy experience on PC.")


class RecommendationResponse(BaseModel):
    status: str
    message: str
    data: dict | None = None


app = FastAPI(title="MATCHA Agent Recommendation Service", version="1.0.0")
db_client = GameVectorDatabase()
db_client.seed_initial_catalog()
live_llm = DeepSeekPipelineClient()
pipeline = MatchPipelineOrchestrator(llm_client=live_llm, vector_store=db_client)
memory = SessionMemoryManager()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/recommend", response_model=RecommendationResponse)
async def generate_recommendation(payload: RecommendationRequest):
    try:
        context_str = memory.format_as_context(payload.user_id)
        execution_state = pipeline.execute_recommendation(
            user_id=payload.user_id, user_prompt=payload.prompt, context_history=context_str
        )
        rec_data = execution_state.final_recommendation

        if rec_data["status"] == "BLOCKED":
            PIPELINE_REQUESTS.labels(status="SAFETY_VIOLATION").inc()
            return RecommendationResponse(status="SAFETY_VIOLATION", message=rec_data["message"], data=execution_state.risk_report)

        if rec_data["status"] == "EMPTY":
            PIPELINE_REQUESTS.labels(status="EMPTY").inc()
            return RecommendationResponse(status="NO_MATCHES", message=rec_data["message"])

        # Track history context frames upon success balances
        memory.add_turn(payload.user_id, "user", payload.prompt)
        memory.add_turn(payload.user_id, "assistant", rec_data["payload"]["explanation"])

        PIPELINE_REQUESTS.labels(status="SUCCESS").inc()
        return RecommendationResponse(status="SUCCESS", message="Match identified.", data=rec_data["payload"])
    except Exception as e:
        PIPELINE_REQUESTS.labels(status="ERROR").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admin/sync-catalog", status_code=202)
async def sync_game_catalog(pages: int = 2):
    task_handle = trigger_catalog_migration.delay(pages_to_pull=pages)
    return {"status": "QUEUED", "task_id": task_handle.id}
