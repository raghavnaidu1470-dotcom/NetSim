"""Packet simulation animation, stepping, and statistics view (Member 3).

Renders tick-based packet stepping across hops, deterministic N-packet loss simulations,
router forwarding tables, and Distance Vector convergence logs.
"""

from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from network.distance_vector import simulate_distance_vector_convergence
from network.routing_table import build_routing_table
from ui.xar_adapter import resolve_xar_route

if TYPE_CHECKING:
    from network.topology import Topology


def render_packet_simulation_view(
    path: List[str],
    metrics: Dict[str, Any],
) -> None:
    """Legacy backward-compatible packet metrics display."""
    if not path or len(path) < 2:
        st.warning("Select valid source and destination endpoints to simulate packet transmission.")
        return

    st.markdown(f"**Forwarding Path**: `{' ➔ '.join(path)}`")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Sent", f"{metrics.get('packets_sent', 100)} pkts")
    with c2:
        st.metric("Delivered", f"{metrics.get('packets_delivered', 98)} pkts")
    with c3:
        st.metric("Dropped", f"{metrics.get('packets_dropped', 2)} pkts")
    with c4:
        st.metric("Delivery Ratio", f"{metrics.get('delivery_ratio', 0.98)*100:.1f}%")

    loss_ratio = metrics.get("delivery_ratio", 0.98)
    st.progress(float(min(1.0, max(0.0, loss_ratio))))


