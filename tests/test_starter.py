"""[starter] checks: these pass BEFORE you change anything.

They confirm the chatbot already works: it talks through the LLM, keeps its
Tutorial 1 state, starts the clinic MCP server and connects to it.
"""
from conftest import run, say

from backend import orchestrator as orch
from backend.content import NO_LLM_MESSAGE


def test_starter_chat_still_works_without_tools(fake):
    fake(say(updates={"reason_for_visit": "exams"}, reply="How long have you felt this way?"))
    state = orch.new_state()
    assert run(orch.handle("Stressed about exams", state)) == "How long have you felt this way?"
    assert state["current_step"] == "duration"


def test_starter_state_has_tool_fields():
    state = orch.new_state()
    assert state["last_tool"] is None and state["booking"] is None


def test_starter_no_llm_configured():
    assert run(orch.handle("hi", orch.new_state())) == NO_LLM_MESSAGE


def test_starter_app_starts_and_connects_to_the_server():
    """Starts the real server as a subprocess, over stdio, like `uvicorn` does."""
    from fastapi.testclient import TestClient
    from backend.app import app

    with TestClient(app) as client:
        body = client.post("/api/reset", json={"session_id": "s"}).json()
    assert body["mcp"]["connected"] is True
