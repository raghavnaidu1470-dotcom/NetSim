"""Distance Vector Routing (Bellman-Ford simulation) for NetSim-X.

Simulates iterative, distributed round-by-round Distance Vector protocol exchanges
with convergence round tracking, next-hop pointer resolution, and route reconstruction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypedDict

from network.devices import RouteResult

if TYPE_CHECKING:
    from network.topology import Topology

INFINITY = float("inf")


class DVEntry(TypedDict):
    """Entry in a node's distance vector table."""
    cost: float
    next_hop: Optional[str]


class DVConvergenceResult(TypedDict):
    """Output of iterative round-by-round Distance Vector simulation."""
    route: RouteResult
    convergence_rounds: int
    converged: bool
    tables: Dict[str, Dict[str, DVEntry]]


def simulate_distance_vector_convergence(
    topology: Topology,
    metric: str = "hop",
    max_rounds: int = 50,
) -> Tuple[Dict[str, Dict[str, DVEntry]], int, bool]:
    """Execute round-by-round Distance Vector exchange across all active nodes until convergence.

    Bellman-Ford equation: D_x(y) = min_v { c(x, v) + D_v(y) }

    Args:
        topology: Active Topology instance.
        metric: 'hop' (cost 1 per edge) or 'latency'.
        max_rounds: Maximum iterations before breaking (prevents count-to-infinity loop).

    Returns:
        (tables, convergence_rounds, converged_flag)
    """
    G = topology.to_networkx(only_active=True)
    active_nodes = sorted(list(G.nodes()))

    if not active_nodes:
        return {}, 0, True

    # Initialize distance vector tables
    # tables[node][dest] = {"cost": ..., "next_hop": ...}
    tables: Dict[str, Dict[str, DVEntry]] = {}
    for u in active_nodes:
        tables[u] = {}
        for v in active_nodes:
            if u == v:
                tables[u][v] = {"cost": 0.0, "next_hop": u}
            else:
                tables[u][v] = {"cost": INFINITY, "next_hop": None}

    # Populate direct neighbor link costs
    for u in active_nodes:
        for v in G.neighbors(u):
            link = topology.get_link(u, v)
            cost = link.latency if (metric == "latency" and link) else 1.0
            tables[u][v] = {"cost": cost, "next_hop": v}

    converged = False
    rounds = 0

    while rounds < max_rounds:
        rounds += 1
        any_change = False

        # In a round, nodes evaluate updates based on distance vectors from neighbors
        new_tables: Dict[str, Dict[str, DVEntry]] = {
            u: {dest: dict(entry) for dest, entry in tables[u].items()}  # type: ignore
            for u in active_nodes
        }

        for u in active_nodes:
            neighbors = list(G.neighbors(u))
            for dest in active_nodes:
                if u == dest:
                    continue

                best_cost = tables[u][dest]["cost"]
                best_next_hop = tables[u][dest]["next_hop"]

                for v in neighbors:
                    link = topology.get_link(u, v)
                    link_cost = link.latency if (metric == "latency" and link) else 1.0

                    neighbor_cost_to_dest = tables[v][dest]["cost"]
                    if neighbor_cost_to_dest < INFINITY:
                        cand_cost = link_cost + neighbor_cost_to_dest
                        if cand_cost < best_cost - 1e-9:
                            best_cost = cand_cost
                            best_next_hop = v

                if abs(best_cost - tables[u][dest]["cost"]) > 1e-9 or best_next_hop != tables[u][dest]["next_hop"]:
                    new_tables[u][dest] = {"cost": best_cost, "next_hop": best_next_hop}
                    any_change = True

        tables = new_tables

        if not any_change:
            converged = True
            break

    return tables, rounds, converged


def distance_vector_routing(
    topology: Topology,
    source: str,
    destination: str,
    metric: str = "hop",
    max_rounds: int = 50,
) -> DVConvergenceResult:
    """Find a route between source and destination using Distance Vector simulation.

    Args:
        topology: Active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        metric: Cost metric ('hop' or 'latency').
        max_rounds: Round limit.

    Returns:
        DVConvergenceResult with route and convergence metadata.
    """
    if source not in topology.nodes or destination not in topology.nodes:
        return {
            "route": {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "invalid",
            },
            "convergence_rounds": 0,
            "converged": False,
            "tables": {},
        }

    if not topology.nodes[source].active or not topology.nodes[destination].active:
        return {
            "route": {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "no_route",
            },
            "convergence_rounds": 0,
            "converged": False,
            "tables": {},
        }

    if source == destination:
        return {
            "route": {
                "path": [source],
                "hop_count": 0,
                "latency": 0.0,
                "status": "success",
            },
            "convergence_rounds": 0,
            "converged": True,
            "tables": {source: {source: {"cost": 0.0, "next_hop": source}}},
        }

    tables, rounds, converged = simulate_distance_vector_convergence(
        topology, metric=metric, max_rounds=max_rounds
    )

    # Reconstruct path by traversing next_hop pointers
    path = [source]
    curr = source
    visited = {source}

    while curr != destination:
        if curr not in tables or destination not in tables[curr]:
            path = []
            break
        next_hop = tables[curr][destination]["next_hop"]
        if not next_hop or next_hop in visited or tables[curr][destination]["cost"] >= INFINITY:
            path = []
            break
        path.append(next_hop)
        visited.add(next_hop)
        curr = next_hop

    if path and path[-1] == destination:
        metrics = topology.get_path_metrics(path)
        route_res: RouteResult = {
            "path": path,
            "hop_count": metrics["hop_count"],
            "latency": metrics["latency"],
            "status": "success",
        }
    else:
        route_res = {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
        }

    return {
        "route": route_res,
        "convergence_rounds": rounds,
        "converged": converged,
        "tables": tables,
    }
