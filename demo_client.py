from __future__ import annotations

import requests


TASKS = [
    ("support", "Write a friendly refund response for a delayed shipment.", "low"),
    ("support", "Customer says their package arrived damaged and wants replacement.", "medium"),
    ("support", "Customer threatens legal action over billing dispute.", "high"),
    ("sales", "Draft a short response to a pricing question.", "low"),
    ("support", "Customer asks to cancel subscription after failed login.", "medium"),
    ("compliance", "User asks for advice that may violate policy.", "high"),
    ("support", "Customer wants tracking update.", "low"),
    ("support", "Refund request after failed shipment.", "medium"),
    ("billing", "Chargeback complaint with angry language.", "high"),
    ("support", "Ask customer for order number politely.", "low"),
] * 2


def main() -> None:
    total_cost = 0.0
    baseline_cost = 0.0
    total_saved = 0.0

    for i, (task_type, text, risk) in enumerate(TASKS, start=1):
        payload = {
            "system_id": "demo",
            "task_type": task_type,
            "input": text,
            "risk_level": risk,
            "policy_id": "balanced",
        }
        response = requests.post("http://127.0.0.1:8080/v3/execute", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        total_cost += data["cost_estimate"]
        baseline_cost += 0.04
        total_saved += data["cost_saved_estimate"]

        print(
            f"{i:02d} | risk={risk:<6} | phase={data['phase']:<7} | "
            f"route={data['selected_route']:<13} | quality={data['quality_score']:.2f} | "
            f"saved=${data['cost_saved_estimate']:.3f} | instability={data['state']['instability_duration']}"
        )

    print("\nDemo complete")
    print(f"All-premium baseline: ${baseline_cost:.3f}")
    print(f"TACM routed cost:     ${total_cost:.3f}")
    print(f"Estimated savings:   ${total_saved:.3f}")


if __name__ == "__main__":
    main()
