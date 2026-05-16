from __future__ import annotations

import asyncio
import random

from policy_engine import Policy
from schemas import ExecuteRequest, ExecutionResult


class ActionExecutor:
    async def run(self, action: str, request: ExecuteRequest, policy: Policy) -> ExecutionResult:
        if "PREMIUM" in action:
            return await self._premium_model(request)
        if action == "FALLBACK_TEMPLATE":
            return self._fallback(request)
        return await self._cheap_model(request)

    async def _cheap_model(self, request: ExecuteRequest) -> ExecutionResult:
        await asyncio.sleep(0.02)
        output = (
            f"I understand the issue. For this {request.task_type} request, "
            "here is a concise response that addresses the user's concern and offers next steps."
        )
        if request.risk_level.value == "high":
            output = "I understand. This needs careful review before a final response is sent."
        return ExecutionResult(
            selected_route="cheap_model",
            output=output,
            cost_estimate=0.004,
            latency_ms=random.randint(450, 1200),
            error=False,
        )

    async def _premium_model(self, request: ExecuteRequest) -> ExecutionResult:
        await asyncio.sleep(0.04)
        output = (
            f"I’m sorry this happened. For this {request.task_type} case, I can help resolve it carefully. "
            "I’ll acknowledge the issue, avoid overpromising, explain the next step, and escalate anything that "
            "requires policy or human review. Here is a safe, complete response tailored to the request: "
            f"{request.input}"
        )
        return ExecutionResult(
            selected_route="premium_model",
            output=output,
            cost_estimate=0.04,
            latency_ms=random.randint(900, 2200),
            error=False,
        )

    def _fallback(self, request: ExecuteRequest) -> ExecutionResult:
        return ExecutionResult(
            selected_route="safe_template_response",
            output="Thanks for reaching out. I’m going to route this for review so we can respond safely and accurately.",
            cost_estimate=0.0,
            latency_ms=50,
            error=False,
        )


action_executor = ActionExecutor()
