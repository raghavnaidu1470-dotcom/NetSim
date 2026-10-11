"""Distance Vector Routing (Bellman-Ford simulation) for NetSim-X.

Simulates iterative, distributed round-by-round Distance Vector protocol exchanges
with convergence round tracking, per-round logging, next-hop pointer resolution,
configurable infinity (default 16 for count-to-infinity modeling), and failure reconvergence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypedDict, Union

from network.devices import RouteResult

if TYPE_CHECKING:
    from network.topology import Topology

DEFAULT_INFINITY: float = 16.0
INFINITY: float = float("inf")


class DVEntry(TypedDict):
    """Entry in a node's distance vector table."""
    cost: float
    next_hop: Optional[str]


class DVConvergenceResult(TypedDict, total=False):
    """Output of iterative round-by-round Distance Vector simulation."""
    route: RouteResult
    convergence_rounds: int
    converged: bool
    tables: Dict[str, Dict[str, DVEntry]]
    round_log: List[Dict[str, Any]]
    infinity: float


def simulate_distance_vector_convergence(
    topology: Topology,
    metric: str = "hop",
    max_rounds: int = 50,
    infinity: Optional[float] = None,
    initial_tables: Optional[Dict[str, Dict[str, DVEntry]]] = None,
    return_log: bool = False,
) -> Union[
    Tuple[Dict[str, Dict[str, DVEntry]], int, bool],
    Tuple[Dict[str, Dict[str, DVEntry]], int, bool, List[Dict[str, Any]]],
]:
    """Execute round-by-round Distance Vector exchange across all active nodes until convergence.

    Bellman-Ford equation: D_x(y) = min_v { c(x, v) + D_v(y) }

    Args:
        topology: Active Topology instance.
        metric: 'hop'/'hops' (cost 1 per edge) or 'latency'.
        max_rounds: Maximum iterations before breaking (prevents count-to-infinity loop).
        infinity: Metric infinity threshold (default 16.0 for hop count, inf for latency). Costs >= infinity are treated as unreachable.
        initial_tables: Optional seed tables (e.g. for simulating reconvergence after failure).
        return_log: If True, returns 4-tuple including round_log. If False, returns 3-tuple (tables, rounds, converged).

    Returns:
        If return_log is False: (tables, convergence_rounds, converged_flag)
        If return_log is True: (tables, convergence_rounds, converged_flag, round_log)

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/why_shortest_is_not_best.json")
        >>> tables, rounds, converged = simulate_distance_vector_convergence(topo, metric="hops")
        >>> converged
        True
    """
    normalized_metric = metric.lower().strip()
    use_latency = normalized_metric == "latency"
    effective_infinity = (
        float(infinity)
        if infinity is not None
        else (float("inf") if use_latency else DEFAULT_INFINITY)
    )

    G = topology.to_networkx(only_active=True)
    active_nodes = sorted(list(G.nodes()))

    if not active_nodes:
        if return_log:
            return {}, 0, True, []
        return {}, 0, True

    # Initialize distance vector tables
    if initial_tables is not None:
        tables: Dict[str, Dict[str, DVEntry]] = {
            u: {dest: dict(entry) for dest, entry in initial_tables.get(u, {}).items()}  # type: ignore
            for u in active_nodes
        }
        for u in active_nodes:
            if u not in tables:
                tables[u] = {}
            for v in active_nodes:
                if v not in tables[u]:
                    tables[u][v] = {"cost": 0.0 if u == v else effective_infinity, "next_hop": u if u == v else None}
    else:
        tables = {}
        for u in active_nodes:
            tables[u] = {}
            for v in active_nodes:
                if u == v:
                    tables[u][v] = {"cost": 0.0, "next_hop": u}
                else:
                    tables[u][v] = {"cost": effective_infinity, "next_hop": None}

        # Populate direct neighbor link costs
        for u in active_nodes:
            for v in sorted(G.neighbors(u)):
                link = topology.get_link(u, v)
                cost = link.latency if (use_latency and link) else 1.0
                if cost < effective_infinity:
                    tables[u][v] = {"cost": cost, "next_hop": v}

    converged = False
    rounds = 0
    round_log: List[Dict[str, Any]] = []

    while rounds < max_rounds:
        rounds += 1
        any_change = False
        updates_in_round: List[str] = []

        new_tables: Dict[str, Dict[str, DVEntry]] = {
            u: {dest: dict(entry) for dest, entry in tables[u].items()}  # type: ignore
            for u in active_nodes
        }

        for u in active_nodes:
            neighbors = sorted(list(G.neighbors(u)))
            for dest in active_nodes:
                if u == dest:
                    continue

                best_cost = tables[u][dest]["cost"]
                best_next_hop = tables[u][dest]["next_hop"]

                for v in neighbors:
                    link = topology.get_link(u, v)
                    link_cost = link.latency if (use_latency and link) else 1.0

                    neighbor_cost_to_dest = tables[v][dest]["cost"]
                    if neighbor_cost_to_dest < effective_infinity - 1e-9:
                        cand_cost = link_cost + neighbor_cost_to_dest
                        if cand_cost >= effective_infinity:
                            cand_cost = effective_infinity

                        # Deterministic tie-break: lower cost wins; on tie, keep existing or pick lower neighbor ID
                        if cand_cost < best_cost - 1e-9:
                            best_cost = cand_cost
                            best_next_hop = v
                        elif abs(cand_cost - best_cost) <= 1e-9 and best_next_hop is not None and v < best_next_hop:
                            best_next_hop = v

                if best_cost >= effective_infinity:
                    best_cost = effective_infinity
                    best_next_hop = None

                if abs(best_cost - tables[u][dest]["cost"]) > 1e-9 or best_next_hop != tables[u][dest]["next_hop"]:
                    new_tables[u][dest] = {"cost": best_cost, "next_hop": best_next_hop}
                    any_change = True
                    updates_in_round.append(f"{u}->{dest}: cost {tables[u][dest]['cost']}->{best_cost} via {best_next_hop}")

        tables = new_tables

        round_log.append({
            "round": rounds,
            "updates_count": len(updates_in_round),
            "updates": updates_in_round,
            "tables_snapshot": {
                u: {d: dict(e) for d, e in tables[u].items()}
                for u in active_nodes
            },
        })

        if not any_change:
            converged = True
            break

    if return_log:
        return tables, rounds, converged, round_log
    return tables, rounds, converged


