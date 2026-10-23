# NetSim-X Presentation Screenshots Guide

This directory holds the official visual artifacts and screenshots captured from the NetSim-X interactive Streamlit dashboard (`ui/app.py`).

> **Note for Presenters**: Do not fabricate or mock screenshot images. Launch the dashboard locally via `streamlit run ui/app.py` and capture clean, full-resolution PNG captures of the active interface matching the catalog below.

---

## Required Screenshot Catalog for Presentation & Final Report

| File Name | Tab / View | Scenario | Key Visual Elements to Capture |
| :--- | :--- | :--- | :--- |
| `01_topology_overview.png` | **Tab 1: Topology & Routing** | `why_shortest_is_not_best.json` | NetworkX/Matplotlib canvas showing cyan square host nodes (`PC1`, `PC2`), emerald green router nodes (`R1`–`R5`), link labels showing latency, packet loss %, and congestion %, and the active path highlighted in gold. Also include the Node and Link inventory dataframes below the graph. |
| `02_packet_simulation_hop_by_hop.png` | **Tab 2: Packet Simulation** | `why_shortest_is_not_best.json` | Hop-by-hop stepper in progress with progress bar partially filled, KPI cards showing current node location, hops traversed, cumulative latency, and the detailed step-by-step event log. |
| `03_packet_simulation_loss_stream.png` | **Tab 2: Packet Simulation** | `why_shortest_is_not_best.json` | Stochastic multi-packet flow section showing N=100 packets streamed, delivery ratio progress bar, delivered vs dropped counts, and the Router Forwarding Table inspector expander. |
| `04_network_disruption_reroute.png` | **Tab 3: Network Disruption** | `router_failure.json` | Before-and-after comparison showing the baseline path (`PC1 -> R1 -> R2 -> PC2`) vs the dynamically rerouted path (`PC1 -> R1 -> R3 -> R4 -> PC2`) after failing `R2`. Capture recovery time sliders and formal recovery duration calculation ($T_{\text{detect}} + N_{\text{rounds}} \times T_{\text{round}} = 350\text{ ms}$). |
| `05_algorithm_comparison_benchmark.png` | **Tab 4: Algorithm Comparison** | `why_shortest_is_not_best.json` | Multi-Algorithm Benchmark Matrix comparing Dijkstra (Hop Count), Dijkstra (Latency), Distance Vector, and XAR side-by-side. Ensure the visible `[Reference preview]` badge on the XAR row is clearly shown. |
| `06_algorithm_comparison_barcharts.png` | **Tab 4: Algorithm Comparison** | `why_shortest_is_not_best.json` | Side-by-side bar charts displaying Latency (ms), Bottleneck Congestion (%), Hop Count, and Multi-Criteria Penalty Score across all four routing strategies, followed by the Explainable Decision Engine ("Why This Route?") card. |
| `07_protocol_lab_tcp_vs_udp.png` | **Tab 5: Protocol Lab** | Subtab A (TCP vs UDP) | Side-by-side comparative cards showing TCP (3-way handshake, retransmissions, 100% reliability, throughput) vs UDP (0 RTT startup, datagram loss, no retransmission), with side-by-side sequence timeline tables. |
| `08_protocol_lab_crc_division.png` | **Tab 5: Protocol Lab** | Subtab B (CRC Error Detection) | Sender modulo-2 polynomial division showing data `1101011011`, appended zeros, CRC-4 remainder `1110`, transmitted frame `11010110111110`, single-bit error injection toggle, and receiver syndrome detection banner (`Syndrome = 0000` vs error detected). |

---

## How to Capture

1. Start the Streamlit application:
   ```bash
   streamlit run ui/app.py
   ```
2. In your browser (e.g. `http://localhost:8501`), set the browser window to full width (1920x1080 recommended).
3. Use your operating system's screenshot utility (e.g., `Cmd + Shift + 4` on macOS) to capture each designated tab.
4. Save the resulting images directly into this `screenshots/` directory matching the exact filenames listed above.
