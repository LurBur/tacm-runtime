from __future__ import annotations

from fastapi import FastAPI

from observation_buffer import observation_buffer
from runtime import execute_tacm_request
from schemas import ExecuteRequest, ExecuteResponse, RuntimeState


app = FastAPI(
    title="TACM Runtime API",
    version="3.0.0",
    description="Autonomous adaptive-control runtime for AI routing, evaluation, and feedback learning.",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "TACM Runtime API",
        "version": "3.0.0",
        "core_loop": "observe -> decide -> act -> evaluate -> learn",
        "execute_endpoint": "/v3/execute",
    }


@app.post("/v3/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest) -> ExecuteResponse:
    return await execute_tacm_request(request)


@app.get("/v3/state/{system_id}", response_model=RuntimeState)
def get_state(system_id: str) -> RuntimeState:
    return observation_buffer.get_state(system_id)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
