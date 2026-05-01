# OT MCP Server Design (SDLC + AI Architecture)

## 1. SDLC Flow
1. **Requirements**
   - Integrate legacy OT protocols with AI systems without unsafe direct control.
   - Preserve backward compatibility (timing semantics, register maps, alarm behavior).
   - Enforce human-in-the-loop for any control-path command.
2. **Architecture/Design**
   - MCP server tools expose discovery, translation recommendations, and control-intent creation.
   - MCP resources provide policy/guardrail documents and architecture references.
3. **Implementation**
   - `ot_mcp_server.py` with typed models, protocol mappings, and safety checks.
4. **Verification**
   - Validate server imports and static syntax (`python -m py_compile`).
   - Smoke test tool registration by launching server process.
5. **Deployment**
   - Run as sidecar service in OT DMZ or trusted edge zone.
6. **Operations/Monitoring**
   - Ship audit logs to SIEM; monitor command approval latency and denied actions.
7. **Continuous Improvement**
   - Add adapters for additional OT protocols and add model feedback loops.

## 2. AI + OT Architecture Principles
- **Safety first**: AI recommends; humans approve writes.
- **Backward compatibility**: modern interfaces map to existing PLC/RTU semantics.
- **Least privilege**: action allow-lists and role checks.
- **Deterministic operations**: no AI-driven actuation without bounded policies.
- **Auditability**: trace every recommendation and command intent.

## 3. Human-in-the-Loop Guardrails
- Mandatory approval for high-risk assets (e.g., safety-loop tagged devices).
- Block actions for assets in `offline` or `maintenance` states.
- Capture operator identity in each control intent.
- Keep emergency shutdown systems out-of-band from MCP control channels.

## 4. Backward Compatibility Strategy
- Maintain dual-stack operation with protocol gateway translation.
- Run parallel validation with digital twin/bench before plant cutover.
- Preserve polling cadence and event sequencing from legacy SCADA.

## 5. Suggested Next Steps for Industry Scale
- Integrate CMDB, historian, and real PLC inventory sync.
- Add signed command workflow (PKI-backed approval).
- Add anomaly-scoring tool from OT telemetry for AI-driven advisories.
