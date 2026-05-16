from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Phase(str, Enum):
    CRYSTAL = "CRYSTAL"
    FLOWER = "FLOWER"
    FLAME = "FLAME"


class ExecuteRequest(BaseModel):
    system_id: str = Field(..., min_length=1)
    task_type: str = Field(default="general")
    input: str = Field(..., min_length=1)
    risk_level: RiskLevel = RiskLevel.medium
    policy_id: str = "balanced"
    task_id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:10]}")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuntimeState(BaseModel):
    stability_score: float
    efficiency_score: float
    failure_rate: float
    instability_duration: int
    phase_distribution: Dict[str, int]
    avg_cost: float
    avg_latency_ms: float
    avg_quality: float
    window_size: int


class DecisionTrace(BaseModel):
    reason: List[str]
    crystal_score: float
    flower_score: float
    flame_score: float


class ExecuteResponse(BaseModel):
    task_id: str
    phase: Phase
    action_taken: str
    selected_route: str
    output: str
    quality_score: float
    cost_estimate: float
    cost_saved_estimate: float
    state: RuntimeState
    decision_trace: DecisionTrace


class ExecutionResult(BaseModel):
    selected_route: str
    output: str
    cost_estimate: float
    latency_ms: int
    error: bool = False


class EvaluationResult(BaseModel):
    quality_score: float
    passed: bool
    reason: List[str]


class Observation(BaseModel):
    task_id: str
    system_id: str
    task_type: str
    risk_level: RiskLevel
    phase: Phase
    action_taken: str
    selected_route: str
    cost_estimate: float
    latency_ms: int
    quality_score: float
    error: bool