def simulate_distance_vector_reconvergence(
    topology: Topology,
    failed_node: Optional[str] = None,
    failed_link: Optional[Tuple[str, str]] = None,
    metric: str = "hop",
    max_rounds: int = 50,
    infinity: Optional[float] = None,
) -> Dict[str, Any]:
    """Simulate initial convergence, apply a component failure, and track reconvergence rounds.

    Args:
        topology: Active Topology instance.
        failed_node: Node ID to deactivate.
        failed_link: (source, destination) link pair to deactivate.
        metric: 'hop' or 'latency'.
        max_rounds: Round cap.
        infinity: Count-to-infinity threshold.

    Returns:
        Dictionary with initial and post-failure convergence metrics, rounds, and logs.

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/router_failure.json")
        >>> res = simulate_distance_vector_reconvergence(topo, failed_node="R2")
        >>> res["reconvergence_converged"]
        True
    """
    init_res = simulate_distance_vector_convergence(
        topology, metric=metric, max_rounds=max_rounds, infinity=infinity, return_log=True
    )
    initial_tables, init_rounds, init_converged, init_log = init_res  # type: ignore

    # Apply failure
    if failed_node:
        topology.set_node_active(failed_node, False)
    if failed_link:
        topology.set_link_active(failed_link[0], failed_link[1], False)

    reconv_res = simulate_distance_vector_convergence(
        topology, metric=metric, max_rounds=max_rounds, infinity=infinity, return_log=True
    )
    post_tables, reconv_rounds, reconv_converged, reconv_log = reconv_res  # type: ignore

    return {
        "initial_rounds": init_rounds,
        "initial_converged": init_converged,
        "reconvergence_rounds": reconv_rounds,
        "reconvergence_converged": reconv_converged,
        "tables": post_tables,
        "reconvergence_log": reconv_log,
        "failed_node": failed_node,
        "failed_link": failed_link,
    }


