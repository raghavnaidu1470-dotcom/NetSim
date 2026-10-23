# NetSim-X Sprint Issues & Milestone Backlog

This backlog tracks the foundational issues assigned to team members across the 14-day schedule.

---

## Milestone 1: Core Implementation (Days 3–5)

### Issue #1: [Member 2] Implement Path Metric Aggregation and Normalization
- **Assignee**: Member 2 (Harish)
- **Role**: `adaptive/metrics.py`
- **Schedule Due**: Day 3
- **Status**: 🟡 Open / In Progress (Member 2 stub)
- **Doc Link**: [`member2_xar_simulation.md#2-files--exact-function-signatures`](member2_xar_simulation.md#2-files--exact-function-signatures)
- **Labels**: `member-2`, `phase-2`
- **Acceptance Criteria**:
  - Implement `aggregate_path_metrics(topology, path)` returning latency, loss, reliability, bottleneck congestion, and hops.
  - Implement `normalize_metrics(raw)` applying `MAX_LATENCY_CEILING = 200.0` and `MAX_HOPS_CEILING = 10.0`.
  - Implement `compute_path_score(norm, weights)` evaluating $\text{Score} = w_h \cdot H + w_l \cdot L + w_c \cdot C + w_p \cdot P + w_r \cdot (1-R)$.
  - Unskip and pass all tests in `tests/test_metrics.py`.

### Issue #2: [Member 2] Implement XAR Candidate Path Evaluation & Optimal Selection
- **Assignee**: Member 2 (Harish)
- **Role**: `adaptive/xar.py`
- **Schedule Due**: Day 4
- **Status**: 🟡 Open / In Progress (Member 2 stub)
- **Doc Link**: [`member2_xar_simulation.md#2-files--exact-function-signatures`](member2_xar_simulation.md#2-files--exact-function-signatures)
- **Labels**: `member-2`, `phase-2`
- **Acceptance Criteria**:
  - Implement `evaluate_all_candidate_paths(topology, src, dst, profile)` calling `topology.enumerate_paths()`.
  - Sort paths ascending by XAR score.
  - Implement `xar_find_route(topology, src, dst, profile)` returning `RouteResult`.
  - Verify that on `why_shortest_is_not_best.json`, XAR selects the 5-hop path over the 4-hop path.
  - Unskip and pass tests in `tests/test_xar.py`.

### Issue #3: [Member 3] Wire Up Interactive Streamlit Visualizer with Live Route Highlighting
- **Assignee**: Member 3 (Akhilesh Reddy) — *Implemented by Ragghav Kamaraj covering Member 3*
- **Role**: `ui/app.py`, `ui/topology_view.py`
- **Schedule Due**: Day 5
- **Status**: 🟢 **Completed & Verified**
- **Doc Link**: [`member3_ui_analytics.md#2-streamlit-tab-by-tab-wireframes-ascii`](member3_ui_analytics.md#2-streamlit-tab-by-tab-wireframes-ascii)
- **Labels**: `member-3`, `phase-2`
- **Acceptance Criteria**:
  - [x] Connect UI dropdowns to dynamically invoke `topology.find_route()`.
  - [x] Highlight computed route with distinct gold edge coloring on the Matplotlib canvas.
  - [x] Display metrics cards for latency, hop count, and congestion.
  - [x] Renders distinct host vs router styling and node/link inventory tables.

---

## Milestone 2: First Integration (Days 6–7)

### Issue #4: [Member 2] Implement Explainable Routing Decision Generator
- **Assignee**: Member 2 (Harish)
- **Role**: `adaptive/explanation.py`
- **Schedule Due**: Day 6
- **Status**: 🟡 Open / In Progress (Member 2 stub)
- **Doc Link**: [`member2_xar_simulation.md#3-worked-mathematical-example-on-why_shortest_is_not_bestjson`](member2_xar_simulation.md#3-worked-mathematical-example-on-why_shortest_is_not_bestjson)
- **Labels**: `member-2`, `phase-3`, `integration`
- **Acceptance Criteria**:
  - Implement `compare_routes(topology, selected, alternative, profile)` calculating exact metric deltas.
  - Format natural-language explanation comparing selected route against shortest path.
  - Unskip and pass `tests/test_explanation.py`.

### Issue #5: [Member 3] Connect Algorithm Comparison Dashboard & Explanation Panel
- **Assignee**: Member 3 (Akhilesh Reddy) — *Implemented by Ragghav Kamaraj covering Member 3*
- **Role**: `ui/dashboard.py`, `ui/xar_adapter.py`
- **Schedule Due**: Day 7
- **Status**: 🟢 **Completed & Verified**
- **Doc Link**: [`member3_ui_analytics.md#tab-4-algorithm-comparison-uidashboardpy`](member3_ui_analytics.md#tab-4-algorithm-comparison-uidashboardpy)
- **Labels**: `member-3`, `phase-3`, `integration`
- **Acceptance Criteria**:
  - [x] Populate Comparison tab with side-by-side metrics comparing Dijkstra (hop), Dijkstra (latency), Distance Vector, and XAR.
  - [x] Display the generated XAR explanation text in an alert box.
  - [x] Clearly badge XAR reference preview until Member 2 merges live engine.
  - [x] Render multi-metric bar charts comparing latency, hops, congestion, and score.

---

## Milestone 3: Network Resilience & Disruption (Days 8–9)

### Issue #6: [Member 2] Implement Failure Toggles, Congestion Bursts, and Recovery Calculations
- **Assignee**: Member 2 (Harish)
- **Role**: `simulation/failures.py`, `simulation/congestion.py`
- **Schedule Due**: Day 8
- **Status**: 🟡 Open / In Progress (Member 2 stub)
- **Doc Link**: [`member2_xar_simulation.md#2-files--exact-function-signatures`](member2_xar_simulation.md#2-files--exact-function-signatures)
- **Labels**: `member-2`, `phase-4`
- **Acceptance Criteria**:
  - Implement `trigger_node_failure` and `trigger_link_failure`.
  - Calculate recovery time using $T_{\text{detect}} + (N_{\text{rounds}} \times T_{\text{round}})$.
  - Implement `set_link_congestion` and `apply_burst_congestion`.
  - Unskip and pass tests in `tests/test_failures.py` and `tests/test_congestion.py`.

### Issue #7: [Member 3] Interactive Network Disruption Controls in UI
- **Assignee**: Member 3 (Akhilesh Reddy) — *Implemented by Ragghav Kamaraj covering Member 3*
- **Role**: `ui/app.py`, `ui/packet_view.py`, `ui/controls.py`
- **Schedule Due**: Day 9
- **Status**: 🟢 **Completed & Verified**
- **Doc Link**: [`member3_ui_analytics.md#tab-3-network-disruption--recovery`](member3_ui_analytics.md#tab-3-network-disruption--recovery)
- **Labels**: `member-3`, `phase-4`
- **Acceptance Criteria**:
  - [x] Provide runtime failure toggles for routers (crash/restore) and links (sever/reconnect).
  - [x] Render failed nodes with dashed red edges and offline styling.
  - [x] Display recovery time slider and estimated packet drops during the outage window.
  - [x] Include one-click scenario to fail intermediate bottleneck routers on active path.
  - [x] Show side-by-side before-and-after failure rerouting metrics and deltas.

---

## Milestone 4: Protocol Demonstrations (Day 12)

### Issue #8: [Member 3] Implement Transport-Layer Demonstrations (TCP vs UDP)
- **Assignee**: Member 3 (Akhilesh Reddy) — *Implemented by Ragghav Kamaraj covering Member 3*
- **Role**: `protocols/tcp_udp.py`, `ui/protocol_lab.py`
- **Schedule Due**: Day 12
- **Status**: 🟢 **Completed & Verified**
- **Doc Link**: [`member3_ui_analytics.md#tab-5-protocol-lab-protocolstcp_udppy-protocolscrcpy`](member3_ui_analytics.md#tab-5-protocol-lab-protocolstcp_udppy-protocolscrcpy)
- **Labels**: `member-3`, `phase-6`
- **Acceptance Criteria**:
  - [x] Simulate TCP 3-way handshake and sliding window retransmissions.
  - [x] Simulate UDP datagram transmission with unrecovered drops.
  - [x] Consume route-derived packet loss as default with slider override.
  - [x] Unskip and pass `tests/test_tcp_udp.py` (8/8 tests passing).

### Issue #9: [Member 3] Implement CRC Polynomial Error Detection Demonstration
- **Assignee**: Member 3 (Akhilesh Reddy) — *Implemented by Ragghav Kamaraj covering Member 3*
- **Role**: `protocols/crc.py`, `ui/protocol_lab.py`
- **Schedule Due**: Day 12
- **Status**: 🟢 **Completed & Verified**
- **Doc Link**: [`member3_ui_analytics.md#tab-5-protocol-lab-protocolstcp_udppy-protocolscrcpy`](member3_ui_analytics.md#tab-5-protocol-lab-protocolstcp_udppy-protocolscrcpy)
- **Labels**: `member-3`, `phase-6`
- **Acceptance Criteria**:
  - [x] Implement modulo-2 bitwise division for `compute_crc` and `verify_crc`.
  - [x] Support CRC-4, CRC-8, and custom validated polynomials.
  - [x] Support single-bit error injection and receiver syndrome verification.
  - [x] Unskip and pass `tests/test_crc.py` (8/8 tests passing).
