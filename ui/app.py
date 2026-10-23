"""Main Streamlit application entry point for NetSim-X (Member 3).

Interactive simulation and analytics platform evaluating Dijkstra, Distance Vector,
and Explainable Adaptive Routing (XAR) across 5 functional tabs:
1. Topology & Forwarding Path
2. Step-by-Step Packet Simulation
3. Network Disruption & Fault Recovery
4. Multi-Algorithm Race Mode & Benchmark Matrix
5. Transport & Data-Link Protocol Lab (TCP/UDP, CRC)
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from network.topology import Topology
from ui.controls import render_disruption_tab, render_sidebar_controls
from ui.dashboard import render_algorithm_comparison_tab
from ui.packet_view import render_packet_simulation_tab
from ui.protocol_lab import render_protocol_lab_tab
from ui.topology_view import render_topology_view
from ui.xar_adapter import resolve_xar_route

# Setup page layout, title, and favicon
st.set_page_config(
    page_title="NetSim-X | Explainable Adaptive Routing & Resilience",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOPOLOGIES_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"


def load_available_topologies() -> Dict[str, Path]:
    """Discover all JSON topology files in data/topologies/."""
    if not TOPOLOGIES_DIR.is_dir():
        return {}
    files = list(TOPOLOGIES_DIR.glob("*.json"))
    return {f.stem: f for f in sorted(files)}


def get_topology_for_scenario(scenario_key: str, available_topologies: Dict[str, Path]) -> Topology:
    """Load and return a clean Topology object for the requested scenario."""
    if scenario_key in available_topologies:
        return Topology.load_json(available_topologies[scenario_key])
    elif available_topologies:
        first_key = list(available_topologies.keys())[0]
        return Topology.load_json(available_topologies[first_key])
    return Topology("empty")


def main() -> None:
    st.title("🌐 NetSim-X: Explainable Adaptive Routing & Resilience")
    st.caption(
        "Interactive simulation framework evaluating Dijkstra, Distance Vector, "
        "and Explainable Adaptive Routing (XAR) under multi-criteria objectives and network disruptions."
    )

    available_topos = load_available_topologies()
    if not available_topos:
        st.error(f"No scenario files found in `{TOPOLOGIES_DIR}`. Please verify project structure.")
        return

    # Initialize authoritative topology state in session_state
    if "selected_scenario_name" not in st.session_state:
        default_scenario = (
            "why_shortest_is_not_best"
            if "why_shortest_is_not_best" in available_topos
            else list(available_topos.keys())[0]
        )
        st.session_state["selected_scenario_name"] = default_scenario
        st.session_state["authoritative_topology"] = get_topology_for_scenario(default_scenario, available_topos)
        st.session_state["original_baseline_topology"] = copy.deepcopy(st.session_state["authoritative_topology"])
        st.session_state["sim_tick"] = 0
        st.session_state["event_log"] = []

    # Render Sidebar Controls
    controls = render_sidebar_controls(
        available_topologies=available_topos,
        active_topology=st.session_state["authoritative_topology"],
    )

    # Handle Scenario Switching or Custom Upload
    if controls["uploaded_topology"] is not None:
        custom_topo = controls["uploaded_topology"]
        if (
            st.session_state.get("selected_scenario_name") != "custom_upload"
            or st.session_state.get("custom_topo_name") != custom_topo.name
        ):
            st.session_state["selected_scenario_name"] = "custom_upload"
            st.session_state["custom_topo_name"] = custom_topo.name
            st.session_state["authoritative_topology"] = copy.deepcopy(custom_topo)
            st.session_state["original_baseline_topology"] = copy.deepcopy(custom_topo)
            st.session_state["sim_tick"] = 0
            st.session_state["event_log"] = []
            st.rerun()

    elif controls["selected_topology_name"] != "Upload Custom JSON":
        new_scenario = controls["selected_topology_name"]
        if new_scenario != st.session_state.get("selected_scenario_name"):
            st.session_state["selected_scenario_name"] = new_scenario
            st.session_state["authoritative_topology"] = get_topology_for_scenario(new_scenario, available_topos)
            st.session_state["original_baseline_topology"] = copy.deepcopy(st.session_state["authoritative_topology"])
            st.session_state["sim_tick"] = 0
            st.session_state["event_log"] = []
            st.rerun()

    # Handle Reset Request
    if controls["reset_requested"]:
        st.session_state["authoritative_topology"] = copy.deepcopy(st.session_state["original_baseline_topology"])
        st.session_state["sim_tick"] = 0
        st.session_state["event_log"] = ["Topology restored to initial scenario baseline."]
        st.rerun()

    authoritative_topo: Topology = st.session_state["authoritative_topology"]
    src = controls["source"]
    dst = controls["destination"]
    algo = controls["algorithm"]
    metric = controls["metric"]
    profile = controls["traffic_profile"]
    algo_label = controls["algorithm_label"]

    # Recompute active route on authoritative topology
    if algo == "xar":
        active_route_res, route_metrics, route_score, is_xar_fallback = resolve_xar_route(
            authoritative_topo, src, dst, profile=profile
        )
    else:
        active_route_res = authoritative_topo.find_route(src, dst, algorithm=algo, metric=metric)
        if active_route_res.get("status") == "success" and active_route_res.get("path"):
            route_metrics = authoritative_topo.get_path_metrics(active_route_res["path"])
        else:
            route_metrics = {}

    st.session_state["selected_route"] = active_route_res
    active_path = active_route_res.get("path", [])

    # Five Functional Tabs Interface
    tabs = st.tabs([
        "🗺️ Topology & Routing",
        "📦 Packet Simulation",
        "⚡ Network Disruption",
        "⚖️ Algorithm Comparison",
        "🔬 Protocol Lab",
    ])

    # TAB 1: Topology
    with tabs[0]:
        render_topology_view(
            authoritative_topo,
            highlighted_path=active_path,
            title=f"{st.session_state['selected_scenario_name']} ({algo_label})",
        )

    # TAB 2: Packet Simulation
    with tabs[1]:
        render_packet_simulation_tab(
            authoritative_topo,
            source=src,
            destination=dst,
            algorithm=algo,
            metric=metric,
            traffic_profile=profile,
        )

    # TAB 3: Network Disruption
    with tabs[2]:
        render_disruption_tab(
            authoritative_topo,
            source=src,
            destination=dst,
            algorithm=algo,
            metric=metric,
            traffic_profile=profile,
            original_topology=st.session_state.get("original_baseline_topology"),
        )

    # TAB 4: Algorithm Comparison
    with tabs[3]:
        render_algorithm_comparison_tab(
            authoritative_topo,
            source=src,
            destination=dst,
            traffic_profile=profile,
        )

    # TAB 5: Protocol Lab
    with tabs[4]:
        render_protocol_lab_tab(
            authoritative_topo,
            active_path=active_path,
        )


if __name__ == "__main__":
    main()
