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

## 3 Demo Scenarios Included

All demo topologies reside in `data/topologies/` and can be loaded directly from the UI or CLI:

1. **`why_shortest_is_not_best.json`**:
   - Demonstrates why minimum hop count is often suboptimal.
   - **Dijkstra (hop-count metric)** picks the 4-hop congested path (`PC1 -> R1 -> R2 -> R5 -> PC2`, 79.0 ms, 82% congestion, 19.17% loss).
   - **XAR** picks the clean 5-hop path (`PC1 -> R1 -> R3 -> R4 -> R5 -> PC2`, 36.0 ms, 12% congestion, 3.16% loss).
   - *Note on metrics*: With a latency metric, Dijkstra would also pick the better 36.0 ms route. The demo intentionally runs Dijkstra on hop count to show the classic shortest-path pitfall where unweighted hop minimization routes traffic directly into a congested bottleneck.
2. **`router_failure.json`**:
   - Normal traffic routes across intermediate router `R2`.
   - Failing `R2` triggers dynamic recovery, showing rerouting over a multi-hop backup path, recovery delay, and packets dropped.
3. **`traffic_profile_change.json`**:
   - Demonstrates profile-directed path selection.
   - Real-Time profile chooses low-latency path despite minor loss; Reliable Data Transfer selects lossless, ultra-reliable path.

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
