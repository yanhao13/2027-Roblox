from typing import List, Dict
from pydantic import BaseModel


class ChatTurn(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class SessionMemoryManager:
    """Manages sliding-window conversation histories bound to specific session IDs to establish continuity."""
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.registry: Dict[str, List[ChatTurn]] = {}

    def get_session(self, session_id: str) -> List[ChatTurn]:
        if session_id not in self.registry:
            self.registry[session_id] = []
        return self.registry[session_id]

    def add_turn(self, session_id: str, role: str, content: str):
        history = self.get_session(session_id)
        history.append(ChatTurn(role=role, content=content))

        if len(history) > self.window_size * 2:
            self.registry[session_id] = history[-(self.window_size * 2):]

    def format_as_context(self, session_id: str) -> str:
        history = self.get_session(session_id)
        if not history:
            return "No prior conversation history."

        formatted_turns = []
        for turn in history:
            prefix = "User Request" if turn.role == "user" else "System Response"
            formatted_turns.append(f"{prefix}: {turn.content}")
        return "\n".join(formatted_turns)
