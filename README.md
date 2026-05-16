# TACM Runtime API

TACM Runtime V3.0 is an autonomous adaptive-control layer for AI/model/tool calls.

It implements the loop:

```txt
Observe -> Decide -> Act -> Evaluate -> Learn
```

Instead of sending app requests directly to one model, the app sends requests to TACM first. TACM selects the route, executes the route, evaluates the result, stores the observation, and updates future behavior.

## Current V3.0 Seed

This first build is intentionally narrow:

- FastAPI runtime
- One main endpoint: `POST /v3/execute`
- In-memory rolling observation buffer
- Phase engine: CRYSTAL / FLOWER / FLAME
- Policy engine with a built-in `balanced` policy
- Mock cheap and premium model routes
- Deterministic evaluator
- Cost savings estimate versus all-premium routing
- Demo client with 20 support-style tasks

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run API

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8080
```

Open:

```txt
http://127.0.0.1:8080/docs
```

## Test Execute Endpoint

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8080/v3/execute `
  -ContentType "application/json" `
  -Body '{
    "system_id": "demo",
    "task_type": "support",
    "input": "Customer wants a refund after failed shipment.",
    "risk_level": "medium",
    "policy_id": "balanced"
  }'
```

## Run Demo

In a second terminal, with the API running:

```powershell
.\.venv\Scripts\activate
python demo_client.py
```

Expected behavior:

- low-risk calls route cheaper
- medium-risk calls route cheap with evaluation
- high-risk calls escalate to premium
- state updates after every call
- phase distribution changes over time
- estimated savings are printed at the end

## Product Claim

TACM Runtime automatically routes AI calls by risk, instability, and cost, reducing model spend while escalating risky calls before failure.

## Next Build Step

Replace mock routes with one OpenAI-compatible provider interface while preserving the same TACM control loop.
