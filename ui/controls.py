"""UI control widgets and sidebar panels (Member 3).

Provides selection widgets for topologies, endpoints, algorithms, traffic profiles,
and runtime failure triggers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import streamlit as st

if TYPE_CHECKING:
    from network.topology import Topology


def render_sidebar_controls(
    topology: Topology,
    available_topologies: List[str],
) -> Dict[str, Any]:
    """Render the sidebar control panel in Streamlit.

    Args:
        topology: Active Topology instance.
        available_topologies: List of topology file names.

    Returns:
        Dictionary of user selections.
    """
    st.sidebar.title("🎮 NetSim-X Controls")

    selected_topo_name = st.sidebar.selectbox(
        "Load Topology Scenario",
        options=available_topologies,
        index=0,
    )

    node_ids = sorted(list(topology.nodes.keys()))
    default_src_idx = 0
    default_dst_idx = len(node_ids) - 1 if node_ids else 0

    col1, col2 = st.sidebar.columns(2)
    with col1:
        source_node = st.selectbox("Source", options=node_ids, index=default_src_idx)
    with col2:
        dest_node = st.selectbox("Destination", options=node_ids, index=default_dst_idx)

    algorithm = st.sidebar.selectbox(
        "Routing Algorithm",
        options=["Dijkstra (Link State)", "Distance Vector", "XAR (Adaptive)"],
        index=0,
    )

    traffic_profile = st.sidebar.selectbox(
        "Traffic Profile (XAR)",
        options=["Standard", "Real-Time", "Reliable Data Transfer"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("💥 Disruption Injection")
    failed_node = st.sidebar.selectbox(
        "Fail Router / Node",
        options=["None"] + [n for n, node in topology.nodes.items() if node.type == "router"],
        index=0,
    )

    return {
        "selected_topology": selected_topo_name,
        "source": source_node,
        "destination": dest_node,
        "algorithm": algorithm,
        "traffic_profile": traffic_profile,
        "failed_node": failed_node if failed_node != "None" else None,
    }