def distance_vector_routing(
    topology: Topology,
    source: str,
    destination: str,
    metric: str = "hop",
    max_rounds: int = 50,
    infinity: Optional[float] = None,
) -> DVConvergenceResult:
    """Find a route between source and destination using Distance Vector simulation.

    Args:
        topology: Active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        metric: Cost metric ('hop'/'hops' or 'latency').
        max_rounds: Round limit.
        infinity: Distance vector infinity cutoff (default 16.0 for hops, inf for latency).

    Returns:
        DVConvergenceResult with route and convergence metadata.

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/why_shortest_is_not_best.json")
        >>> res = distance_vector_routing(topo, "PC1", "PC2", metric="hops")
        >>> res["route"]["status"]
        'success'
    """
    normalized_metric = metric.lower().strip()
    use_latency = normalized_metric == "latency"
    effective_infinity = (
        float(infinity)
        if infinity is not None
        else (float("inf") if use_latency else DEFAULT_INFINITY)
    )

    if source not in topology.nodes or destination not in topology.nodes:
        missing = [n for n in (source, destination) if n not in topology.nodes]
        return {
            "route": {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "invalid",
                "message": f"Node does not exist in topology: {', '.join(missing)}",
                "algorithm": "distance_vector",
            },
            "convergence_rounds": 0,
            "converged": False,
            "tables": {},
            "round_log": [],
            "infinity": effective_infinity,
        }

    if not topology.nodes[source].active or not topology.nodes[destination].active:
        inactive = [n for n in (source, destination) if not topology.nodes[n].active]
        return {
            "route": {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "no_route",
                "message": f"Node is inactive/down: {', '.join(inactive)}",
                "algorithm": "distance_vector",
            },
            "convergence_rounds": 0,
            "converged": False,
            "tables": {},
            "round_log": [],
            "infinity": effective_infinity,
        }

    if source == destination:
        return {
            "route": {
                "path": [source],
                "hop_count": 0,
                "latency": 0.0,
                "status": "success",
                "message": "Source and destination are identical",
                "algorithm": "distance_vector",
            },
            "convergence_rounds": 0,
            "converged": True,
            "tables": {source: {source: {"cost": 0.0, "next_hop": source}}},
            "round_log": [],
            "infinity": effective_infinity,
        }

    sim_res = simulate_distance_vector_convergence(
        topology, metric=metric, max_rounds=max_rounds, infinity=effective_infinity, return_log=True
    )
    tables, rounds, converged, round_log = sim_res  # type: ignore

    # Reconstruct path by traversing next_hop pointers
    path = [source]
    curr = source
    visited = {source}

    while curr != destination:
        if curr not in tables or destination not in tables[curr]:
            path = []
            break
        next_hop = tables[curr][destination]["next_hop"]
        if not next_hop or next_hop in visited or tables[curr][destination]["cost"] >= effective_infinity - 1e-9:
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
            "message": f"Distance Vector converged in {rounds} rounds",
            "algorithm": "distance_vector",
        }
    else:
        route_res = {
            "path": [],
            "hop_count": 0,
            "latency": 0.0,
            "status": "no_route",
            "message": f"Distance Vector found no route (cost >= infinity or disconnected)",
            "algorithm": "distance_vector",
        }

    return {
        "route": route_res,
        "convergence_rounds": rounds,
        "converged": converged,
        "tables": tables,
        "round_log": round_log,
        "infinity": effective_infinity,
    }
