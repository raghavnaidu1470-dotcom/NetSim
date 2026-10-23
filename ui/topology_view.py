"""Topology visualization and graph analytics component (Member 3).

Renders the network topology graph using NetworkX and Matplotlib with distinct node styles
(routers vs hosts, active vs failed), link metrics (latency, loss %, congestion %),
and route highlights, alongside node and link inventory tables.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

if TYPE_CHECKING:
    from network.topology import Topology


def draw_topology_graph(
    topology: Topology,
    highlighted_path: Optional[List[str]] = None,
    title: str = "NetSim-X Topology",
) -> plt.Figure:
    """Render the topology graph as a Matplotlib Figure.

    Hosts and routers are styled with distinctive colors and shapes:
    - Hosts: Teal / Cyan (#17a2b8) square nodes
    - Active Routers: Emerald Green (#28a745) circular nodes
    - Inactive / Failed Nodes: Crimson / Red (#dc3545) with greyed border
    - Inactive Links: Dashed crimson lines
    - Active Unselected Links: Slate grey solid lines
    - Highlighted Route: Thick vibrant gold (#ffc107) path

    Args:
        topology: Topology instance to visualize.
        highlighted_path: Ordered list of node IDs along active route.
        title: Figure title.

    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#ffffff")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=14, color="#212529")

    G = nx.Graph()
    host_nodes: List[str] = []
    router_active_nodes: List[str] = []
    failed_nodes: List[str] = []
    node_labels: Dict[str, str] = {}

    for node_id, node in topology.nodes.items():
        G.add_node(node_id)
        node_labels[node_id] = f"{node_id}\n{node.ip}"
        if not node.active:
            failed_nodes.append(node_id)
        elif node.type == "host":
            host_nodes.append(node_id)
        else:
            router_active_nodes.append(node_id)

    for link in topology.links:
        if link.source in topology.nodes and link.destination in topology.nodes:
            G.add_edge(
                link.source,
                link.destination,
                latency=link.latency,
                congestion=link.congestion,
                packet_loss=link.packet_loss,
                reliability=link.reliability,
                active=link.active,
            )

    pos = nx.spring_layout(G, seed=42, k=1.2)

    # 1. Draw Inactive / Broken Links
    inactive_edges = [
        (u, v) for u, v, d in G.edges(data=True) if not d.get("active", True)
    ]
    if inactive_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=inactive_edges,
            ax=ax,
            edge_color="#dc3545",
            style="dashed",
            width=2.5,
            alpha=0.7,
        )

    # 2. Draw Active Route Edges
    path_edge_set = set()
    highlight_edges = []
    if highlighted_path and len(highlighted_path) >= 2:
        for i in range(len(highlighted_path) - 1):
            u, v = highlighted_path[i], highlighted_path[i + 1]
            path_edge_set.add((u, v))
            path_edge_set.add((v, u))
            highlight_edges.append((u, v))

    # 3. Draw Normal Active Links
    normal_edges = [
        (u, v)
        for u, v, d in G.edges(data=True)
        if d.get("active", True) and (u, v) not in path_edge_set
    ]
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=normal_edges,
        ax=ax,
        edge_color="#6c757d",
        width=1.8,
        alpha=0.6,
    )

    if highlight_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=highlight_edges,
            ax=ax,
            edge_color="#f39c12",
            width=4.5,
            alpha=0.95,
        )

    # 4. Draw Nodes with distinctive styles
    if host_nodes:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=host_nodes,
            ax=ax,
            node_color="#17a2b8",
            node_shape="s",
            node_size=1300,
            edgecolors="#0f6674",
            linewidths=2.0,
            label="Host",
        )

    if router_active_nodes:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=router_active_nodes,
            ax=ax,
            node_color="#28a745",
            node_shape="o",
            node_size=1400,
            edgecolors="#1e7e34",
            linewidths=2.0,
            label="Active Router",
        )

    if failed_nodes:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=failed_nodes,
            ax=ax,
            node_color="#dc3545",
            node_shape="X",
            node_size=1400,
            edgecolors="#721c24",
            linewidths=2.0,
            label="Failed Node",
        )

    nx.draw_networkx_labels(
        G,
        pos,
        labels=node_labels,
        ax=ax,
        font_size=8,
        font_weight="bold",
        font_color="#ffffff",
    )

    # 5. Draw Edge Metric Labels
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        if d.get("active", True):
            lat = d.get("latency", 0.0)
            loss_pct = d.get("packet_loss", 0.0) * 100.0
            cong_pct = d.get("congestion", 0.0) * 100.0
            edge_labels[(u, v)] = f"{lat:.0f}ms\nL:{loss_pct:.1f}%\nC:{cong_pct:.0f}%"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=7,
        font_color="#343a40",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#ced4da", alpha=0.85),
    )

    ax.axis("off")
    plt.tight_layout()
    return fig


def render_topology_view(
    topology: Topology,
    highlighted_path: Optional[List[str]] = None,
    title: str = "NetSim-X Topology",
) -> None:
    """Render complete Tab 1 view: visual graph, legend, and node/link tables."""
    st.subheader("🗺️ Network Topology & Forwarding Path")

    col_graph, col_legend = st.columns([4, 1])
    with col_graph:
        fig = draw_topology_graph(topology, highlighted_path=highlighted_path, title=title)
        st.pyplot(fig)
        plt.close(fig)

    with col_legend:
        st.markdown("#### Graph Legend")
        st.markdown(
            "- 🟦 **Host**: Cyan square\n"
            "- 🟢 **Router (Active)**: Green circle\n"
            "- ❌ **Node (Failed)**: Red cross\n"
            "- 🟧 **Active Route**: Gold highlight\n"
            "- ➖ **Active Link**: Grey line\n"
            "- ⛔ **Inactive Link**: Dashed red line"
        )
        if highlighted_path:
            st.info(f"**Highlighted Path**:\n`{' ➔ '.join(highlighted_path)}`")

    st.markdown("---")
    st.markdown("### 📋 Topology Inventory Tables")
    col_nodes, col_links = st.columns(2)

    with col_nodes:
        st.markdown("**Device Nodes**")
        node_records = [
            {
                "Node ID": n.id,
                "IPv4 Address": n.ip,
                "Type": n.type.capitalize(),
                "Operational Status": "Online 🟢" if n.active else "Offline / Crashed 🔴",
            }
            for n in topology.nodes.values()
        ]
        st.dataframe(pd.DataFrame(node_records), use_container_width=True, hide_index=True)

    with col_links:
        st.markdown("**Physical Links**")
        link_records = [
            {
                "Channel": f"{l.source} ↔ {l.destination}",
                "Latency (ms)": f"{l.latency:.1f}",
                "Bandwidth (Mbps)": f"{l.bandwidth:.0f}",
                "Congestion": f"{int(l.congestion * 100)}%",
                "Loss Rate": f"{l.packet_loss * 100:.1f}%",
                "Reliability": f"{l.reliability * 100:.1f}%",
                "Status": "Active" if l.active else "Severed / Down",
            }
            for l in topology.links
        ]
        st.dataframe(pd.DataFrame(link_records), use_container_width=True, hide_index=True)
