"""UI control widgets, sidebar configurations, and network disruption panel (Member 3).

Provides sidebar parameter selectors, scenario loaders, and the interactive Network
Disruption and Recovery tab with real-time before/after rerouting analysis.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from network.distance_vector import simulate_distance_vector_reconvergence
from network.topology import Topology
from ui.xar_adapter import resolve_xar_route

try:
    from simulation.failures import calculate_recovery_time
except (ImportError, NotImplementedError):
    calculate_recovery_time = None  # type: ignore


def compute_recovery_time_fallback(
    detection_delay_ms: float,
    recomputation_rounds: int,
    per_round_delay_ms: float = 50.0,
) -> Tuple[float, str]:
    """Compute recovery time using spec formula: detection_delay + (recomputation_rounds * per_round_delay).

    Returns:
        Tuple of (recovery_time_ms, calculation_origin_label).
    """
    if calculate_recovery_time is not None:
        try:
            val = calculate_recovery_time(
                detection_delay_ms=detection_delay_ms,
                recomputation_rounds=recomputation_rounds,
                per_round_delay_ms=per_round_delay_ms,
            )
            return float(val), "computed by simulation.failures.calculate_recovery_time"
        except (NotImplementedError, Exception):
            pass

    # Spec formula fallback
    time_ms = float(detection_delay_ms + (recomputation_rounds * per_round_delay_ms))
    return time_ms, "computed by UI from spec formula"


def render_sidebar_controls(
    available_topologies: Dict[str, Path],
    active_topology: Topology,
) -> Dict[str, Any]:
    """Render the sidebar controls panel in Streamlit.

    Args:
        available_topologies: Dictionary mapping scenario names to Path objects.
        active_topology: Currently loaded Topology in session state.

    Returns:
        Dictionary of user control selections.
    """
    st.sidebar.title("🎮 NetSim-X Controls")

    # 1. Topology Scenario Selection & Custom Upload
    topo_options = list(available_topologies.keys()) + ["Upload Custom JSON"]
    default_topo_idx = (
        topo_options.index("why_shortest_is_not_best")
        if "why_shortest_is_not_best" in topo_options
        else 0
    )

    selected_topo_name = st.sidebar.selectbox(
        "📂 Topology Scenario",
        options=topo_options,
        index=default_topo_idx,
        help="Select a curated benchmark topology scenario or upload a custom JSON schema.",
    )

    uploaded_topology: Optional[Topology] = None
    if selected_topo_name == "Upload Custom JSON":
        uploaded_file = st.sidebar.file_uploader("Upload Topology JSON", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                uploaded_topology = Topology.from_dict(data)
                st.sidebar.success(f"Loaded '{uploaded_topology.name}' ({len(uploaded_topology.nodes)} nodes)")
            except Exception as e:
                st.sidebar.error(f"Failed to parse topology JSON: {e}")

    # Use active topology for endpoint dropdowns
    curr_topo = uploaded_topology if uploaded_topology is not None else active_topology
    node_ids = sorted(list(curr_topo.nodes.keys()))

    default_src_idx = 0
    default_dst_idx = len(node_ids) - 1 if node_ids else 0
    if "PC1" in node_ids:
        default_src_idx = node_ids.index("PC1")
    if "PC2" in node_ids:
        default_dst_idx = node_ids.index("PC2")

    st.sidebar.markdown("### 📍 Endpoints")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        source_node = st.selectbox("Source", options=node_ids, index=default_src_idx)
    with col2:
        dest_node = st.selectbox("Destination", options=node_ids, index=default_dst_idx)

    # 2. Routing Protocol Selection
    st.sidebar.markdown("### ⚙️ Routing Configuration")
    algorithm_label = st.sidebar.selectbox(
        "Routing Protocol",
        options=[
            "Dijkstra (Hop Count)",
            "Dijkstra (Latency)",
            "Distance Vector",
            "XAR (Explainable Adaptive)",
        ],
        index=0,
    )

    algo_mapping = {
        "Dijkstra (Hop Count)": ("dijkstra", "hop"),
        "Dijkstra (Latency)": ("dijkstra", "latency"),
        "Distance Vector": ("distance_vector", "hop"),
        "XAR (Explainable Adaptive)": ("xar", "hop"),
    }
    algo_key, metric_key = algo_mapping[algorithm_label]

    traffic_profile = st.sidebar.selectbox(
        "XAR Traffic Profile",
        options=["Standard", "Real-Time", "Reliable Data Transfer"],
        index=0,
        help="Adjusts penalty weights for latency, hops, loss, and reliability in XAR.",
    )

    st.sidebar.markdown("---")
    reset_clicked = st.sidebar.button("🔄 Reset to Original Scenario", use_container_width=True)

    return {
        "selected_topology_name": selected_topo_name,
        "uploaded_topology": uploaded_topology,
        "source": source_node,
        "destination": dest_node,
        "algorithm": algo_key,
        "metric": metric_key,
        "algorithm_label": algorithm_label,
        "traffic_profile": traffic_profile.lower().replace(" ", "_").replace("-", "_"),
        "reset_requested": reset_clicked,
    }


def render_disruption_tab(
    topology: Topology,
    source: str,
    destination: str,
    algorithm: str = "dijkstra",
    metric: str = "hop",
    traffic_profile: str = "standard",
    original_topology: Optional[Topology] = None,
) -> None:
    """Render complete Tab 3: Network Disruption & Resilience analysis view."""
    st.subheader("⚡ Network Disruption, Fault Injection & Dynamic Recovery")
    st.caption(
        "Inject router crashes, link cuts, and congestion bursts to observe dynamic protocol rerouting "
        "and calculate recovery durations."
    )

    # 1. Pre-failure baseline route resolution
    baseline_topo = original_topology if original_topology is not None else copy.deepcopy(topology)
    if "xar" in algorithm.lower():
        prev_route, prev_metrics, _, _ = resolve_xar_route(baseline_topo, source, destination, profile=traffic_profile)
    else:
        prev_route = baseline_topo.find_route(source, destination, algorithm=algorithm, metric=metric)

    # Disruption Trigger Controls
    st.markdown("### 🛠️ Fault Injection Controls")
    col_routers, col_links = st.columns(2)

    with col_routers:
        st.markdown("**Router Deactivation / Recovery**")
        active_routers = [nid for nid, n in sorted(topology.nodes.items()) if n.type == "router" and n.active]
        inactive_routers = [nid for nid, n in sorted(topology.nodes.items()) if n.type == "router" and not n.active]

        c_f1, c_f2 = st.columns([2, 1])
        with c_f1:
            router_to_fail = st.selectbox("Select Active Router to Crash", options=["None"] + active_routers, index=0)
        with c_f2:
            if st.button("💥 Crash Router") and router_to_fail != "None":
                topology.set_node_active(router_to_fail, False)
                st.session_state["authoritative_topology"] = topology
                st.session_state["last_disruption"] = f"Router '{router_to_fail}' crashed"
                st.rerun()

        if inactive_routers:
            c_r1, c_r2 = st.columns([2, 1])
            with c_r1:
                router_to_restore = st.selectbox("Select Inactive Router to Restore", options=inactive_routers, index=0)
            with c_r2:
                if st.button("🟢 Restore Router"):
                    topology.set_node_active(router_to_restore, True)
                    st.session_state["authoritative_topology"] = topology
                    st.session_state["last_disruption"] = f"Router '{router_to_restore}' restored"
                    st.rerun()

    with col_links:
        st.markdown("**Link Severance / Recovery**")
        active_links = [f"{l.source} ↔ {l.destination}" for l in topology.links if l.active]
        inactive_links = [f"{l.source} ↔ {l.destination}" for l in topology.links if not l.active]

        c_l1, c_l2 = st.columns([2, 1])
        with c_l1:
            link_to_cut = st.selectbox("Select Active Link to Cut", options=["None"] + active_links, index=0)
        with c_l2:
            if st.button("✂️ Sever Link") and link_to_cut != "None":
                u, v = link_to_cut.split(" ↔ ")
                topology.set_link_active(u, v, False)
                st.session_state["authoritative_topology"] = topology
                st.session_state["last_disruption"] = f"Link '{u} ↔ {v}' severed"
                st.rerun()

        if inactive_links:
            c_lr1, c_lr2 = st.columns([2, 1])
            with c_lr1:
                link_to_restore = st.selectbox("Select Severed Link to Restore", options=inactive_links, index=0)
            with c_lr2:
                if st.button("🔌 Reconnect Link"):
                    u, v = link_to_restore.split(" ↔ ")
                    topology.set_link_active(u, v, True)
                    st.session_state["authoritative_topology"] = topology
                    st.session_state["last_disruption"] = f"Link '{u} ↔ {v}' reconnected"
                    st.rerun()

    # One-click failure scenario: fail the router current path uses
    st.markdown("### 🎯 One-Click Targeted Scenarios")
    prev_path = prev_route.get("path", [])
    intermediate_routers = [
        n for n in prev_path[1:-1]
        if n in topology.nodes and topology.nodes[n].type == "router" and topology.nodes[n].active
    ]

    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if intermediate_routers:
            target_router = intermediate_routers[0]
            if st.button(f"💥 One-Click Disruption: Fail Critical Path Router ({target_router})"):
                topology.set_node_active(target_router, False)
                st.session_state["authoritative_topology"] = topology
                st.session_state["last_disruption"] = f"Failed path bottleneck router '{target_router}'"
                st.rerun()
        else:
            st.button("💥 One-Click Disruption: No active intermediate routers on path", disabled=True)

    with col_demo2:
        if st.button("♻️ Restore All Components to Operational State"):
            for n in topology.nodes.values():
                n.active = True
            for l in topology.links:
                l.active = True
            st.session_state["authoritative_topology"] = topology
            st.session_state["last_disruption"] = "All components restored"
            st.rerun()

    st.markdown("---")

    # Link Metric Sliders (Congestion, Latency, Loss)
    with st.expander("🎛️ Dynamic Link Metric Tuning (Inject Congestion & Delay)", expanded=False):
        link_names = [f"{l.source} ↔ {l.destination}" for l in topology.links if l.active]
        if link_names:
            selected_tune_link = st.selectbox("Select Link to Tune", options=link_names)
            u_t, v_t = selected_tune_link.split(" ↔ ")
            target_l = topology.get_link(u_t, v_t)
            if target_l:
                c_tune1, c_tune2, c_tune3 = st.columns(3)
                with c_tune1:
                    new_cong = st.slider("Link Congestion", 0.0, 1.0, float(target_l.congestion), 0.05)
                with c_tune2:
                    new_lat = st.slider("Link Latency (ms)", 1.0, 150.0, float(target_l.latency), 1.0)
                with c_tune3:
                    new_loss = st.slider("Link Packet Loss", 0.0, 0.50, float(target_l.packet_loss), 0.01)

                if st.button("Apply Link Metric Changes"):
                    topology.update_link_metrics(u_t, v_t, latency=new_lat, congestion=new_cong, packet_loss=new_loss)
                    st.session_state["authoritative_topology"] = topology
                    st.session_state["last_disruption"] = f"Updated metrics on link '{u_t} ↔ {v_t}'"
                    st.rerun()

    # Recompute route on current active topology
    if "xar" in algorithm.lower():
        curr_route, curr_metrics, _, _ = resolve_xar_route(topology, source, destination, profile=traffic_profile)
    else:
        curr_route = topology.find_route(source, destination, algorithm=algorithm, metric=metric)

    st.markdown("### 📊 Before vs After Failure Rerouting Impact")
    col_bef, col_aft = st.columns(2)

    with col_bef:
        st.markdown("**Original Baseline Path**")
        if prev_route.get("status") == "success":
            st.success(f"`{' ➔ '.join(prev_route['path'])}`")
            st.write(f"- **Hops**: `{prev_route['hop_count']}` hops")
            st.write(f"- **Latency**: `{prev_route['latency']:.1f}` ms")
        else:
            st.error("Baseline route was unavailable.")

    with col_aft:
        st.markdown("**Rerouted Path (Post-Disruption)**")
        if curr_route.get("status") == "success":
            st.success(f"`{' ➔ '.join(curr_route['path'])}`")
            st.write(f"- **Hops**: `{curr_route['hop_count']}` hops")
            st.write(f"- **Latency**: `{curr_route['latency']:.1f}` ms")
        else:
            st.error("❌ Destination Unreachable: Network is disconnected!")

    # Quantitative Deltas
    st.markdown("### 📈 Recovery Metrics & Convergence Calculation")
    hops_delta = curr_route.get("hop_count", 0) - prev_route.get("hop_count", 0)
    lat_delta = curr_route.get("latency", 0.0) - prev_route.get("latency", 0.0)

    # Calculate reconvergence rounds via DV or spec formula
    dv_reconv_rounds = 4  # default standard
    try:
        dv_sim = simulate_distance_vector_reconvergence(copy.deepcopy(baseline_topo), metric=metric)
        if "reconvergence_rounds" in dv_sim:
            dv_reconv_rounds = max(1, int(dv_sim["reconvergence_rounds"]))
    except Exception:
        pass

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        det_delay = st.slider("Detection Delay T_detect (ms)", 50.0, 500.0, 150.0, 25.0)
    with col_s2:
        recomp_rounds = st.slider(
            "Recomputation Rounds N_rounds", 1, 15, dv_reconv_rounds, 1,
            help="Derived from simulate_distance_vector_reconvergence or manual override.",
        )
    with col_s3:
        per_round_delay = st.slider("Round Propagation T_round (ms)", 10.0, 100.0, 50.0, 5.0)

    total_rec_time, origin_label = compute_recovery_time_fallback(
        detection_delay_ms=det_delay,
        recomputation_rounds=recomp_rounds,
        per_round_delay_ms=per_round_delay,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            "Recovery Time",
            f"{total_rec_time:.1f} ms",
            help=f"Formula: T_detect + (N_rounds * T_round). Origin: {origin_label}",
        )
    with k2:
        delta_str = f"{hops_delta:+d} hops" if hops_delta != 0 else "0 hops"
        st.metric("Hop Delta", delta_str, delta=hops_delta, delta_color="inverse")
    with k3:
        delta_lat_str = f"{lat_delta:+.1f} ms" if lat_delta != 0 else "0 ms"
        st.metric("Latency Delta", delta_lat_str, delta=round(lat_delta, 1), delta_color="inverse")
    with k4:
        route_status = "Rerouted 🔄" if curr_route.get("path") != prev_route.get("path") else "Stable 🟢"
        if curr_route.get("status") != "success":
            route_status = "Disconnected ❌"
        st.metric("Route State", route_status)

    st.caption(
        f"ℹ️ **Recovery calculation**: `{origin_label}`: "
        f"${det_delay:.0f}ms + ({recomp_rounds} \\times {per_round_delay:.0f}ms) = {total_rec_time:.1f}ms$"
    )
