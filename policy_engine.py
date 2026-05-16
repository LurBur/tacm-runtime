from __future__ import annotations

from dataclasses import dataclass

from schemas import ExecuteRequest, Phase, RuntimeState


@dataclass(frozen=True)
class Policy:
    policy_id: str
    max_cost_per_call: float
    min_quality_score: float
    max_latency_ms: int
    allow_exploration: bool
    exploration_rate: float
    flame_escalation_route: str
    fallback_route: str


POLICIES = {
    "balanced": Policy(
        policy_id="balanced",
        max_cost_per_call=0.05,
        min_quality_score=0.80,
        max_latency_ms=5000,
        allow_exploration=True,
        exploration_rate=0.12,
        flame_escalation_route="premium_model",
        fallback_route="safe_template_response",
    )
}


class PolicyEngine:
    def load(self, policy_id: str) -> Policy:
        return POLICIES.get(policy_id, POLICIES["balanced"])

    def choose_action(self, phase: Phase, request: ExecuteRequest, state: RuntimeState, policy: Policy) -> str:
        if phase == Phase.FLAME:
            return "ROUTE_PREMIUM_AND_RUN_EVALUATOR"

        if phase == Phase.FLOWER:
            if request.risk_level.value == "high" or state.instability_duration >= 3:
                return "ROUTE_PREMIUM_AND_RUN_EVALUATOR"
            return "ROUTE_CHEAP_WITH_EVALUATION"

        if request.risk_level.value == "high":
            return "ROUTE_PREMIUM_AND_RUN_EVALUATOR"
        return "ROUTE_CHEAP"


policy_engine = PolicyEngine()
