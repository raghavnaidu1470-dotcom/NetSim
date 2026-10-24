# NetSim-X: Explainable Adaptive Routing & Network Resilience Simulation Framework

[![CI Tests](https://github.com/raghavnaidu1470-dotcom/NetSim/actions/workflows/test.yml/badge.svg)](https://github.com/raghavnaidu1470-dotcom/NetSim/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework: Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

---

## Abstract

**NetSim-X** is an interactive computer network simulation framework designed to visualize packet transmission, routing behavior, and network resilience under dynamically changing conditions. Unlike traditional educational routing simulators that primarily demonstrate shortest-path selection, NetSim-X introduces an **Explainable Adaptive Routing (XAR)** mechanism that evaluates hop count, latency, congestion, packet-loss probability, and link reliability when choosing routes. It implements Link State and Distance Vector routing alongside XAR for comparative analysis, simulates router/link failures, congestion, latency changes and packet loss, and recomputes routes while visualizing network recovery. An Explainable Routing Engine justifies each routing decision, and an algorithm-comparison environment evaluates all strategies under identical conditions. TCP/UDP and CRC demonstrations illustrate transport-layer behavior and data integrity.

---

## Key Features

1. **Multi-Metric Adaptive Routing (XAR)**:
   - Multi-objective penalty formulation:
     $$\text{Score}(P) = w_h \cdot H + w_l \cdot L + w_c \cdot C + w_p \cdot P + w_r \cdot (1 - R)$$
   - Tailored traffic profiles: *Standard*, *Real-Time Video*, and *Reliable Data Transfer*.
2. **Explainable Routing Engine**:
   - Generates transparent, human-readable rationales justifying why an adaptive route was chosen over the shortest path.
3. **Traditional Routing Baseline**:
   - Full Link State / Dijkstra shortest path engine.
   - Iterative round-by-round Distance Vector (Bellman-Ford) simulation with convergence round counting and routing table updates.
4. **Dynamic Disruptions & Resilience Analysis**:
   - Runtime router crashes, link failures, and congestion bursts.
   - Formal calculation of recovery duration:
     $$\text{Recovery Time} = \text{detection\_delay} + (\text{recomputation\_rounds} \times \text{per\_round\_delay})$$
5. **Interactive Streamlit Dashboard**:
   - Multi-tab visualization suite: Topology View, Packet Simulation, Disruption Lab, Algorithm Race Mode, and Protocol Demonstrations.
6. **Educational Protocol Lab**:
   - TCP 3-way handshake & sliding window retransmission vs UDP datagram burst.
   - CRC-4 / CRC-8 bitwise polynomial division and single-bit corruption detection.

---

## System Architecture

```text
+-------------------------------------------------------------------------------+
|                                  Streamlit UI                                 |
|   Topology View  |  Packet Flow  |  Disruption Lab  |  Race Mode  |  Protocols|
+-------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         v                                                         v
+--------------------------+                             +--------------------+
|  network/ (Member 1)     |                             | protocols/ (M3)    |
|  - Topology & IPv4 Model |                             | - TCP/UDP Demo     |
|  - NetworkX Graph Engine |                             | - CRC Division     |
|  - Dijkstra Link State   |                             +--------------------+
|  - Distance Vector & RT  |
+--------------------------+
         |
         v
+-------------------------------------------------------+
|  adaptive/ & simulation/ (Member 2)                   |
|  - Path Metrics Aggregation & Unit Normalization      |
|  - XAR Multi-Metric Scoring Engine                    |
|  - Natural-Language Route Explanation Generator       |
|  - Failure, Congestion & Recovery Simulator           |
+-------------------------------------------------------+
```

---

## Project Structure

```text
NetSim/
├── .github/workflows/          # CI pipelines (test.yml running pytest across Python 3.11 & 3.12)
├── adaptive/                   # Explainable Adaptive Routing (XAR) & traffic profiles
│   ├── explanation.py          # Natural language decision justification generator
│   ├── metrics.py              # Metric aggregation, unit-interval normalization, scoring math
│   ├── mock_data.py            # Fixture datasets for early UI testing and benchmarking
│   ├── traffic_profiles.py     # Priority weights (standard, real_time, reliable_data_transfer)
│   └── xar.py                  # Candidate path scoring and optimal route selection
├── data/topologies/            # JSON network scenario topologies
│   ├── router_failure.json     # Dynamic router R2 crash and reroute recovery demo
│   ├── traffic_profile_change.json # Real-Time vs Reliable Data Transfer path steering
│   └── why_shortest_is_not_best.json # Hop-count shortest path vs low-latency/loss path
├── docs/                       # Architecture, handbooks, milestones, specifications
│   ├── integration.md          # Multi-member interface workflows and checkpoints
│   ├── issues.md               # Sprint issue backlog and milestone tasks
│   ├── member1_network_engine.md # Member 1 handbook (Network & Routing Engine)
│   ├── member2_xar_simulation.md # Member 2 handbook (XAR & Simulation Engine)
│   ├── member3_ui_analytics.md   # Member 3 handbook (UI, Dashboards & Protocols)
│   ├── plan.md                 # 14-day team sprint roadmap and milestones
│   └── spec.md                 # System architecture, schemas, and mathematical formulations
├── network/                    # Core topology representation & traditional routing algorithms
│   ├── devices.py              # Node, Link, RouteResult dataclasses and IPv4 validation
│   ├── distance_vector.py      # Round-by-round Bellman-Ford simulation & convergence tracking
│   ├── link_state.py           # Dijkstra Link State algorithm (hop and latency metrics)
│   ├── routing_table.py        # Forwarding table generation and failure invalidation
│   └── topology.py             # NetworkX graph builder, JSON parser, and path enumerator
├── protocols/                  # Educational transport and data-link layer protocols
│   ├── crc.py                  # CRC-4/CRC-8 polynomial division and bit-flip detection
│   └── tcp_udp.py              # TCP 3-way handshake/sliding window vs UDP fire-and-forget
├── simulation/                 # Network disruption and degradation simulation
│   ├── congestion.py           # Dynamic link congestion modification and burst events
│   ├── failures.py             # Node/link failure toggles and formal recovery time calculations
│   └── packet_loss.py          # Stochastic packet drop modeling across paths
├── tests/                      # Pytest unit and integration test suite
├── ui/                         # Streamlit web application and visual dashboards
│   ├── app.py                  # Main 5-tab Streamlit dashboard application
│   ├── controls.py             # Sidebar parameter selectors and failure controls
│   ├── dashboard.py            # Comparative benchmark tables and KPI metrics cards
│   ├── packet_view.py          # Tick-based packet delivery animation and metrics
│   └── topology_view.py        # Matplotlib & NetworkX graph visualizer with path highlighting
├── CODEOWNERS                  # Package code ownership boundaries for team members
├── CONTRIBUTING.md             # Development guidelines and branch workflow rules
├── GETTING_STARTED.md          # Team onboarding guide and local setup instructions
├── pytest.ini                  # Pytest configuration and marker declarations
├── requirements.txt            # Project dependencies (NetworkX, Streamlit, Matplotlib, Pytest)
└── STATUS.md                   # Real-time implementation status tracker for all modules
```

---

## How Routing Works

NetSim-X implements traditional single-metric algorithms alongside multi-objective adaptive routing to explore the trade-offs between computational simplicity and application-level path quality.

### 1. Link State / Dijkstra
- **Graph Construction**: The topology engine builds a NetworkX graph from active nodes and operational links (`Topology.to_networkx(only_active=True)`). Nodes or links marked inactive (`active=False`) are completely excluded from graph path calculations.
- **Metric Options**:
  - `metric="hop"`: Assigns a uniform unit weight (`1.0`) to every active edge to compute unweighted shortest paths (minimizing hop count).
  - `metric="latency"`: Weights each edge by its physical propagation and queuing latency in milliseconds (`latency`), minimizing total path delay.
- **Returned Structure**: Returns a `RouteResult` dictionary containing `path` (ordered list of visited node IDs), `hop_count` (integer link count), `latency` (accumulated path latency in ms), and `status` (`"success"`, `"no_route"`, or `"invalid"`).

### 2. Distance Vector (Bellman-Ford)
- **Round-Based Table Exchange**: Each node maintains an internal routing table of distance estimates to all destinations. In discrete simulation rounds (`simulate_distance_vector_convergence`), neighboring routers exchange distance vectors and update local costs using Bellman-Ford: $D_x(y) = \min_v \{ c(x, v) + D_v(y) \}$.
- **Convergence Detection**: The simulation iteratively steps through exchange rounds until a round completes with zero table distance or next-hop updates across the entire network (`has_changed == False`), returning the exact number of convergence rounds required.
- **Reconvergence After Failure**: When an active router or link fails, next-hop entries pointing to the failed device are invalidated. Routers propagate distance vector changes over subsequent rounds until stable alternate paths are established.
- **Infinity Value**: Unreachable destinations and broken routes are represented using `INFINITY = 999999.0` (acting as the upper distance ceiling and poison-reverse bound).

### 3. Explainable Adaptive Routing (XAR)
- **Candidate Path Enumeration**: Evaluates candidate paths using `Topology.enumerate_paths(source, destination, max_hops=8)`, finding all simple loop-free active paths up to a specified hop cutoff.
- **Path-Level Aggregation Rules**:
  - *Cumulative Latency*: Sum of link latencies, $L_{\mathrm{raw}} = \sum \text{latency}(e_i)$.
  - *End-to-End Packet Loss*: Multiplicative drop probability, $P_{\mathrm{raw}} = 1 - \prod (1 - p_{\mathrm{loss}}(e_i))$.
  - *End-to-End Reliability*: Product of operational link availabilities, $R_{\mathrm{raw}} = \prod \text{reliability}(e_i)$.
  - *Bottleneck Congestion*: Maximum link utilization on the path, $C_{\mathrm{raw}} = \max \text{congestion}(e_i)$.
  - *Hop Count*: Total edge traversals, $\text{Hops} = |path| - 1$.
- **Fixed-Ceiling Normalization**: Converts raw metrics to $[0.0, 1.0]$ where **0 is ideal** and **1 is worst**:
  - $H = \min(1.0, \text{Hops} / 10.0)$
  - $L = \min(1.0, L_{\mathrm{raw}} / 200.0)$
  - $C = C_{\mathrm{raw}} \in [0.0, 1.0]$
  - $P = P_{\mathrm{raw}} \in [0.0, 1.0]$
  - $R_{\mathrm{penalty}} = 1.0 - R_{\mathrm{raw}} \in [0.0, 1.0]$
- **Score Formula & Lowest Score Wins**:
  $$\text{Score}(P) = w_h \cdot H + w_l \cdot L + w_c \cdot C + w_p \cdot P + w_r \cdot (1 - R)$$
  All candidate paths are scored against the selected profile's weights. **The path with the lowest score is selected.**
- **Transparent Explanation Output**: Compares the chosen path against the alternative shortest path, outputting exact metric deltas (e.g. latency saved, congestion reduced, loss avoided) and explaining the trade-offs to network operators.

---

## Traffic Profiles

Traffic profiles allow applications to configure routing objectives by weighting specific network penalties. Real weights are defined in `adaptive/traffic_profiles.py`:

| Profile | Priority Order | Typical Use | Weights ($w_h, w_l, w_c, w_p, w_r$) |
| :--- | :--- | :--- | :--- |
| **`standard`** | Latency > Hops = Congestion = Loss > Reliability | General-purpose enterprise data balancing latency and efficiency | $w_h=0.20$, $w_l=0.25$, $w_c=0.20$, $w_p=0.20$, $w_r=0.15$ |
| **`real_time`** | Latency > Loss > Congestion > Hops > Reliability | Interactive VoIP, video streaming, and latency-critical teleconferencing | $w_h=0.10$, $w_l=0.45$, $w_c=0.15$, $w_p=0.25$, $w_r=0.05$ |
| **`reliable_data_transfer`** | Loss > Reliability > Latency > Congestion > Hops | Database replication, file transfers, and financial transaction processing | $w_h=0.05$, $w_l=0.15$, $w_c=0.10$, $w_p=0.40$, $w_r=0.30$ |

---

## Resilience Flow

When a network device fails, NetSim-X coordinates detection, routing table invalidation, recomputation, and recovery time reporting:

```mermaid
sequenceDiagram
    autonumber
    actor User as Operator / UI
    participant Topo as Topology (network/topology.py)
    participant Fail as Simulation (simulation/failures.py)
    participant RT as RoutingTable (network/routing_table.py)
    participant Engine as Routing Engine (Dijkstra / DV / XAR)
    participant UI as Dashboard View (ui/app.py)

    User->>Topo: set_node_active("R2", False)
    Note over Topo: Router R2 marked inactive; links severed in graph
    User->>Fail: trigger_node_failure(topo, "R2", src, dst, algo="xar")
    Fail->>RT: invalidate_next_hop("R2")
    Note over RT: Routes through R2 cleared from forwarding tables
    Fail->>Fail: calculate_recovery_time(detection_delay_ms=150.0, recomputation_rounds=4, per_round_delay_ms=50.0)
    Note over Fail: Recovery Time = 150 + (4 * 50) = 350 ms
    Fail->>Engine: find_route(src, dst, algorithm="xar")
    Engine->>Topo: enumerate_paths(src, dst, max_hops=8)
    Note over Engine: Recomputes optimal path over remaining active topology
    Engine-->>Fail: RouteResult (active backup path)
    Fail-->>UI: RecoveryMetrics (recovery_time_ms=350, packets_lost=12, backup_route)
    UI-->>User: Render updated topology, highlighted backup route & recovery KPI cards
```

---

## 3 Demo Scenarios Included

All demo topologies reside in `data/topologies/` and can be verified using `python scripts/verify_demos.py`:

1. **`why_shortest_is_not_best.json`**:
   - Demonstrates why unweighted minimum hop count is often suboptimal in congested networks.
   - **Dijkstra (hop-count metric)**: Picks the 4-hop congested path (`PC1 -> R1 -> R2 -> R5 -> PC2`, 79.0 ms latency, 82.0% congestion, 19.17% packet loss, 65.47% reliability).
   - **Dijkstra (latency metric)**: Picks the clean 5-hop path (`PC1 -> R1 -> R3 -> R4 -> R5 -> PC2`, 36.0 ms latency, 12.0% congestion, 3.16% packet loss, 96.84% reliability).
   - *Reference values from the specification (reproduced by `tests/test_member2_verification.py`)*: Under the Standard profile ($w_h=0.20, w_l=0.25, w_c=0.20, w_p=0.20, w_r=0.15$), the specification defines an adaptive score of $0.1801$ for the 5-hop path vs $0.4329$ for the 4-hop path.
2. **`router_failure.json`**:
   - Demonstrates runtime router disruption and dynamic path recovery.
   - **Pre-failure route**: Traffic flows across intermediate router `R2` along `PC1 -> R1 -> R2 -> PC2` (3 hops, 14.0 ms latency, 10.0% congestion, 0.70% packet loss, 98.80% reliability).
   - **Post-failure route**: Failing `R2` triggers dynamic recovery, re-routing over backup path `PC1 -> R1 -> R3 -> R4 -> PC2` (4 hops, 44.0 ms latency, 15.0% congestion, 2.58% packet loss, 94.98% reliability).
   - *Reference values from the specification (reproduced by `tests/test_member2_verification.py`)*: Under the theoretical resilience model ($T_{\mathrm{detect}} = 150\text{ ms}$, $N_{\mathrm{rounds}} = 4$, $T_{\mathrm{round}} = 50\text{ ms}$), the specification defines an expected recovery time of $350.0\text{ ms}$.
3. **`traffic_profile_change.json`**:
   - Demonstrates candidate path characteristics between two alternative 4-hop paths (`PC1 -> R1 -> R3 -> R4 -> PC2` vs `PC1 -> R1 -> R2 -> R4 -> PC2`).
   - **Candidate A (Low Latency / Dijkstra latency metric choice)**: `PC1 -> R1 -> R3 -> R4 -> PC2` (4 hops, 17.0 ms latency, 14.0% congestion, 14.61% packet loss, 79.94% reliability).
   - **Candidate B (High Reliability / Dijkstra hop metric choice)**: `PC1 -> R1 -> R2 -> R4 -> PC2` (4 hops, 69.0 ms latency, 8.0% congestion, 0.40% packet loss, 99.60% reliability).
   - *Reference values from the specification (reproduced by `tests/test_member2_verification.py`)*: Under profile weighting, Candidate A achieves score $0.1458$ vs $0.2085$ under Real-Time traffic, whereas Candidate B achieves score $0.0826$ vs $0.1654$ under Reliable Data Transfer.

---

## Algorithm Comparison (Race Mode)

The interactive **Algorithm Race Mode** evaluates Dijkstra, Distance Vector, and XAR side-by-side on identical topologies and traffic demands across seven core metrics:

1. **Accumulated Latency (ms)**: Cumulative transmission and propagation delay along the path.
2. **Hop Count**: Total links traversed from source to destination.
3. **End-to-End Packet Loss (%)**: Cumulative drop probability.
4. **Bottleneck Congestion (%)**: Maximum single-link utilization along the path.
5. **Route Cost / Adaptive Score**: Normalized multi-metric penalty score under active profile.
6. **Delivered vs. Retransmitted Packets**: Actual payload throughput and TCP retransmission volume under loss.
7. **Recovery / Convergence Time (ms)**: Iterative recomputation rounds and outage window duration following network failures.

> **Important**: **XAR is not guaranteed to win every race.** In uncongested, uniform networks with zero packet loss, traditional Dijkstra or Distance Vector finds the mathematically optimal shortest path with lower computational complexity ($O(V \log V + E)$ vs $k$-path candidate enumeration). XAR is designed specifically to prevent severe degradation in real-world scenarios where shortest paths conceal heavy congestion, high packet drops, or poor link reliability.

### XAR Engine Status & Reference Preview

Member 2's `adaptive` and `simulation` packages are implemented and verified (`tests/test_member2_verification.py`). The front end still reaches XAR through a decoupled adapter (`ui/xar_adapter.py`) so the dashboard degrades gracefully:
- **Live Engine**: The adapter calls `adaptive.xar.xar_find_route` and `adaptive.explanation.compare_routes` and shows their results without any badge.
- **Spec-Compliant Reference Preview (safety net)**: Only if the engine raises `NotImplementedError` or `ImportError`, the adapter enumerates simple candidate paths via `enumerate_paths` and scores each against the formula in `docs/spec.md`, tagging the output with the **`[Reference preview]`** badge (`XAR (reference preview, not Member 2's implementation)`).
- **Zero-Rigging Guarantee**: Results are evaluated strictly from graph metrics without manipulation: if XAR ties or loses (for example in `router_failure.json`, where every algorithm agrees), it is displayed as is.

---

## Running the Dashboard

Launch the interactive dashboard locally:

```bash
streamlit run ui/app.py
```

The web application opens automatically in your browser (default `http://localhost:8501`) with five comprehensive tabs:

1. **🗺️ Tab 1: Topology & Routing**:
   - Interactive NetworkX & Matplotlib visualization with distinctive styling: Cyan square host nodes, Emerald green router nodes, and dashed red lines for inactive links.
   - Dynamic path highlighting in gold showing the active route computed by the selected algorithm.
   - Edge metric labels displaying latency (ms), packet loss (%), and bottleneck congestion (%).
   - Full tabular inventory of device nodes and physical link parameters.
2. **📦 Tab 2: Packet Simulation**:
   - Hop-by-hop stepper moving packets through intermediate routers with cumulative latency tracking and an event log.
   - Stochastic batch transmission of $N$ packets using route-aggregated packet loss rates with a reproducible random seed.
   - Router forwarding table inspector displaying active next-hop pointers.
   - Distance Vector convergence iterations log.
3. **⚡ Tab 3: Network Disruption**:
   - Interactive fault injection: crash/restore routers, cut/reconnect links, and adjust link metrics via sliders.
   - Targeted one-click scenario to crash the critical intermediate router along the active route.
   - Before-and-after failure rerouting impact analysis (path shift, hop delta, latency delta).
   - Resilience calculation adhering to the formal recovery time formula: $T_{\mathrm{detect}} + (N_{\mathrm{rounds}} \times T_{\mathrm{round}})$.
4. **⚖️ Tab 4: Algorithm Comparison (Race Mode)**:
   - Evaluates Dijkstra (Hop Count), Dijkstra (Latency), Distance Vector, and XAR side-by-side across identical topologies.
   - Multi-metric benchmark matrix and side-by-side bar charts (Latency, Congestion, Hops, Multi-Criteria Score).
   - Explainable Decision Engine ("Why This Route?") detailing trade-offs.
5. **🔬 Tab 5: Protocol Lab**:
   - **Transport Layer**: Comparative simulation of TCP (3-way handshake, sliding window, timeouts, retransmissions, teardown) vs. UDP (zero-handshake connectionless datagram burst) with side-by-side event timeline tables. Defaults to the active path's packet loss rate.
   - **Data Link Layer**: Modulo-2 polynomial division for CRC-4 (`10011`), CRC-8 (`100000111`), or custom generators with step-by-step XOR division trace, interactive single-bit error injection, and receiver syndrome verification.

---

## Quickstart & Local Setup

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/raghavnaidu1470-dotcom/NetSim.git
cd NetSim

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
pytest
```

### 3. Launch the Interactive Web App
```bash
streamlit run ui/app.py
```

For onboarding, see [**GETTING_STARTED.md**](GETTING_STARTED.md).

---

## Team Roles & Ownership

To prevent merge conflicts, codebase modules are strictly partitioned:

| Member | Package Ownership | Focus Area | Detailed Handbook |
| :--- | :--- | :--- | :--- |
| **Member 1** (Ragghav Kamaraj) | `network/`, `data/topologies/` | Network topology, IPv4 validation, Dijkstra, Distance Vector, routing tables | [`docs/member1_network_engine.md`](docs/member1_network_engine.md) |
| **Member 2** (Harish) | `adaptive/`, `simulation/` | XAR scoring, normalization, traffic profiles, explanation engine, failure simulation | [`docs/member2_xar_simulation.md`](docs/member2_xar_simulation.md) |
| **Member 3** (Akhilesh Reddy) | `ui/`, `protocols/` | Streamlit dashboard, NetworkX drawing, comparison benchmark, TCP/UDP & CRC demos | [`docs/member3_ui_analytics.md`](docs/member3_ui_analytics.md) |

---

## Current Development Status

See [`STATUS.md`](STATUS.md) for module-by-module implementation status.

---

## Future Work (Out of Scope)

The following areas are intentionally out of scope for the 2-week simulation framework:
- Dynamic exterior gateway protocols (BGP, EGP) and full-scale OSPF link-state advertisements.
- Real socket OS-level TCP/IP stack integration.
- IPv6 address support and subnet CIDR prefix matching.
- VLAN tagging, 802.1Q encapsulation, and Ethernet frame switching.
- Application-layer network services (DNS, DHCP, NAT, Firewalls).
- Wireless channels, fading models, and mobility simulations.
- Machine learning / deep reinforcement learning routing policies.
- Live raw packet capture (PCAP) and Wireshark decoding.
- Multi-process distributed router daemons.

---

## License

This project is licensed under the [MIT License](LICENSE).
