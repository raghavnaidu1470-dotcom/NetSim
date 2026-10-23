# Member 3 Handbook: UI, Analytics & Protocol Demonstrations

**Role Owner**: Akhilesh Reddy (Member 3)  
**Implementation Origin**: Implemented by **Ragghav Kamaraj (Member 1)** covering Member 3's role to complete front-end analytics and educational protocol demos.  
**Packages Owned**: `ui/` (`app.py`, `topology_view.py`, `controls.py`, `dashboard.py`, `packet_view.py`, `protocol_lab.py`, `xar_adapter.py`), `protocols/` (`tcp_udp.py`, `crc.py`), and corresponding tests in `tests/`.

---

## 1. Purpose & Responsibilities

The NetSim-X User Interface provides an interactive, visual platform for network routing simulation, algorithmic benchmarking, fault resilience testing, and educational protocol analysis:
1. **Interactive Topology Visualization**: Draws network graphs dynamically via NetworkX and Matplotlib with custom shapes and colors for hosts vs. routers, operational status, link metric labels, and active path highlighting.
2. **Hop-by-Hop Packet Stepping**: Provides non-blocking tick-based packet simulation with per-hop latency accumulation, stochastic multi-packet loss streaming, and router forwarding table inspection.
3. **Resilience & Fault Injection**: Allows runtime crashing/restoration of routers and links, dynamic link metric tuning, and automated recovery time calculations adhering to the formal specification.
4. **Multi-Algorithm Race Mode**: Benchmarks Dijkstra (Hop Count), Dijkstra (Latency), Distance Vector, and XAR side-by-side with comparison tables, bar charts, and explainable decision rationales.
5. **Educational Protocol Demonstrations**: Pure-Python simulations of TCP sliding window/3-way handshake vs. UDP datagrams, and CRC polynomial division with bit-level corruption and syndrome verification.

---

## 2. Streamlit Tab-by-Tab Architecture & Functions

```text
========================================================================================
|  🌐 NetSim-X: Explainable Adaptive Routing Framework                                 |
========================================================================================
| [Sidebar Controls] | [Tabs: 1. Topology | 2. Packets | 3. Disruption | 4. Race | 5. Protocols]
| Topo: why_shortest | ----------------------------------------------------------------
| Src: PC1  Dst: PC2 | 🗺️ Active Tab View with Live Data & Dynamic Updates
| Algo: XAR          | +----------------------------------+ +-------------------------+
| Profile: Standard  | |  [ Matplotlib / NetworkX Graph ] | | Metrics & KPIs          |
| Failures: Injected | |  PC1 - R1 - R3 - R4              | | Latency: 36.0 ms        |
|                    | |       \   /                      | | Hops: 5                 |
| [Reset Scenario]   | |        R5 - PC2                  | | Loss: 3.16% | Cong: 12% |
|                    | +----------------------------------+ +-------------------------+
----------------------------------------------------------------------------------------
```

### Tab 1: Topology & Routing (`ui/topology_view.py`)
- **Key Functions**:
  - `draw_topology_graph(topology, highlighted_path, title)`: Generates thread-safe Matplotlib Figure using the headless `Agg` backend.
  - `render_topology_view(topology, highlighted_path, title)`: Main Tab 1 renderer.
- **Visual Styling**:
  - **Hosts**: Cyan / Teal squares (`#17a2b8`) with node ID and IPv4 address.
  - **Active Routers**: Emerald Green circles (`#28a745`).
  - **Failed / Inactive Nodes**: Crimson red crosses (`#dc3545`).
  - **Active Links**: Slate grey solid lines (`#6c757d`).
  - **Severed / Inactive Links**: Dashed crimson lines (`#dc3545`).
  - **Highlighted Route**: Thick golden yellow forwarding path (`#f39c12`, width 4.5).
  - **Link Labels**: Edge annotations showing latency (ms), packet loss (%), and bottleneck congestion (%).
- **Inventory Tables**: Clean Pandas dataframes displaying all nodes (ID, IP, Type, Status) and physical links (Endpoints, Latency, Bandwidth, Congestion, Loss, Reliability, State).
- *Screenshot Placeholder*: `screenshots/01_topology_overview.png`

