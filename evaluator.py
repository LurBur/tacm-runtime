from __future__ import annotations

from schemas import EvaluationResult, ExecuteRequest, ExecutionResult


class Evaluator:
    async def score(self, request: ExecuteRequest, result: ExecutionResult) -> EvaluationResult:
        text = result.output.lower().strip()
        score = 0.50
        reason: list[str] = []

        if len(text) > 80:
            score += 0.12
            reason.append("response has useful length")
        if any(word in text for word in ["sorry", "understand", "help", "resolve", "next step"]):
            score += 0.15
            reason.append("response contains helpful support language")
        if request.task_type.lower() in text:
            score += 0.08
            reason.append("response references task type")
        if request.risk_level.value == "high" and result.selected_route == "premium_model":
            score += 0.12
            reason.append("high risk routed to premium path")
        if request.risk_level.value == "high" and result.selected_route == "cheap_model":
            score -= 0.18
            reason.append("high risk used cheap path")
        if result.error:
            score -= 0.35
            reason.append("execution error detected")
        if result.cost_estimate <= 0.004 and request.risk_level.value == "low":
            score += 0.05
            reason.append("low-risk task handled efficiently")

        score = max(0.0, min(1.0, score))
        passed = score >= 0.75
        if not reason:
            reason.append("basic deterministic quality estimate")

        return EvaluationResult(quality_score=round(score, 4), passed=passed, reason=reason)


evaluator = Evaluator()
