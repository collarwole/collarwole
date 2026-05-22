# OT MCP Server Design (SDLC + AI Architecture)

## 1) SDLC Flow
1. **Requirements**
   - Integrate legacy OT protocols into modern AI/analytics without direct unsafe actuation.
   - Preserve backward compatibility (timing, register semantics, alarm workflows).
   - Enforce human-in-the-loop and change-control for every control-path intent.
2. **Design**
   - MCP tools for inventory, protocol transitions, intent creation, and intent review.
   - MCP resources for safety guardrails and architecture reference context.
3. **Implementation**
   - Typed asset model with criticality and action allow-lists.
   - Policy engine for action and engineering-bound checks.
   - JSONL tamper-evident style audit trail for intent lifecycle events.
4. **Verification**
   - Static syntax checks and import validation.
   - Unit tests for policy checks and approval workflow.
5. **Deployment**
   - Run in OT DMZ/edge zone with strict identity and network segmentation.
6. **Operations**
   - Stream audit records to SIEM/SOC; monitor denied actions and approval SLA.
7. **Continuous Improvement**
   - Extend mappings, integrate live CMDB/historian data, and validate with twin replay.

## 2) AI + OT Guardrail Principles
- **AI assists, humans authorize**: AI remains advisory by default.
- **Least privilege**: per-asset action allow-lists.
- **Deterministic boundaries**: enforce bounded setpoint policies.
- **Fail closed**: uncertainty or unsupported states block controls.
- **Traceability**: every intent create/review action is auditable.

## 3) Backward Compatibility Strategy
- Preserve protocol semantics using field gateways/adapters.
- Maintain dual-stack during migration and validate with parallel runs.
- Use rollback gates before final cutover per segment/cell.
