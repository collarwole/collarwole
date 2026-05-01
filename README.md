# OT Modernization MCP Server

This repository now includes a production-oriented starter MCP server for Operational Technology (OT) modernization with AI safety guardrails.

## What it provides
- OT asset inventory tooling in AI-consumable normalized schema.
- Legacy-to-modern protocol transition recommendations (e.g., Modbus/DNP3 to OPC-UA/MQTT).
- Human-in-the-loop control intent creation (no unsafe direct actuation).
- MCP resources for safety guardrails and architecture references.

## Files
- `ot_mcp_server.py` - MCP server implementation.
- `DESIGN.md` - SDLC and AI architecture approach for industry-scale rollout.
- `requirements.txt` - Python dependency.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ot_mcp_server.py
```

## Core safety posture
- Backward compatibility is built in through protocol mapping strategies and compatibility notes.
- Human approval is required before control intents move toward execution.
- Unsafe states (`offline`, `maintenance`) are blocked from control intent acceptance.
