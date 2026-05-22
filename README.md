# OT Modernization MCP Server

Production-oriented MCP server for Operational Technology (OT) modernization that keeps **legacy compatibility**, **safety guardrails**, and **human-in-the-loop controls** as first-class architecture requirements.

## Core capabilities
- Normalized OT asset inventory for AI/model context.
- Legacy-to-modern protocol transition recommendations.
- Safety-gated control intent creation (no direct actuation).
- Human approval/rejection workflow for control intents.
- Auditable JSONL intent lifecycle logging.

## Project files
- `ot_mcp_server.py` — MCP server implementation.
- `DESIGN.md` — SDLC and AI architecture guidance.
- `tests/test_ot_mcp_server.py` — policy and approval workflow tests.
- `requirements.txt` — runtime and test dependencies.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ot_mcp_server.py
```

## Safety posture
- All control requests are modeled as intents and policy-validated.
- Offline/maintenance assets are blocked from control operations.
- Change-ticket and operator identity are required for control intents.
- Human approval is expected before execution in plant systems.

## Testing
```bash
python -m py_compile ot_mcp_server.py
pytest -q
```
