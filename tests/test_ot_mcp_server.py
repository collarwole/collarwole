from ot_mcp_server import (
    APPROVALS,
    DeviceState,
    OTAsset,
    create_control_intent,
    evaluate_policy,
    review_control_intent,
)


def test_evaluate_policy_blocks_bad_setpoint() -> None:
    asset = OTAsset(
        asset_id="x",
        name="x",
        vendor="x",
        protocol="modbus-tcp",
        model="x",
        site="x",
        firmware="x",
    )
    result = evaluate_policy(asset, "setpoint", "200")
    assert result["allowed"] is False


def test_intent_lifecycle_approval() -> None:
    created = create_control_intent(
        asset_id="plc-001",
        action="setpoint",
        value="50",
        operator="ops-a",
        change_ticket="CHG-1001",
        require_human_approval=True,
    )
    assert created["accepted"] is True
    intent_id = created["control_intent"]["intent_id"]

    reviewed = review_control_intent(intent_id, "supervisor", True, "approved during shift")
    assert reviewed["updated"] is True
    assert APPROVALS[intent_id]["status"] == "approved"


def test_blocked_for_offline_asset() -> None:
    from ot_mcp_server import ASSET_DB

    original = ASSET_DB["plc-001"].state
    ASSET_DB["plc-001"].state = DeviceState.OFFLINE
    try:
        created = create_control_intent(
            asset_id="plc-001",
            action="setpoint",
            value="40",
            operator="ops-a",
            change_ticket="CHG-1002",
        )
        assert created["accepted"] is False
    finally:
        ASSET_DB["plc-001"].state = original