### Tab 2: Packet Simulation (`ui/packet_view.py`)
- **Key Functions**:
  - `render_packet_simulation_tab(topology, source, destination, algorithm, metric, traffic_profile)`
  - `render_packet_simulation_view(path, metrics)` (legacy backward compatibility)
- **State Management**:
  - Uses `st.session_state["pkt_sim_hop"]` (current hop index) and `st.session_state["pkt_sim_log"]` (chronological event log).
  - Non-blocking stepper buttons: "Send New Packet", "Step (+1 Hop)", "Fast-Forward to End", and "Reset Stepper".
- **Multi-Packet Stochastic Flow**:
  - Streams $N$ packets across active route with reproducible random seed.
  - Calculates delivered vs dropped packets using route cumulative loss probability $P_{\text{raw}} = 1 - \prod (1 - p_{\text{loss}})$.
- **Router Forwarding Table Inspector**:
  - Select any router to inspect its live routing table via `build_routing_table()`.
- **Distance Vector Convergence Details**:
  - Expander detailing Bellman-Ford rounds and per-round distance vector updates from `simulate_distance_vector_convergence()`.
- *Screenshot Placeholders*: `screenshots/02_packet_simulation_hop_by_hop.png`, `screenshots/03_packet_simulation_loss_stream.png`

### Tab 3: Network Disruption & Fault Recovery (`ui/controls.py`)
- **Key Functions**:
  - `render_sidebar_controls(available_topologies, active_topology)`
  - `render_disruption_tab(topology, source, destination, algorithm, metric, traffic_profile, original_topology)`
  - `compute_recovery_time_fallback(detection_delay_ms, recomputation_rounds, per_round_delay_ms)`
- **Disruption Capabilities**:
  - Router Crash / Restore toggles via `topology.set_node_active()`.
  - Link Cut / Reconnect toggles via `topology.set_link_active()`.
  - One-Click Targeted Disruption: Automatically identifies and fails the intermediate bottleneck router on the current path.
  - Dynamic Link Sliders: Adjust link congestion, latency, and packet loss on the fly.
  - Master Reset: One-click restoration of all network components to pristine state.
- **Resilience Calculation**:
  - Formally evaluates recovery time:
    $$\text{Recovery Time} = T_{\text{detect}} + (N_{\text{rounds}} \times T_{\text{round}})$$
  - Dynamically extracts Distance Vector convergence rounds from `simulate_distance_vector_reconvergence()`.
  - Calls `simulation.failures.calculate_recovery_time` or computes via spec formula (labeled `"computed by UI from spec formula"`).
- *Screenshot Placeholder*: `screenshots/04_network_disruption_reroute.png`

### Tab 4: Algorithm Comparison / Race Mode (`ui/dashboard.py`, `ui/xar_adapter.py`)
- **Key Functions**:
  - `build_comparison_benchmark(topology, source, destination, traffic_profile)`
  - `render_comparison_dashboard(comparison_data)`
  - `render_algorithm_comparison_tab(topology, source, destination, traffic_profile)`
  - `resolve_xar_route(...)`, `generate_xar_explanation(...)` from `ui.xar_adapter`
- **Benchmark Matrix**:
  - Evaluates Dijkstra (Hop Count), Dijkstra (Latency), Distance Vector, and XAR side-by-side across identical graph snapshots.
  - Columns: Algorithm, Badge, Path, Hop Count, Latency (ms), Packet Loss, Bottleneck Congestion, Reliability, Adaptive Penalty Score, Convergence Rounds.
- **XAR Adapter & Fallback Badge**:
  - Calls `adaptive.xar.xar_find_route` if implemented.
  - If unimplemented (`NotImplementedError` or `ImportError`), scores candidate paths enumerated via Member 1's `enumerate_paths` against the exact mathematical formula in `docs/spec.md` and `adaptive/traffic_profiles.py`.
  - Rows and results are explicitly badged with **`[Reference preview]`** (`"XAR (reference preview, not Member 2's implementation)"`).
  - When Member 2 merges the live engine, the adapter automatically detects it and drops the badge without requiring any UI code modifications.
- **Graphical Analytics**:
  - Side-by-side bar charts for Latency, Bottleneck Congestion, Hop Count, and Multi-Criteria Penalty Score.
- **Explainable Decision Engine**:
  - Displays natural-language justification ("Why This Route?") comparing the selected path against the shortest-path alternative.
