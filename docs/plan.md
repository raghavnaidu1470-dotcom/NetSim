# NetSim-X 14-Day Project Plan & Milestones

This schedule establishes clear deliverables, integration checkpoints, and edge-case testing protocols for our 3-person engineering team across two weeks.

---

## 1. Timeline & Sprint Phases

### Phase 1: Architecture & Design (Days 1–2)
- [x] Agree on shared data schema (`Node`, `Link`, `RouteResult`).
- [x] Finalize XAR mathematical formulation, normalization rules, and traffic profiles (`docs/spec.md`).
- [x] Set up Git branches (`develop`, `feature/*`), CI workflow, issue templates, and CODEOWNERS.
- [x] Create 3 reference demo topologies (`data/topologies/`).

### Phase 2: Core Implementation (Days 3–5)
- **Member 1 (Ragghav Kamaraj - Network Engine)**:
  - Topology loading from JSON with IPv4 validation.
  - NetworkX graph generation and path enumeration (`enumerate_paths`).
  - Dijkstra / Link State shortest path engine.
  - Round-by-round Distance Vector with convergence round counter.
  - Routing table generation and update after node failure.
- **Member 2 (Harish - Adaptive & Simulation)**:
  - Implement metric aggregation and unit-interval normalization (`adaptive/metrics.py`).
  - Implement XAR candidate path evaluation and route selection (`adaptive/xar.py`).
  - Implement disruption handlers for router/link failures and congestion injection (`simulation/`).
- **Member 3 (Akhilesh Reddy - UI & Visualizer)**:
  - Build Streamlit foundation with sidebar parameter selectors (`ui/controls.py`).
  - Integrate NetworkX / Matplotlib graph rendering with path highlighting (`ui/topology_view.py`).
  - Set up session state for tick-based packet simulation.

### Phase 3: First Integration Checkpoint (Days 6–7)
- **Target**: End-to-end routing flow functional.
- User selects topology and endpoints in UI ➔ Member 1 generates graph & paths ➔ Member 2 scores with XAR ➔ UI displays highlighted route and explanation text.
- Resolve any schema mismatches or coordinate system differences.

### Phase 4: Network Resilience & Disruption (Days 8–9)
- Implement interactive failure toggles ("Fail R2" button).
- Visualize dead routers (red nodes) and severed links (dashed red).
- Calculate and display formal recovery time:
  $$\text{Recovery Time} = \text{detection\_delay} + (\text{recomputation\_rounds} \times \text{per\_round\_delay})$$
- Trigger automatic rerouting and display before/after metrics delta.

### Phase 5: Algorithm Race Mode & Benchmarking (Days 10–11)
- Build comparative dashboard comparing Dijkstra, Distance Vector, and XAR on:
  - Latency (ms)
  - Hop count
  - Packet loss probability
  - Bottleneck congestion
  - Convergence rounds / recovery time
- Verify that XAR does not artificially win every race; demonstrate scenarios where Dijkstra ties or beats XAR in raw hops.

### Phase 6: Protocol Demonstration Lab (Day 12)
- **TCP vs UDP Demo**:
  - Interactive visualization of 3-way handshake (SYN, SYN-ACK, ACK).
  - Sliding window flow control with retransmission under packet drops.
  - Comparison against UDP fire-and-forget datagram stream.
- **CRC Error Detection Demo**:
  - Step-by-step modulo-2 polynomial long division.
  - Checksum generator and receiver syndrome verification with bit flipping.

### Phase 7: Cross-Testing & Edge Cases (Day 13)
- Execute exhaustive testing across all critical edge cases (see Section 2).
- Ensure no scenario causes the app or backend to crash with an unhandled exception.
- Run complete test suite (`pytest`) with 100% test passing rate.

### Phase 8: Polish, Presentation & Freeze (Day 14)
- **Code Freeze**: Zero new features or algorithmic changes.
- Finalize `README.md` with system architecture diagrams, demo screenshots, and setup instructions.
- Prepare live demo walkthrough script and presentation slides.

---

## 2. Exhaustive Edge Cases & Handling Policy

The application must **NEVER crash**. When encountering abnormal network conditions, friendly user-facing messages or fallback structures must be returned.

| Edge Case Scenario | Expected System Behavior | Test Verification |
| :--- | :--- | :--- |
| **Source == Destination** | Return path `[source]`, hop count `0`, latency `0.0`, status `"success"`. | `test_link_state_source_is_destination` |
| **Disconnected Network** | Return path `[]`, status `"no_route"`, display friendly UI warning. | `test_distance_vector_disconnected` |
| **All Paths Failed / Severed** | Route status `"no_route"`, highlight disconnected topology with red edges. | `test_find_route_invalid_and_disconnected` |
| **Invalid IPv4 Address** | Raise clean `ValueError` at ingestion; UI shows descriptive format error. | `test_validate_ipv4_invalid` |
| **100% Packet Loss ($P=1.0$)** | XAR heavily penalizes path; TCP simulation shows 100% retransmission attempts. | `test_packet_loss` |
| **Severe Congestion ($C=1.0$)** | XAR avoids link if alternatives exist; UI displays high bottleneck alert. | `test_congestion` |
| **Router Failure Mid-Routing** | Simulation catches failure at next hop, drops packet, and recalculates path. | `test_failures` |
| **Equal-Cost Routes** | Deterministic tie-breaking (e.g. alphabetical or lower hop count). | `test_topology` |
| **Single Valid Path** | Chosen by all algorithms regardless of poor metrics; warnings displayed. | `test_topology` |
