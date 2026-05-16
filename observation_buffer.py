from __future__ import annotations

from collections import Counter
from typing import List

from memory_store import store
from schemas import Observation, RuntimeState


def _avg(values: List[float], default: float) -> float:
    return sum(values) / len(values) if values else default


class ObservationBuffer:
    def get_state(self, system_id: str) -> RuntimeState:
        observations = store.get_observations(system_id)
        if not observations:
            return RuntimeState(
                stability_score=0.75,
                efficiency_score=0.75,
                failure_rate=0.0,
                instability_duration=0,
                phase_distribution={"CRYSTAL": 0, "FLOWER": 0, "FLAME": 0},
                avg_cost=0.0,
                avg_latency_ms=0.0,
                avg_quality=0.80,
                window_size=0,
            )

        costs = [obs.cost_estimate for obs in observations]
        latencies = [float(obs.latency_ms) for obs in observations]
        qualities = [obs.quality_score for obs in observations]
        failures = [1.0 if obs.error or obs.quality_score < 0.70 else 0.0 for obs in observations]
        phase_counts = Counter(obs.phase.value for obs in observations)

        avg_cost = _avg(costs, 0.0)
        avg_latency = _avg(latencies, 0.0)
        avg_quality = _avg(qualities, 0.80)
        failure_rate = _avg(failures, 0.0)

        instability_duration = 0
        for obs in reversed(observations):
            unstable = obs.error or obs.quality_score < 0.76 or obs.phase.value == "FLAME"
            if unstable:
                instability_duration += 1
            else:
                break

        recent = observations[-10:]
        older = observations[-20:-10]
        recent_quality = _avg([obs.quality_score for obs in recent], avg_quality)
        older_quality = _avg([obs.quality_score for obs in older], avg_quality)
        recent_cost = _avg([obs.cost_estimate for obs in recent], avg_cost)
        older_cost = _avg([obs.cost_estimate for obs in older], avg_cost)

        quality_decline = max(0.0, older_quality - recent_quality)
        cost_growth = max(0.0, recent_cost - older_cost)
        efficiency_penalty = min(0.45, quality_decline + (cost_growth * 5.0) + (failure_rate * 0.35))

        efficiency_score = max(0.0, min(1.0, avg_quality - efficiency_penalty))
        stability_score = max(0.0, min(1.0, 1.0 - failure_rate - min(0.35, instability_duration * 0.04)))

        return RuntimeState(
            stability_score=round(stability_score, 4),
            efficiency_score=round(efficiency_score, 4),
            failure_rate=round(failure_rate, 4),
            instability_duration=instability_duration,
            phase_distribution={
                "CRYSTAL": phase_counts.get("CRYSTAL", 0),
                "FLOWER": phase_counts.get("FLOWER", 0),
                "FLAME": phase_counts.get("FLAME", 0),
            },
            avg_cost=round(avg_cost, 6),
            avg_latency_ms=round(avg_latency, 2),
            avg_quality=round(avg_quality, 4),
            window_size=len(observations),
        )

    def update(self, observation: Observation) -> RuntimeState:
        store.add_observation(observation)
        store.update_route_estimate(
            observation.system_id,
            observation.selected_route,
            observation.quality_score,
            observation.cost_estimate,
        )
        return self.get_state(observation.system_id)


observation_buffer = ObservationBuffer()