- *Screenshot Placeholders*: `screenshots/05_algorithm_comparison_benchmark.png`, `screenshots/06_algorithm_comparison_barcharts.png`

### Tab 5: Protocol Lab (`ui/protocol_lab.py`, `protocols/`)
- **Subtab A: Transport Layer (TCP vs UDP)**:
  - `protocols.tcp_udp.simulate_tcp(num_packets, loss_probability, timeout_ms, seed, window_size, rtt_ms, max_retries)`
  - `protocols.tcp_udp.simulate_udp(num_packets, loss_probability, seed, rtt_ms)`
  - Models 3-way handshake (SYN, SYN-ACK, ACK), sliding window data transfer with sequence numbers, timeout timers, retransmissions, retry caps (preventing infinite loops under 100% loss), and FIN teardown.
  - Models UDP connectionless fire-and-forget datagram transmission with zero handshake overhead and unrecovered channel loss.
  - Consumes active route packet loss as default, with manual slider overrides.
  - Side-by-side message sequence event timeline dataframes.
- **Subtab B: Data Link Layer (CRC Error Detection)**:
  - `protocols.crc.crc_remainder(data_bits, generator_bits)`: Modulo-2 polynomial long division returning remainder checksum and step-by-step XOR division trace.
  - `protocols.crc.crc_encode(data_bits, generator)`: Appends remainder checksum to message bits.
  - `protocols.crc.crc_check(received_bits, generator)`: Receiver syndrome verification (remainder = 0000 -> valid).
  - `protocols.crc.corrupt_bits(bits, positions)`: Flips bit(s) at designated indices.
  - Interactive single-bit error injection slider with live syndrome mismatch verification.
- *Screenshot Placeholders*: `screenshots/07_protocol_lab_tcp_vs_udp.png`, `screenshots/08_protocol_lab_crc_division.png`

---

## 3. Architecture & Session State Rules

1. **Strict Member 1 API Usage**:
   - The UI solely invokes public Member 1 methods: `Topology.find_route`, `Topology.enumerate_paths`, `Topology.set_node_active`, `Topology.set_link_active`, `Topology.update_link_metrics`, `distance_vector_routing`, `simulate_distance_vector_reconvergence`, and `build_routing_table`.
   - **No routing logic is implemented inside `ui/`**.
2. **Authoritative Topology & Defensive Copies**:
   - The authoritative `Topology` is stored in `st.session_state["authoritative_topology"]`.
   - What-if actions and exploratory calculations use deep copies (`copy.deepcopy()`) to avoid state corruption across Streamlit reruns.
3. **Graceful Error Handling**:
   - All edge cases (identical source/destination, disconnected endpoints, offline nodes, invalid bitstrings) display informative, friendly banners (`st.info`, `st.warning`, `st.error`).
   - Unhandled tracebacks are completely eliminated.

---

## 4. How to Launch the Streamlit App

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run Streamlit dashboard
streamlit run ui/app.py
```

The application automatically opens at `http://localhost:8501`.

---

## 5. Definition of Done Checklist

- [x] Working interactive Streamlit app with all 5 functional tabs (`ui/app.py`).
- [x] Network graph visualizer with distinct host/router styling and dynamic path highlighting (`ui/topology_view.py`).
- [x] Tick-based hop stepper and reproducible stochastic packet flow (`ui/packet_view.py`).
- [x] Fault injection panel with one-click failure and formal recovery calculations (`ui/controls.py`).
- [x] Algorithm comparison matrix, bar charts, and explainable decision panel (`ui/dashboard.py`).
- [x] Decoupled XAR reference preview adapter with auto-drop badge flag (`ui/xar_adapter.py`).
- [x] Transport layer TCP vs. UDP simulation with 3-way handshake and retransmissions (`protocols/tcp_udp.py`).
- [x] Data-link layer CRC modulo-2 division, error injection, and syndrome checking (`protocols/crc.py`).
- [x] Unskip and pass all 24 unit tests across `tests/test_ui_components.py`, `tests/test_tcp_udp.py`, and `tests/test_crc.py` (67 tests passing project-wide).
- [x] Streamlit `AppTest` automated smoke test passing across all 3 demo scenarios.
- [x] Update `STATUS.md`, `README.md`, `docs/issues.md`, and screenshot guide (`screenshots/README.md`).
