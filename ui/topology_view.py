"""Topology visualization component using NetworkX and Matplotlib (Member 3).

Renders interactive or static visual graphs showing hosts, routers, links,
and highlighted active routing paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import matplotlib.pyplot as plt
import networkx as nx

if TYPE_CHECKING:
    from network.topology import Topology


def draw_topology_graph(
    topology: Topology,
    highlighted_path: Optional[List[str]] = None,
    title: str = "NetSim-X Topology",
) -> plt.Figure:
    """Render the topology as a Matplotlib Figure.

    Args:
        topology: Topology object to draw.
        highlighted_path: Ordered list of nodes along chosen path to highlight.
        title: Figure title string.

    Returns:
        Matplotlib Figure object for st.pyplot().
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)

    G = nx.Graph()
    node_colors = []
    node_labels = {}

    for node_id, node in topology.nodes.items():
        G.add_node(node_id)
        node_labels[node_id] = f"{node_id}\n{node.ip}"
        if not node.active:
            node_colors.append("#dc3545")  # Red for inactive/failed
        elif node.type == "host":
            node_colors.append("#17a2b8")  # Cyan for hosts
        else:
            node_colors.append("#28a745")  # Green for active routers

    for link in topology.links:
        if link.source in topology.nodes and link.destination in topology.nodes:
            G.add_edge(
                link.source,
                link.destination,
                latency=link.latency,
                congestion=link.congestion,
                active=link.active,
            )

    pos = nx.spring_layout(G, seed=42)

    # Draw inactive links
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
            width=2.0,
        )

    # Draw normal active edges
    path_edge_set = set()
    if highlighted_path and len(highlighted_path) >= 2:
        for i in range(len(highlighted_path) - 1):
            u, v = highlighted_path[i], highlighted_path[i + 1]
            path_edge_set.add((u, v))
            path_edge_set.add((v, u))

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
        width=1.5,
    )

    # Draw highlighted path edges
    if highlighted_path and len(highlighted_path) >= 2:
        highlight_edges = [
            (highlighted_path[i], highlighted_path[i + 1])
            for i in range(len(highlighted_path) - 1)
        ]
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=highlight_edges,
            ax=ax,
            edge_color="#ffc107",
            width=4.0,
        )

    # Draw nodes and labels
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=1200,
        edgecolors="#343a40",
        linewidths=1.5,
    )
    nx.draw_networkx_labels(
        G,
        pos,
        labels=node_labels,
        ax=ax,
        font_size=8,
        font_weight="bold",
    )

    # Draw edge labels (latencies)
    edge_labels = {
        (u, v): f"{d.get('latency', 0)}ms | C:{int(d.get('congestion', 0)*100)}%"
        for u, v, d in G.edges(data=True)
        if d.get("active", True)
    }
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, ax=ax, font_size=7
    )

    ax.axis("off")
    plt.tight_layout()
    return fig