def render_packet_simulation_tab(
    topology: Topology,
    source: str,
    destination: str,
    algorithm: str = "dijkstra",
    metric: str = "hop",
    traffic_profile: str = "standard",
) -> None:
    """Render complete Tab 2: Packet Simulation view."""
    st.subheader("📦 Step-by-Step Packet Simulation & Transport Analytics")

    # Graceful handling of invalid endpoints
    if source not in topology.nodes or destination not in topology.nodes:
        st.warning("⚠️ One or both selected endpoint nodes do not exist in the active topology.")
        return

    if source == destination:
        st.info(f"ℹ️ Source node `{source}` and destination `{destination}` are identical. Packet delivery is instantaneous (0 ms, 0 hops).")
        return

    if not topology.nodes[source].active or not topology.nodes[destination].active:
        inactive = [n for n in (source, destination) if not topology.nodes[n].active]
        st.error(f"❌ Cannot transmit packets: Endpoint device(s) offline / crashed: {', '.join(inactive)}")
        return

    # Compute path
    algo_key = algorithm.lower().strip()
    if "xar" in algo_key:
        route_res, _, _, _ = resolve_xar_route(topology, source, destination, profile=traffic_profile)
    else:
        route_res = topology.find_route(source, destination, algorithm=algo_key, metric=metric)

    if route_res.get("status") != "success" or not route_res.get("path"):
        st.error(f"❌ No active forwarding path available between `{source}` and `{destination}`.")
        st.caption("All candidate physical routes are severed or blocked by inactive routers.")
        return

    path: List[str] = route_res["path"]
    total_hops = len(path) - 1

    # Session state initialization for tick simulation
    if "pkt_sim_hop" not in st.session_state:
        st.session_state["pkt_sim_hop"] = 0
    if "pkt_sim_log" not in st.session_state:
        st.session_state["pkt_sim_log"] = []
    if "pkt_sim_path" not in st.session_state or st.session_state["pkt_sim_path"] != path:
        st.session_state["pkt_sim_path"] = path
        st.session_state["pkt_sim_hop"] = 0
        st.session_state["pkt_sim_log"] = [f"[Init] Route established: {' ➔ '.join(path)}"]

    st.markdown(f"**Active Route**: `{' ➔ '.join(path)}` (`{total_hops}` hops, `{route_res.get('latency', 0.0)}` ms total latency)")

    # 1. Tick-based Hop Stepping
    st.markdown("### ⏱️ Hop-by-Hop Transmission Stepper")
    current_hop = st.session_state["pkt_sim_hop"]
    current_node = path[min(current_hop, total_hops)]

    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 1])
    with col_btn1:
        if st.button("🚀 Send New Packet"):
            st.session_state["pkt_sim_hop"] = 0
            st.session_state["pkt_sim_log"] = [f"[0.0 ms] Packet created at source `{source}`"]
            st.rerun()

    with col_btn2:
        if st.button("⏩ Step (+1 Hop)"):
            if current_hop < total_hops:
                u = path[current_hop]
                v = path[current_hop + 1]
                link = topology.get_link(u, v)
                lat = link.latency if link else 0.0
                cong = int(link.congestion * 100) if link else 0
                st.session_state["pkt_sim_hop"] += 1
                new_hop = st.session_state["pkt_sim_hop"]
                st.session_state["pkt_sim_log"].append(
                    f"Hop {new_hop}/{total_hops}: `{u}` ➔ `{v}` (Delay: {lat:.1f}ms | Congestion: {cong}%)"
                )
                if new_hop == total_hops:
                    st.session_state["pkt_sim_log"].append(f"🏁 Packet successfully delivered to destination `{destination}`!")
                st.rerun()

    with col_btn3:
        if st.button("⏭️ Fast-Forward to End"):
            while st.session_state["pkt_sim_hop"] < total_hops:
                u = path[st.session_state["pkt_sim_hop"]]
                v = path[st.session_state["pkt_sim_hop"] + 1]
                link = topology.get_link(u, v)
                lat = link.latency if link else 0.0
                st.session_state["pkt_sim_hop"] += 1
                new_hop = st.session_state["pkt_sim_hop"]
                st.session_state["pkt_sim_log"].append(
                    f"Hop {new_hop}/{total_hops}: `{u}` ➔ `{v}` (Delay: {lat:.1f}ms)"
                )
            st.session_state["pkt_sim_log"].append(f"🏁 Packet successfully delivered to destination `{destination}`!")
            st.rerun()

    with col_btn4:
        if st.button("🔄 Reset Stepper"):
            st.session_state["pkt_sim_hop"] = 0
            st.session_state["pkt_sim_log"] = [f"[Reset] Ready to transmit from `{source}`"]
            st.rerun()

    # Progress and status
    prog_ratio = current_hop / total_hops if total_hops > 0 else 1.0
    st.progress(float(min(1.0, max(0.0, prog_ratio))))

    # Compute current cumulative latency
    cum_lat = 0.0
    for i in range(current_hop):
        l = topology.get_link(path[i], path[i + 1])
        if l:
            cum_lat += l.latency

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Packet Location", f"Node {current_node}")
    with m2:
        st.metric("Hops Traversed", f"{current_hop} / {total_hops}")
    with m3:
        st.metric("Cumulative Delay", f"{cum_lat:.1f} ms")
    with m4:
        status_label = "In Flight 🚀" if current_hop < total_hops else "Delivered 🏁"
        st.metric("Status", status_label)

    # Event log
    with st.expander("📜 Step-by-Step Packet Event Log", expanded=True):
        for log_line in reversed(st.session_state["pkt_sim_log"]):
            st.text(log_line)

    st.markdown("---")

    # 2. Batch N-Packet Transmission Simulation
    st.markdown("### 📊 Multi-Packet Stochastic Flow Simulation")
    st.caption("Simulate streaming N packets across the active path using link packet loss rates.")

    col_n, col_seed = st.columns(2)
    with col_n:
        n_packets = st.slider("Number of Packets (N)", min_value=10, max_value=500, value=100, step=10)
    with col_seed:
        sim_seed = st.number_input("Random Seed (Reproducible)", min_value=1, max_value=9999, value=42)

    path_m = topology.get_path_metrics(path)
    loss_rate = path_m["packet_loss"]

    rng = random.Random(int(sim_seed))
    dropped_count = 0
    for _ in range(n_packets):
        if rng.random() < loss_rate:
            dropped_count += 1
    delivered_count = n_packets - dropped_count
    ratio = delivered_count / n_packets if n_packets > 0 else 1.0

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.metric("Total Streamed", f"{n_packets} pkts")
    with b2:
        st.metric("Delivered", f"{delivered_count} pkts", delta="Success")
    with b3:
        st.metric("Dropped in Transit", f"{dropped_count} pkts", delta=f"{loss_rate*100:.1f}% path loss", delta_color="inverse")
    with b4:
        st.metric("Delivery Reliability", f"{ratio * 100:.1f}%")

    st.progress(float(min(1.0, max(0.0, ratio))))

    st.markdown("---")

    # 3. Router Forwarding Table Inspector
    st.markdown("### 🧭 Router Forwarding Table Inspector")
    routers = [nid for nid, node in sorted(topology.nodes.items()) if node.type == "router" and node.active]
    if routers:
        default_router = path[1] if len(path) > 2 and path[1] in routers else routers[0]
        selected_router = st.selectbox("Inspect Forwarding Table for Router", options=routers, index=routers.index(default_router))
        rt = build_routing_table(topology, selected_router, algorithm=algo_key, metric=metric)
        rt_records = [
            {
                "Destination": e.destination_id,
                "Destination IP": e.destination_ip,
                "Next Hop": e.next_hop_id or "Direct",
                "Next Hop IP": e.next_hop_ip or "-",
                "Cost Metric": f"{e.metric:.1f}",
                "Hops": e.hop_count,
                "Status": "Active" if e.status == "active" else "Unreachable",
            }
            for e in rt.entries.values()
        ]
        st.dataframe(pd.DataFrame(rt_records), use_container_width=True, hide_index=True)
    else:
        st.info("No active routers in current topology.")

    # 4. Distance Vector Convergence Rounds Log
    with st.expander("🔄 Distance Vector Protocol Convergence Analysis", expanded=False):
        st.caption("Displays round-by-round Bellman-Ford message exchange iterations on current topology snapshot.")
        try:
            topo_copy = copy.deepcopy(topology)
            sim_dv = simulate_distance_vector_convergence(topo_copy, metric=metric, return_log=True)
            dv_tables, dv_rounds, dv_converged, dv_log = sim_dv  # type: ignore

            st.write(f"- **Convergence Rounds Required**: `{dv_rounds}` rounds")
            st.write(f"- **Converged Successfully**: `{'Yes ✅' if dv_converged else 'No (Count-to-Infinity) ❌'}`")

            if dv_log:
                log_records = []
                for entry in dv_log:
                    round_num = entry.get("round", 0)
                    for node_id, updates in entry.get("updates", {}).items():
                        log_records.append({
                            "Round": round_num,
                            "Node": node_id,
                            "Destination": updates.get("dest", "-"),
                            "New Cost": updates.get("cost", "-"),
                            "New Next Hop": updates.get("next_hop", "-"),
                        })
                if log_records:
                    st.dataframe(pd.DataFrame(log_records), use_container_width=True, hide_index=True)
                else:
                    st.write("No distance vector updates required after round 0.")
        except Exception as e:
            st.info(f"Distance vector convergence details unavailable: {e}")
