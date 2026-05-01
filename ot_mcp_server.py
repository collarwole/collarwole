#!/usr/bin/env python3
"""OT MCP Server: bridge legacy OT assets into AI-ready workflows safely.

This server exposes tools and resources oriented around:
- protocol translation metadata for legacy OT devices
- safety-gated control intents (human-in-the-loop)
- asset inventory normalization for analytics/AI pipelines

It is intentionally conservative: write/control operations require approval
and policy checks before execution.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("ot-mcp")

mcp = FastMCP(
    "ot-modernization-mcp",
    instructions=(
        "Safe OT modernization MCP server with backward-compatible protocol "
        "translation models, human-in-the-loop controls, and AI-ready context."
    ),
)


class DeviceState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class OTAsset:
    asset_id: str
    name: str
    vendor: str
    protocol: str
    model: str
    site: str
    firmware: str
    state: DeviceState = DeviceState.HEALTHY
    tags: List[str] = field(default_factory=list)


# In a production implementation, these would come from CMDB/asset APIs.
ASSET_DB: Dict[str, OTAsset] = {
    "plc-001": OTAsset(
        asset_id="plc-001",
        name="Boiler PLC #1",
        vendor="Siemens",
        protocol="modbus-tcp",
        model="S7-1200",
        site="Plant-A",
        firmware="4.5.2",
        tags=["critical", "safety-loop"],
    ),
    "rtu-041": OTAsset(
        asset_id="rtu-041",
        name="Pipeline RTU #41",
        vendor="Schneider",
        protocol="dnp3",
        model="SCADAPack",
        site="Field-West",
        firmware="8.1.1",
        state=DeviceState.DEGRADED,
        tags=["legacy", "remote"],
    ),
}


PROTOCOL_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "modbus-tcp": {
        "modern_interface": "opc-ua",
        "mapping_strategy": "register-to-namespace",
        "security_notes": "Wrap in TLS gateway and signed command policy",
        "backward_compatibility": "Preserve register semantics and polling cadence",
    },
    "dnp3": {
        "modern_interface": "mqtt-sparkplug-b",
        "mapping_strategy": "point-class-to-topic",
        "security_notes": "Use secure authentication and sequence integrity checks",
        "backward_compatibility": "Maintain unsolicited response handling",
    },
    "profibus": {
        "modern_interface": "opc-ua",
        "mapping_strategy": "fieldbus-segment gateway",
        "security_notes": "Segmentation plus protocol firewall",
        "backward_compatibility": "Deterministic cycle timing constraints retained",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@mcp.tool(
    description=(
        "Return OT asset inventory in a normalized, AI-consumable schema. "
        "Use this for model context and modernization planning."
    )
)
def list_assets(site: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
    records = list(ASSET_DB.values())
    if site:
        records = [a for a in records if a.site.lower() == site.lower()]
    if state:
        records = [a for a in records if a.state.value == state.lower()]

    return [
        {
            "asset_id": a.asset_id,
            "name": a.name,
            "vendor": a.vendor,
            "model": a.model,
            "site": a.site,
            "protocol": a.protocol,
            "firmware": a.firmware,
            "state": a.state.value,
            "tags": a.tags,
        }
        for a in records
    ]


@mcp.tool(
    description=(
        "Provide a legacy-to-modern protocol transition design with safety notes "
        "and compatibility constraints."
    )
)
def recommend_protocol_transition(protocol: str) -> Dict[str, Any]:
    key = protocol.lower()
    if key not in PROTOCOL_MAPPINGS:
        return {
            "protocol": protocol,
            "supported": False,
            "message": "No baseline mapping found. Create a custom adapter profile.",
        }
    return {
        "protocol": key,
        "supported": True,
        **PROTOCOL_MAPPINGS[key],
        "generated_at": utc_now(),
    }


@mcp.tool(
    description=(
        "Create a control intent packet. Does not execute by default. "
        "Requires human approval and policy compliance before execution."
    )
)
def create_control_intent(
    asset_id: str,
    action: str,
    value: str,
    operator: str,
    require_human_approval: bool = True,
) -> Dict[str, Any]:
    asset = ASSET_DB.get(asset_id)
    if not asset:
        return {"accepted": False, "reason": "Unknown asset_id"}

    if asset.state in {DeviceState.OFFLINE, DeviceState.MAINTENANCE}:
        return {
            "accepted": False,
            "reason": f"Asset is in {asset.state.value} state; control blocked",
        }

    risk = "high" if "safety-loop" in asset.tags else "medium"
    control_packet = {
        "intent_id": f"intent-{asset_id}-{int(datetime.now().timestamp())}",
        "asset_id": asset_id,
        "asset_protocol": asset.protocol,
        "action": action,
        "value": value,
        "operator": operator,
        "risk": risk,
        "require_human_approval": require_human_approval,
        "status": "pending_approval" if require_human_approval else "policy_review",
        "created_at": utc_now(),
    }
    return {"accepted": True, "control_intent": control_packet}


@mcp.resource("ot://safety/guardrails")
def safety_guardrails() -> str:
    return json.dumps(
        {
            "version": "1.0",
            "principles": [
                "Never bypass SIS/ESD controls via MCP pathways",
                "Require human approval for all control-plane writes",
                "Enforce allow-list actions per asset criticality",
                "Validate command bounds with engineering setpoints",
                "Fail closed on telemetry uncertainty",
                "Log every read/write decision for auditability",
            ],
            "last_reviewed_utc": utc_now(),
        },
        indent=2,
    )


@mcp.resource("ot://architecture/reference")
def architecture_reference() -> str:
    return json.dumps(
        {
            "layers": {
                "edge": "Protocol adapters for Modbus/DNP3/Profibus to OPC-UA/MQTT",
                "broker": "Event and command broker with schema validation",
                "policy": "Safety engine + role-based authorization + human approval",
                "ai": "Context enrichment for anomaly detection and optimization models",
                "observability": "Tamper-evident logs, traces, and OT SOC integration",
            },
            "compatibility": {
                "legacy_preservation": "Timing, register semantics, and alarm workflows retained",
                "migration_strategy": "Parallel-run + digital twin validation before cutover",
            },
            "timestamp": utc_now(),
        },
        indent=2,
    )


async def main() -> None:
    logger.info("Starting OT MCP server")
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
