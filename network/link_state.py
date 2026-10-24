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
    or latency metric is used. On topologies like why_shortest_is_not_best.json,
    Dijkstra (hop-count metric) picks the congested 4-hop path, whereas Dijkstra (latency metric)
    selects the lower-latency 5-hop path. This illustrates the classic shortest-path pitfall.

    Deterministic tie-breaking rule:
    When equal-cost paths exist, ties are resolved first by fewest hops, and then
    lexicographically by node sequence identifiers.

    Args:
        topology: The active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        metric: Edge weight metric to minimize: 'hop'/'hops' (1 per edge) or 'latency'.

    Returns:
        RouteResult dictionary with 'path', 'hop_count', 'latency', 'status', 'message', 'algorithm'.

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/why_shortest_is_not_best.json")
        >>> res = link_state_dijkstra(topo, "PC1", "PC2", metric="hops")
        >>> res["status"]
        'success'
        >>> res["hop_count"]
        4
    """
    normalized_metric = metric.lower().strip()
    if normalized_metric in ("hop", "hops", "hop_count"):
        use_latency = False
    elif normalized_metric == "latency":
        use_latency = True
    else:
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "invalid",
            "message": f"Unsupported Dijkstra metric '{metric}'. Expected 'hops' or 'latency'.",
            "algorithm": "dijkstra",
        }

    if source not in topology.nodes or destination not in topology.nodes:
        missing = [n for n in (source, destination) if n not in topology.nodes]
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "invalid",
            "message": f"Node does not exist in topology: {', '.join(missing)}",
            "algorithm": "dijkstra",
        }

    if not topology.nodes[source].active or not topology.nodes[destination].active:
        inactive = [n for n in (source, destination) if not topology.nodes[n].active]
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
            "message": f"Node is inactive/down: {', '.join(inactive)}",
            "algorithm": "dijkstra",
        }

    if source == destination:
        return {
            "path": [source],
            "hop_count": 0,
            "latency": 0.0,
            "status": "success",
            "message": "Source and destination are identical",
            "algorithm": "dijkstra",
        }

    G = topology.to_networkx(only_active=True)
    if source not in G or destination not in G:
        return {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
            "message": f"Source '{source}' or destination '{destination}' is not present in active graph",
            "algorithm": "dijkstra",
        }

    # Priority queue: (cost, hop_count, path)
    # Natural tuple comparison guarantees deterministic tie-break:
    # 1. lowest cost
    # 2. fewest hops
    # 3. lexicographical path comparison
    heap: List[Tuple[float, int, List[str]]] = [(0.0, 0, [source])]
    best_cost: Dict[str, float] = {source: 0.0}
    visited: Set[str] = set()
    target_path: Optional[List[str]] = None

    while heap:
        cost, hops, path = heapq.heappop(heap)
        curr = path[-1]

        if curr == destination:
            target_path = path
            break

        if curr in visited:
            continue
        visited.add(curr)

        for neighbor in sorted(G.neighbors(curr)):
            if neighbor in visited:
                continue
            link = topology.get_link(curr, neighbor)
            link_cost = link.latency if (use_latency and link) else 1.0
            new_cost = cost + link_cost

            if neighbor not in best_cost or new_cost < best_cost[neighbor] - 1e-9:
                best_cost[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, hops + 1, path + [neighbor]))
            elif abs(new_cost - best_cost[neighbor]) <= 1e-9:
                heapq.heappush(heap, (new_cost, hops + 1, path + [neighbor]))

    if target_path is not None:
        metrics = topology.get_path_metrics(target_path)
        return {
            "path": target_path,
            "hop_count": metrics["hop_count"],
            "latency": metrics["latency"],
            "status": "success",
            "message": f"Dijkstra computed shortest route via '{metric}' metric",
            "algorithm": "dijkstra",
        }

    return {
        "path": [],
        "hop_count": 0,
        "latency": 0.0,
        "status": "no_route",
        "message": f"No active path found between '{source}' and '{destination}'",
        "algorithm": "dijkstra",
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
        metric: 'hop'/'hops' or 'latency'.

    Returns:
        Dictionary mapping destination node ID -> path list.

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/why_shortest_is_not_best.json")
        >>> paths = compute_all_shortest_paths_from_source(topo, "PC1", metric="latency")
        >>> "PC2" in paths
        True
    """
    if source not in topology.nodes or not topology.nodes[source].active:
        return {}

    G = topology.to_networkx(only_active=True)
    if source not in G:
        return {}

    paths: Dict[str, List[str]] = {}
    for target in sorted(G.nodes()):
        res = link_state_dijkstra(topology, source, target, metric=metric)
        if res["status"] == "success":
            paths[target] = res["path"]

    return paths
