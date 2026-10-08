"""Link State Routing (Dijkstra's Algorithm) for NetSim-X.

Simulates link-state routing protocol behavior, where each router has full topology
knowledge (LSDB) and executes Dijkstra's algorithm to compute shortest paths.
"""

from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

import networkx as nx

from network.devices import RouteResult

if TYPE_CHECKING:
    from network.topology import Topology


def link_state_dijkstra(
    topology: Topology,
    source: str,
    destination: str,
    metric: str = "hop",
) -> RouteResult:
    """Compute the shortest path using Link State / Dijkstra's algorithm.

    By default in standard networking pedagogy, hop count (unweighted shortest path)
    or cost metric is used.

    Args:
        topology: The active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        metric: Edge weight metric to minimize: 'hop' (1 per edge) or 'latency'.

    Returns:
        RouteResult dictionary with 'path', 'hop_count', 'latency', 'status'.
    """
    if source not in topology.nodes or destination not in topology.nodes:
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "invalid",
        }

    if not topology.nodes[source].active or not topology.nodes[destination].active:
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
        }

    if source == destination:
        return {
            "path": [source],
            "hop_count": 0,
            "latency": 0.0,
            "status": "success",
        }

    G = topology.to_networkx(only_active=True)
    if source not in G or destination not in G:
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
        }

    weight_attr = "latency" if metric == "latency" else "weight"

    try:
        path = nx.shortest_path(G, source=source, target=destination, weight=weight_attr)
        metrics = topology.get_path_metrics(path)
        return {
            "path": path,
            "hop_count": metrics["hop_count"],
            "latency": metrics["latency"],
            "status": "success",
        }
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
        }


def compute_all_shortest_paths_from_source(
    topology: Topology,
    source: str,
    metric: str = "hop",
) -> Dict[str, List[str]]:
    """Compute shortest paths from a single source to all reachable nodes (Dijkstra Tree).

    Args:
        topology: Active Topology instance.
        source: Source node identifier.
        metric: 'hop' or 'latency'.

    Returns:
        Dictionary mapping destination node ID -> path list.
    """
    if source not in topology.nodes or not topology.nodes[source].active:
        return {}

    G = topology.to_networkx(only_active=True)
    if source not in G:
        return {}

    weight_attr = "latency" if metric == "latency" else "weight"
    paths: Dict[str, List[str]] = {}

    for target in G.nodes():
        if target == source:
            paths[target] = [source]
            continue
        try:
            p = nx.shortest_path(G, source=source, target=target, weight=weight_attr)
            paths[target] = p
        except nx.NetworkXNoPath:
            pass

    return paths
