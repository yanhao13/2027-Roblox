import json
from typing import Dict, Any
from pydantic import BaseModel, Field
from monitoring import track_agent_latency


class ParsedIntentSchema(BaseModel):
    semantic_keywords: str = Field(description="Core gameplay styles, themes, or descriptive keywords.")
    platforms: list[str] = Field(default_factory=list, description="Target platforms explicitly requested.")
    genres: list[str] = Field(default_factory=list, description="Target game genres.")
    negative_constraints: list[str] = Field(default_factory=list, description="Themes or elements the user wants to avoid.")


class IntentParserAgent:
    """Implements the Intent Parsing Layer (Section 3.1)."""
    def __init__(self, llm_client: Any):
        self.llm = llm_client

    @track_agent_latency("intent_parser")
    def parse(self, raw_input: str, conversation_context: str = "") -> Dict[str, Any]:
        """Converts human prompts into machine-readable query criteria."""
        system_prompt = (
            "You are a structured parser extraction system. Analyze the user's game request "
            "and history logs to output a raw JSON object matching this schema: "
            "semantic_keywords (string), platforms (array of strings), genres (array of strings), negative_constraints (array of strings)."
        )

        user_packaged = f"History Logging Context:\n{conversation_context}\n\nCurrent User Request: '{raw_input}'"
        json_output = self.llm._call_structured_llm(system_prompt, user_packaged)

        try:
            parsed_data = json.loads(json_output)
            validated = ParsedIntentSchema(**parsed_data)
            return validated.model_dump()
        except Exception:
            return {"semantic_keywords": raw_input, "platforms": [], "genres": [], "negative_constraints": []}
