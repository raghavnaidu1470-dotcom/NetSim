"""Routing table representation and generation for network routers.

Provides structures and generators to compute forwarding tables for nodes in the
topology based on Link State or Distance Vector routing results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from network.topology import Topology


@dataclass
class RoutingTableEntry:
    """A single routing table forwarding entry."""
    destination_id: str
    destination_ip: str
    next_hop_id: Optional[str]
    next_hop_ip: Optional[str]
    metric: float
    hop_count: int
    status: str = "active"


class RoutingTable:
    """Forwarding table for a specific network router or host.

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/why_shortest_is_not_best.json")
        >>> table = build_routing_table(topo, "R1")
        >>> table.get_next_hop("PC2")
        'R2'
    """

    def __init__(self, node_id: str) -> None:
        self.node_id: str = node_id
        self.entries: Dict[str, RoutingTableEntry] = {}

    def add_or_update_entry(self, entry: RoutingTableEntry) -> None:
        self.entries[entry.destination_id] = entry

    def get_next_hop(self, destination_id: str) -> Optional[str]:
        entry = self.entries.get(destination_id)
        if entry and entry.status == "active":
            return entry.next_hop_id
        return None

    def invalidate_routes_via_node(self, failed_node_id: str) -> int:
        """Mark all entries that route via the failed node as unreachable.

        Args:
            failed_node_id: Node ID that suffered failure.

        Returns:
            Count of invalidated entries.

        Example:
            >>> table = RoutingTable("R1")
            >>> table.add_or_update_entry(RoutingTableEntry("PC2", "10.0.0.2", "R2", "10.0.0.1", 10.0, 2))
            >>> table.invalidate_routes_via_node("R2")
            1
        """
        count = 0
        for entry in self.entries.values():
            if entry.next_hop_id == failed_node_id:
                entry.status = "unreachable"
                count += 1
        return count

    def invalidate_routes_via_link(self, u: str, v: str) -> int:
        """Mark all entries traversing the severed link (u, v) as unreachable.

        Args:
            u: One endpoint of the severed link.
            v: Other endpoint of the severed link.

        Returns:
            Count of invalidated entries.

        Example:
            >>> table = RoutingTable("R1")
            >>> table.add_or_update_entry(RoutingTableEntry("PC2", "10.0.0.2", "R2", "10.0.0.1", 10.0, 2))
            >>> table.invalidate_routes_via_link("R1", "R2")
            1
        """
        count = 0
        target_next_hop = v if self.node_id == u else (u if self.node_id == v else None)
        for entry in self.entries.values():
            if target_next_hop is not None and entry.next_hop_id == target_next_hop:
                entry.status = "unreachable"
                count += 1
            elif entry.next_hop_id in (u, v) and self.node_id in (u, v):
                entry.status = "unreachable"
                count += 1
        return count

    def pretty_print(self) -> str:
        """Render a formatted ASCII table of all forwarding entries.

        Returns:
            Multi-line string representation of the routing table.

        Example:
            >>> table = RoutingTable("R1")
            >>> table.add_or_update_entry(RoutingTableEntry("PC1", "10.0.1.2", "Direct", None, 2.0, 1))
            >>> "Routing Table for Node: R1" in table.pretty_print()
            True
        """
        header = f"Routing Table for Node: {self.node_id}"
        cols = [
            ("Destination ID", 16),
            ("Destination IP", 17),
            ("Next Hop ID", 13),
            ("Next Hop IP", 16),
            ("Metric", 10),
            ("Hops", 6),
            ("Status", 12),
        ]
        sep = "+" + "+".join("-" * (w + 2) for _, w in cols) + "+"
        head_row = "|" + "|".join(f" {name.ljust(w)} " for name, w in cols) + "|"

        lines = [header, sep, head_row, sep]
        for dest_id in sorted(self.entries.keys()):
            e = self.entries[dest_id]
            next_hop = e.next_hop_id or "Direct"
            next_ip = e.next_hop_ip or "-"
            metric_str = f"{e.metric:.2f}" if e.metric != float("inf") else "inf"
            row = (
                f"| {e.destination_id.ljust(16)} "
                f"| {e.destination_ip.ljust(17)} "
                f"| {next_hop.ljust(13)} "
                f"| {next_ip.ljust(16)} "
                f"| {metric_str.rjust(10)} "
                f"| {str(e.hop_count).rjust(6)} "
                f"| {e.status.ljust(12)} |"
            )
            lines.append(row)
        lines.append(sep)
        return "\n".join(lines)

    def to_dict(self) -> List[Dict[str, object]]:
        return [
            {
                "destination_id": e.destination_id,
                "destination_ip": e.destination_ip,
                "next_hop_id": e.next_hop_id or "Direct",
                "next_hop_ip": e.next_hop_ip or "-",
                "metric": e.metric,
                "hop_count": e.hop_count,
                "status": e.status,
            }
            for e in self.entries.values()
        ]


def build_routing_table(
    topology: Topology,
    node_id: str,
    algorithm: str = "dijkstra",
    metric: str = "hop",
) -> RoutingTable:
    """Generate a full routing table for the specified node using the active topology.

    Args:
        topology: Active Topology instance.
        node_id: Identifier of the node to generate the table for.
        algorithm: 'dijkstra', 'distance_vector', or 'xar'.
        metric: Minimization metric ('hop' or 'latency').

    Returns:
        RoutingTable instance populated with entries to all active destinations.

    Example:
        >>> from network.topology import Topology
        >>> topo = Topology.load_json("data/topologies/why_shortest_is_not_best.json")
        >>> table = build_routing_table(topo, "R1", algorithm="dijkstra")
        >>> table.entries["PC2"].hop_count
        4
    """
    table = RoutingTable(node_id=node_id)
    if node_id not in topology.nodes or not topology.nodes[node_id].active:
        return table

    for dest_id, dest_node in sorted(topology.nodes.items()):
        if dest_id == node_id or not dest_node.active:
            continue

        route_res = topology.find_route(source=node_id, destination=dest_id, algorithm=algorithm, metric=metric)
        if route_res["status"] == "success" and len(route_res["path"]) >= 2:
            next_hop_id = route_res["path"][1]
            next_hop_node = topology.get_node(next_hop_id)
            next_hop_ip = next_hop_node.ip if next_hop_node else None

            table.add_or_update_entry(
                RoutingTableEntry(
                    destination_id=dest_id,
                    destination_ip=dest_node.ip,
                    next_hop_id=next_hop_id,
                    next_hop_ip=next_hop_ip,
                    metric=route_res["latency"] if metric == "latency" else float(route_res["hop_count"]),
                    hop_count=route_res["hop_count"],
                    status="active",
                )
            )
        else:
            table.add_or_update_entry(
                RoutingTableEntry(
                    destination_id=dest_id,
                    destination_ip=dest_node.ip,
                    next_hop_id=None,
                    next_hop_ip=None,
                    metric=float("inf"),
                    hop_count=0,
                    status="unreachable",
                )
            )

    return table
