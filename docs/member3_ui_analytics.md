# Member 3 Handbook: UI, Analytics & Protocol Demonstrations

**Owner**: Akhilesh Reddy (Member 3)  
**Packages Owned**: `ui/` (`app.py`, `topology_view.py`, `controls.py`, `dashboard.py`, `packet_view.py`), `protocols/` (`tcp_udp.py`, `crc.py`), and corresponding tests in `tests/`.

---

## 1. Purpose & Responsibilities
Akhilesh Reddy builds the interactive front-end and educational protocol demos for NetSim-X.
The UI visualizes the network graph, animates packet flows, allows disruption injection, and compares algorithms side-by-side.

---

## 2. Streamlit Tab-by-Tab Wireframes (ASCII)

```text
========================================================================
|  🌐 NetSim-X: Explainable Adaptive Routing Framework                |
========================================================================
| [Sidebar]          | [Tabs: Topology | Packets | Disruption | Race | Protocols]
| Topo: why_shortest | ------------------------------------------------
| Src: PC1  Dst: PC2 | 🗺️ Topology & Routing Tab:
| Algo: XAR          | +-------------------------+ +-------------------+
| Profile: Standard  | |  [ Matplotlib Graph ]   | | Route Metrics     |
| Fail: None         | |  PC1 - R1 - R3 - R4     | | Latency: 36.0 ms  |
|                    | |       \   /             | | Hops: 5           |
|                    | |        R5 - PC2         | | Loss: 2.9%        |
|                    | +-------------------------+ +-------------------+
------------------------------------------------------------------------
```

### Tab 1: Topology View (`ui/topology_view.py`)
- **Functions called**: `ui.topology_view.draw_topology_graph(topology, highlighted_path)`
- **Behavior**: Renders nodes (green = active routers, red = failed, cyan = hosts) and links (labels showing latency and congestion). The active path is highlighted in thick gold/yellow.

### Tab 2: Packet Simulation (`ui/packet_view.py`)
- **State**: Uses `st.session_state["sim_tick"]`.
- **Functions called**: `simulation.packet_loss.simulate_packet_transmission()` or `adaptive.mock_data`.
- **Behavior**: Advance Tick button adds packets in flight, calculates delivered vs dropped packets, and renders live progress bar.

### Tab 3: Network Disruption & Recovery
- **Functions called**: `network.topology.Topology.set_node_active()`, `simulation.failures.calculate_recovery_time()`.
- **Behavior**: Displays recovery duration breakdown sliders:
  $$\text{Recovery Time} = \text{detection\_delay} + (\text{recomputation\_rounds} \times \text{per\_round\_delay})$$

### Tab 4: Algorithm Comparison (`ui/dashboard.py`)
- **Functions called**: `ui.dashboard.render_comparison_dashboard()`
- **Table Format**:
  | Algorithm | Path | Hop Count | Latency (ms) | Packet Loss | Congestion | Score |
  | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
  | Dijkstra | `PC1 -> R1 -> R2 -> R5 -> PC2` | 4 | 79.0 | 19.17% | 82% | 0.433 |
  | Distance Vector | `PC1 -> R1 -> R2 -> R5 -> PC2` | 4 | 79.0 | 19.17% | 82% | 0.433 |
  | XAR | `PC1 -> R1 -> R3 -> R4 -> R5 -> PC2` | 5 | 36.0 | 3.16% | 12% | 0.180 |

### Tab 5: Protocol Lab (`protocols/tcp_udp.py`, `protocols/crc.py`)
- **Subtab A: TCP vs UDP Demo**:
  - `simulate_tcp_stream(payload_size_kb, rtt_ms, packet_loss_rate)`
  - `simulate_udp_stream(payload_size_kb, rtt_ms, packet_loss_rate)`
- **Subtab B: CRC Polynomial Division**:
  - `compute_crc(data_bits, polynomial)`
  - `verify_crc(received_bits, polynomial)`
  - Visual bitwise division steps and single-bit corruption detection.

---

## 3. Developing Against Mock Data (No Blockers!)
Before Member 2 merges XAR, import fixtures from `adaptive.mock_data`:
```python
from adaptive.mock_data import MOCK_ROUTE_RESULTS

mock = MOCK_ROUTE_RESULTS["why_shortest_is_not_best"]
dijkstra_path = mock["dijkstra"]["path"]
xar_path = mock["xar"]["path"]
explanation = mock["explanation"]
```
This lets you build and polish the dashboard without waiting for any other pull requests!

---

## 4. How to Run the App
```bash
streamlit run ui/app.py
```

---

## 5. Definition of Done Checklist for Akhilesh Reddy
- [ ] Working interactive Streamlit app with all 5 functional tabs.
- [ ] Network graph renders with dynamic path highlighting.
- [ ] Comparison table updates cleanly based on active topology.
- [ ] Protocol Lab shows TCP retransmissions and CRC bitwise division.
- [ ] Unskip and pass tests in `tests/test_ui_components.py`, `test_tcp_udp.py`, and `test_crc.py`.
- [ ] Update `STATUS.md` on every PR.
