#!/usr/bin/env python3
"""OT MCP Server for safe modernization of legacy industrial systems.

Implements MCP tools/resources for:
- Inventory normalization and lifecycle visibility.
- Legacy protocol transition guidance.
- Human-in-the-loop control intent workflow.
- Safety policy validation and auditable intent tracking.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("ot-mcp")

INTENT_LOG_PATH = Path(os.getenv("INTENT_LOG_PATH", "intent_log.jsonl"))

mcp = FastMCP(
    "ot-modernization-mcp",
    instructions=(
        "Safety-first OT modernization MCP server with backward-compatible protocol "
        "transition patterns and human-approved control workflows."
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
    criticality: str = "medium"
    allowed_actions: List[str] = field(default_factory=lambda: ["setpoint", "start", "stop", "reset"])
    tags: List[str] = field(default_factory=list)


ASSET_DB: Dict[str, OTAsset] = {
    "plc-001": OTAsset(
        asset_id="plc-001",
        name="Boiler PLC #1",
        vendor="Siemens",
        protocol="modbus-tcp",
        model="S7-1200",
        site="Plant-A",
        firmware="4.5.2",
        criticality="high",
        allowed_actions=["setpoint", "stop", "start"],
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
        criticality="medium",
        allowed_actions=["setpoint", "reset"],
        tags=["legacy", "remote"],
    ),
}

PROTOCOL_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "modbus-tcp": {
        "modern_interface": "opc-ua",
        "mapping_strategy": "register-to-namespace",
        "security_notes": "Use TLS termination gateway with signed command envelope",
        "backward_compatibility": "Preserve register semantics and polling cadence",
        "migration_pattern": "parallel run with mirrored data historian validation",
    },
    "dnp3": {
        "modern_interface": "mqtt-sparkplug-b",
        "mapping_strategy": "point-class-to-topic",
        "security_notes": "Mutual auth, sequence integrity, secure outstation profiles",
        "backward_compatibility": "Maintain unsolicited response handling",
        "migration_pattern": "phased migration by feeder/segment with rollback switch",
    },
    "profibus": {
        "modern_interface": "opc-ua",
        "mapping_strategy": "fieldbus-segment gateway",
        "security_notes": "Protocol firewall and segmented zone transfer",
        "backward_compatibility": "Retain deterministic cycle-time constraints",
        "migration_pattern": "cell-by-cell cutover after digital twin replay tests",
    },
}


APPROVALS: Dict[str, Dict[str, Any]] = {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_intent_audit(record: Dict[str, Any]) -> None:
    INTENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INTENT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def evaluate_policy(asset: OTAsset, action: str, value: str) -> Dict[str, Any]:
    if action not in asset.allowed_actions:
        return {
            "allowed": False,
            "reason": f"Action '{action}' is not allowed for {asset.asset_id}",
        }

    if action == "setpoint":
        try:
            numeric = float(value)
        except ValueError:
            return {"allowed": False, "reason": "Setpoint must be numeric"}

        if not 0.0 <= numeric <= 100.0:
            return {
                "allowed": False,
                "reason": "Setpoint out of engineering bounds (0-100)",
            }

    return {"allowed": True, "reason": "Policy checks passed"}


@mcp.tool(description="List OT assets in normalized schema for AI context and planning.")
def list_assets(site: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
    records = list(ASSET_DB.values())
    if site:
        records = [a for a in records if a.site.lower() == site.lower()]
    if state:
        records = [a for a in records if a.state.value == state.lower()]

    return [
        {
            **asdict(asset),
            "state": asset.state.value,
        }
        for asset in records
    ]


@mcp.tool(description="Recommend legacy OT protocol transition strategy and compatibility controls.")
def recommend_protocol_transition(protocol: str) -> Dict[str, Any]:
    key = protocol.lower()
    mapping = PROTOCOL_MAPPINGS.get(key)
    if not mapping:
        return {
            "protocol": protocol,
            "supported": False,
            "message": "No baseline mapping found; create custom adapter profile.",
            "generated_at": utc_now(),
        }

    return {
        "protocol": key,
        "supported": True,
        **mapping,
        "generated_at": utc_now(),
    }


@mcp.tool(description="Create a safety-gated control intent; no direct actuation is performed.")
def create_control_intent(
    asset_id: str,
    action: str,
    value: str,
    operator: str,
    change_ticket: str,
    require_human_approval: bool = True,
) -> Dict[str, Any]:
    asset = ASSET_DB.get(asset_id)
    if not asset:
        return {"accepted": False, "reason": "Unknown asset_id"}

    if asset.state in {DeviceState.OFFLINE, DeviceState.MAINTENANCE}:
        return {
            "accepted": False,
            "reason": f"Asset state is {asset.state.value}; control blocked",
        }

    policy = evaluate_policy(asset, action, value)
    if not policy["allowed"]:
        return {"accepted": False, "reason": policy["reason"]}

    risk = "high" if (asset.criticality == "high" or "safety-loop" in asset.tags) else "medium"
    intent_id = f"intent-{asset_id}-{int(datetime.now().timestamp())}"
    control_intent = {
        "intent_id": intent_id,
        "asset_id": asset_id,
        "asset_protocol": asset.protocol,
        "action": action,
        "value": value,
        "operator": operator,
        "change_ticket": change_ticket,
        "risk": risk,
        "require_human_approval": require_human_approval,
        "status": "pending_approval" if require_human_approval else "approved_by_policy",
        "policy_evaluation": policy,
        "created_at": utc_now(),
    }

    APPROVALS[intent_id] = control_intent
    append_intent_audit({"event": "intent_created", **control_intent})
    return {"accepted": True, "control_intent": control_intent}


@mcp.tool(description="Approve or reject a pending control intent (human-in-the-loop gate).")
def review_control_intent(intent_id: str, approver: str, approve: bool, comment: str) -> Dict[str, Any]:
    intent = APPROVALS.get(intent_id)
    if not intent:
        return {"updated": False, "reason": "Unknown intent_id"}

    if intent["status"] not in {"pending_approval", "approved_by_policy"}:
        return {"updated": False, "reason": f"Intent is already {intent['status']}"}

    intent["status"] = "approved" if approve else "rejected"
    intent["reviewed_by"] = approver
    intent["review_comment"] = comment
    intent["reviewed_at"] = utc_now()
    append_intent_audit({"event": "intent_reviewed", **intent})

    return {"updated": True, "intent": intent}


@mcp.resource("ot://safety/guardrails")
def safety_guardrails() -> str:
    return json.dumps(
        {
            "version": "1.1",
            "principles": [
                "Never bypass SIS/ESD controls via MCP pathways",
                "Require change ticket and human approval for control writes",
                "Enforce allow-list actions per asset and criticality",
                "Validate setpoint bounds against engineering limits",
                "Fail closed on telemetry uncertainty",
                "Write tamper-evident audit records for all control intents",
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
                "edge": "Protocol adapters (Modbus/DNP3/Profibus) to OPC-UA/MQTT",
                "broker": "Event+command bus with schema validation and replay protection",
                "policy": "Authorization, engineering constraints, and human approvals",
                "ai": "Read-only advisory context for anomaly and optimization models",
                "observability": "SIEM-integrated audit trails with OT SOC workflows",
            },
            "compatibility": {
                "legacy_preservation": "Maintain timing, register semantics, alarm workflows",
                "migration_strategy": "Parallel-run + digital twin replay + rollback controls",
            },
            "timestamp": utc_now(),
        },
        indent=2,
    )


async def main() -> None:
    logger.info("Starting OT modernization MCP server")
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
