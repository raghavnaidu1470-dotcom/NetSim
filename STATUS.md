# NetSim-X Module Implementation Status

This document tracks the current development status of all project components. **Rule: Update this file on every Pull Request.**

| Module Path | Owner | Origin | Current State | Next Action |
| :--- | :--- | :--- | :---: | :--- |
| `network/devices.py` | Member 1 (Ragghav Kamaraj) | Member 1 (implemented) | ⏳ **Verified (Pending CI)** | Core schemas, models, and IPv4 validation complete (passes all 44 unit tests locally; pending remote CI run). |
| `network/topology.py` | Member 1 (Ragghav Kamaraj) | Member 1 (implemented) | ⏳ **Verified (Pending CI)** | JSON load/save round trip, graph builder, path enumeration, duplicate IP checks complete (passes all 44 unit tests locally; pending remote CI run). |
| `network/link_state.py` | Member 1 (Ragghav Kamaraj) | Member 1 (implemented) | ⏳ **Verified (Pending CI)** | Dijkstra shortest path algorithm with hop & latency metrics and deterministic tie-breaking complete (passes all 44 unit tests locally; pending remote CI run). |
| `network/distance_vector.py` | Member 1 (Ragghav Kamaraj) | Member 1 (implemented) | ⏳ **Verified (Pending CI)** | Round-by-round Bellman-Ford, per-round logs, configurable infinity (16), and reconvergence complete (passes all 44 unit tests locally; pending remote CI run). |
| `network/routing_table.py` | Member 1 (Ragghav Kamaraj) | Member 1 (implemented) | ⏳ **Verified (Pending CI)** | Routing table generation, failure invalidation (node & link), and ASCII pretty-printing complete (passes all 44 unit tests locally; pending remote CI run). |
| `data/topologies/*.json` | Member 1 (Ragghav Kamaraj) | Member 1 (implemented) | ⏳ **Verified (Pending CI)** | 3 demo scenario topologies written, validated, and verified via `scripts/verify_demos.py` (passes all 44 unit tests locally; pending remote CI run). |
| `adaptive/traffic_profiles.py` | Member 2 (Harish) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, test, and either approve or modify profile definitions and weights. |
| `adaptive/metrics.py` | Member 2 (Harish) | Stub | 🟡 **Stub** | Implement metric aggregation and unit normalization functions. |
| `adaptive/xar.py` | Member 2 (Harish) | Stub | 🟡 **Stub** | Implement candidate path scoring and route selection. |
| `adaptive/explanation.py` | Member 2 (Harish) | Stub | 🟡 **Stub** | Implement route comparison and natural-language explanation generator. |
| `adaptive/mock_data.py` | Member 2 (Harish) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, test, and either approve or modify mock fixtures. |
| `simulation/failures.py` | Member 2 (Harish) | Stub | 🟡 **Stub** | Implement node/link failure triggers and recovery time tracking. |
| `simulation/congestion.py` | Member 2 (Harish) | Stub | 🟡 **Stub** | Implement dynamic link congestion modifications. |
| `simulation/packet_loss.py` | Member 2 (Harish) | Stub | 🟡 **Stub** | Implement stochastic packet drop simulation. |
| `ui/app.py` | Member 3 (Akhilesh Reddy) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, run, and either approve or modify 5-tab application shell. |
| `ui/topology_view.py` | Member 3 (Akhilesh Reddy) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, test, and either approve or modify Matplotlib/NetworkX visualizer. |
| `ui/controls.py` | Member 3 (Akhilesh Reddy) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, test, and either approve or modify sidebar controls and parameter inputs. |
| `ui/dashboard.py` | Member 3 (Akhilesh Reddy) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, test, and either approve or modify benchmark table renderer. |
| `ui/packet_view.py` | Member 3 (Akhilesh Reddy) | Scaffolded (AI) - owner to review and extend | 🛠️ **Scaffolded - pending owner review** | Owner to read, test, and either approve or modify packet transmission and delivery view. |
| `protocols/tcp_udp.py` | Member 3 (Akhilesh Reddy) | Stub | 🟡 **Stub** | Implement TCP 3-way handshake and sliding window logic. |
| `protocols/crc.py` | Member 3 (Akhilesh Reddy) | Stub | 🟡 **Stub** | Implement bitwise polynomial division and error detection. |

---

> **Note**: Files marked **Scaffolded** were generated to unblock integration and must be reviewed and owned by their members before submission.
