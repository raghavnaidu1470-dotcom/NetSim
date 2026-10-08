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
    """Forwarding table for a specific network router or host."""

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
        """Mark all entries that route via the failed node as inactive.

        Returns count of invalidated entries.
        """
        count = 0
        for entry in self.entries.values():
            if entry.next_hop_id == failed_node_id:
                entry.status = "unreachable"
                count += 1
        return count

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
) -> RoutingTable:
    """Generate a full routing table for the specified node using the active topology.

    Args:
        topology: Active Topology instance.
        node_id: Identifier of the node to generate the table for.
        algorithm: 'dijkstra' | 'distance_vector' | 'xar'.

    Returns:
        RoutingTable instance populated with entries to all active destinations.
    """
    table = RoutingTable(node_id=node_id)
    if node_id not in topology.nodes or not topology.nodes[node_id].active:
        return table

    for dest_id, dest_node in topology.nodes.items():
        if dest_id == node_id or not dest_node.active:
            continue

        route_res = topology.find_route(source=node_id, destination=dest_id, algorithm=algorithm)
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
                    metric=route_res["latency"],
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
