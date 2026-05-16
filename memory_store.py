from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, List

from schemas import Observation


class MemoryStore:
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.observations: Dict[str, Deque[Observation]] = defaultdict(lambda: deque(maxlen=window_size))
        self.route_estimates: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(dict)

    def add_observation(self, observation: Observation) -> None:
        self.observations[observation.system_id].append(observation)

    def get_observations(self, system_id: str) -> List[Observation]:
        return list(self.observations[system_id])

    def update_route_estimate(self, system_id: str, route: str, quality: float, cost: float) -> None:
        existing = self.route_estimates[system_id].get(route, {"quality": quality, "cost": cost, "count": 0.0})
        count = existing["count"] + 1.0
        existing["quality"] = ((existing["quality"] * existing["count"]) + quality) / count
        existing["cost"] = ((existing["cost"] * existing["count"]) + cost) / count
        existing["count"] = count
        self.route_estimates[system_id][route] = existing

    def get_route_estimates(self, system_id: str) -> Dict[str, Dict[str, float]]:
        return self.route_estimates[system_id]


store = MemoryStore()
