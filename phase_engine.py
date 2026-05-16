from __future__ import annotations

from schemas import DecisionTrace, ExecuteRequest, Phase, RuntimeState


RISK_WEIGHT = {"low": 0.15, "medium": 0.45, "high": 0.85}


class PhaseEngine:
    def decide(self, request: ExecuteRequest, state: RuntimeState) -> tuple[Phase, DecisionTrace]:
        risk = RISK_WEIGHT[request.risk_level.value]
        uncertainty = 1.0 - state.avg_quality
        instability_pressure = min(1.0, state.instability_duration / 8.0)
        failure_pressure = state.failure_rate

        crystal_score = state.stability_score * state.efficiency_score * (1.0 - risk)
        flower_score = max(0.05, uncertainty + (0.35 if request.risk_level.value == "medium" else 0.0)) * (1.0 - failure_pressure)
        flame_score = max(risk * 0.55, instability_pressure * 0.85, failure_pressure * 0.95)

        reason: list[str] = []
        if state.instability_duration >= 4:
            reason.append("sustained instability detected")
        if state.failure_rate >= 0.20:
            reason.append("failure pressure elevated")
        if request.risk_level.value == "high":
            reason.append("high risk request")
        if state.efficiency_score >= 0.80 and request.risk_level.value == "low":
            reason.append("stable low-risk efficient path")
        if request.risk_level.value == "medium":
            reason.append("medium risk supports monitored exploration")

        if flame_score >= 0.62 or state.instability_duration >= 5:
            phase = Phase.FLAME
        elif flower_score >= crystal_score or request.risk_level.value == "medium":
            phase = Phase.FLOWER
        else:
            phase = Phase.CRYSTAL

        if not reason:
            reason.append("default adaptive routing decision")

        return phase, DecisionTrace(
            reason=reason,
            crystal_score=round(crystal_score, 4),
            flower_score=round(flower_score, 4),
            flame_score=round(flame_score, 4),
        )


phase_engine = PhaseEngine()
