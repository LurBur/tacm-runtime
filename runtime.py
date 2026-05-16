from __future__ import annotations

from action_executor import action_executor
from evaluator import evaluator
from observation_buffer import observation_buffer
from phase_engine import phase_engine
from policy_engine import policy_engine
from schemas import ExecuteRequest, ExecuteResponse, Observation


PREMIUM_BASELINE_COST = 0.04


async def execute_tacm_request(request: ExecuteRequest) -> ExecuteResponse:
    state_before = observation_buffer.get_state(request.system_id)
    phase, decision_trace = phase_engine.decide(request, state_before)
    policy = policy_engine.load(request.policy_id)
    action = policy_engine.choose_action(phase, request, state_before, policy)

    result = await action_executor.run(action, request, policy)
    evaluation = await evaluator.score(request, result)

    observation = Observation(
        task_id=request.task_id,
        system_id=request.system_id,
        task_type=request.task_type,
        risk_level=request.risk_level,
        phase=phase,
        action_taken=action,
        selected_route=result.selected_route,
        cost_estimate=result.cost_estimate,
        latency_ms=result.latency_ms,
        quality_score=evaluation.quality_score,
        error=result.error or not evaluation.passed,
    )
    state_after = observation_buffer.update(observation)

    return ExecuteResponse(
        task_id=request.task_id,
        phase=phase,
        action_taken=action,
        selected_route=result.selected_route,
        output=result.output,
        quality_score=evaluation.quality_score,
        cost_estimate=result.cost_estimate,
        cost_saved_estimate=round(max(0.0, PREMIUM_BASELINE_COST - result.cost_estimate), 6),
        state=state_after,
        decision_trace=decision_trace,
    )
