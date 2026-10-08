# NetSim-X Integration Architecture & Workflows

This document establishes the end-to-end integration contracts connecting the UI layer (`ui/`), Routing Engine (`network/`), and Adaptive Engine (`adaptive/`, `simulation/`).

---

## 1. End-to-End System Flow

```text
+-------------------+
|  Streamlit UI     | (Member 3)
|  User selects:    |
|  - Topology       |
|  - Source/Dest    |
|  - Protocol & Prof|
+---------+---------+
          |
          v
+-------------------+
|  Topology Engine  | (Member 1)
|  - to_networkx()  |
|  - enumerate_paths|
+---------+---------+
          |
          v
+-------------------+
|  XAR Engine       | (Member 2)
|  - aggregate_path |
|  - normalize      |
|  - score candidates
+---------+---------+
          |
          v
+-------------------+
|  Explanation      | (Member 2)
|  - compare_routes |
|  - generate text  |
+---------+---------+
          |
          v
+-------------------+
|  UI Visualization | (Member 3)
|  - draw_topology  |
|  - comparison tab |
|  - explanation box|
+-------------------+
```

---

## 2. Standard Sequence Workflows with Real Function Names

### Sequence A: Route Computation & Highlight
1. **User interaction**: User picks Source (`PC1`) and Destination (`PC2`) in `ui.controls.render_sidebar_controls`.
2. **Path generation**: `network.topology.Topology.find_route(source="PC1", destination="PC2", algorithm="xar")` is called.
3. **Candidate evaluation**:
   - `Topology.enumerate_paths("PC1", "PC2", max_hops=8)` returns all simple paths.
   - For each candidate:
     - `adaptive.metrics.aggregate_path_metrics(topology, path)` produces `RawPathMetrics`.
     - `adaptive.metrics.normalize_metrics(raw_metrics)` produces `NormalizedMetrics`.
     - `adaptive.metrics.compute_path_score(norm, weights)` calculates scalar penalty score.
   - The candidate with the minimal score is designated the winner.
4. **Explanation**:
   - `adaptive.explanation.compare_routes(topology, selected_path, alternative_path, profile)` generates comparison deltas and explanation string.
5. **Rendering**:
   - `ui.topology_view.draw_topology_graph(topology, highlighted_path=selected_path)` draws graph.
   - UI displays metrics and explanation box.

### Sequence B: Runtime Node Disruption & Rerouting
1. **Failure trigger**: User clicks "Fail Router R2" in UI.
2. **Deactivation**: `network.topology.Topology.set_node_active("R2", False)` updates node state.
3. **Graph update**: `Topology.to_networkx(only_active=True)` automatically excludes R2 and all attached links.
4. **Recovery calculation**:
   - `simulation.failures.calculate_recovery_time(detection_delay_ms=150.0, recomputation_rounds=4, per_round_delay_ms=50.0)` computes total recovery time ($350\text{ ms}$).
5. **Rerouting**: `Topology.find_route(source, destination, algorithm)` computes new detour path.
6. **UI updates**: Old path vs new path comparison rendered with extra hops and packets dropped.

---

## 3. Integration Checkpoints

### Checkpoint 1: Days 6–7 (Baseline Route Resolution)
- **Goal**: UI displays live topologies and resolves Dijkstra routes dynamically.
- **Criteria**:
  - `Topology.load_json` loads all 3 topologies without errors.
  - Selecting any valid pair of nodes highlights Dijkstra path in UI.
  - Mock data available in `adaptive.mock_data` to unblock Member 3 while Member 2 finalizes XAR scoring.

### Checkpoint 2: Days 8–9 (Failure Recovery & Disruption)
- **Goal**: Disruption triggers propagate from UI into graph deactivation and recalculation.
- **Criteria**:
  - Toggling router status immediately triggers rerouting in UI.
  - Recovery time metrics calculated and rendered in Disruption tab.

### Checkpoint 3: Days 10–11 (Algorithm Race Mode)
- **Goal**: Dijkstra, Distance Vector, and XAR evaluated side-by-side on identical graph snapshots.
- **Criteria**:
  - Comparative table populated with live metrics.
  - XAR explanation engine justifies why XAR's chosen route is superior to shortest-path.

---

## 4. Common Integration Pitfalls & Solutions

1. **Not rebuilding the NetworkX graph after node deactivation**:
   - *Problem*: Calling `topology.set_node_active(node_id, False)` modifies the `Node` object, but if `G` was cached, Dijkstra continues to route through the failed node.
   - *Fix*: Always call `topology.to_networkx(only_active=True)` during route computation, or call `find_route` which regenerates the active graph.

2. **Mutating shared Topology objects directly inside the UI**:
   - *Problem*: In Streamlit, mutating a topology object in memory can cause state leaks across page reruns or corrupt default scenarios.
   - *Fix*: When applying temporary disruptions in UI, create a fresh copy or cleanly restore original state via `Topology.set_node_active(node_id, True)`.

3. **Inconsistent Link Directions**:
   - *Problem*: Looking up `topology.get_link(v, u)` fails if link was defined as `u -> v`.
   - *Fix*: `Topology.get_link(u, v)` is bidirectionally symmetric: it checks both `(u, v)` and `(v, u)`.

4. **Division by Zero in Normalization**:
   - *Problem*: If ceiling is 0 or unconfigured.
   - *Fix*: Fixed constants `MAX_LATENCY_CEILING = 200.0` and `MAX_HOPS_CEILING = 10.0` are defined and enforced in `adaptive/metrics.py`.
