"""Network topology management, graph construction, and path enumeration.

Provides the Topology class representing network devices and links, graph conversion
to NetworkX, failure toggles, and unified route finding.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

from network.devices import Link, LinkDict, Node, NodeDict, RouteResult, validate_ipv4


class Topology:
    """In-memory network topology representing routers, hosts, and communication links.

    Attributes:
        name: Name of the topology.
        description: Description of the topology scenario.
        nodes: Dictionary of node_id -> Node.
        links: List of Link objects.
    """

    def __init__(self, name: str = "custom", description: str = "") -> None:
        self.name: str = name
        self.description: str = description
        self.nodes: Dict[str, Node] = {}
        self.links: List[Link] = []

    def add_node(self, node: Node) -> None:
        """Add a validated Node to the topology."""
        if not isinstance(node, Node):
            raise TypeError("node must be an instance of Node")
        self.nodes[node.id] = node

    def add_link(self, link: Link) -> None:
        """Add a validated Link between existing nodes to the topology."""
        if not isinstance(link, Link):
            raise TypeError("link must be an instance of Link")
        if link.source not in self.nodes:
            raise ValueError(f"Link source '{link.source}' does not exist in topology")
        if link.destination not in self.nodes:
            raise ValueError(f"Link destination '{link.destination}' does not exist in topology")
        self.links.append(link)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by its identifier."""
        return self.nodes.get(node_id)

    def get_link(self, u: str, v: str) -> Optional[Link]:
        """Retrieve the link between nodes u and v (bidirectional)."""
        for link in self.links:
            if (link.source == u and link.destination == v) or (
                link.source == v and link.destination == u
            ):
                return link
        return None

    def set_node_active(self, node_id: str, active: bool) -> bool:
        """Toggle active status of a node.

        Returns:
            True if node exists and was updated, False otherwise.
        """
        if node_id in self.nodes:
            self.nodes[node_id].active = active
            return True
        return False

    def set_link_active(self, u: str, v: str, active: bool) -> bool:
        """Toggle active status of a link between u and v."""
        link = self.get_link(u, v)
        if link:
            link.active = active
            return True
        return False

    def update_link_metrics(
        self,
        u: str,
        v: str,
        latency: Optional[float] = None,
        congestion: Optional[float] = None,
        packet_loss: Optional[float] = None,
        reliability: Optional[float] = None,
        bandwidth: Optional[float] = None,
    ) -> bool:
        """Update runtime metrics on an existing link."""
        link = self.get_link(u, v)
        if not link:
            return False
        if latency is not None:
            if latency < 0:
                raise ValueError("Latency cannot be negative")
            link.latency = float(latency)
        if congestion is not None:
            if not (0.0 <= congestion <= 1.0):
                raise ValueError("Congestion must be within [0.0, 1.0]")
            link.congestion = float(congestion)
        if packet_loss is not None:
            if not (0.0 <= packet_loss <= 1.0):
                raise ValueError("Packet loss must be within [0.0, 1.0]")
            link.packet_loss = float(packet_loss)
        if reliability is not None:
            if not (0.0 <= reliability <= 1.0):
                raise ValueError("Reliability must be within [0.0, 1.0]")
            link.reliability = float(reliability)
        if bandwidth is not None:
            if bandwidth <= 0:
                raise ValueError("Bandwidth must be positive")
            link.bandwidth = float(bandwidth)
        return True

    def to_networkx(self, only_active: bool = True) -> nx.Graph:
        """Construct a NetworkX Graph representing the topology.

        Args:
            only_active: If True, only include active nodes and active links.
                         If False, include all nodes/links with 'active' attributes.

        Returns:
            nx.Graph with nodes and link attributes attached.
        """
        G = nx.Graph()

        for node_id, node in self.nodes.items():
            if only_active and not node.active:
                continue
            G.add_node(
                node_id,
                ip=node.ip,
                type=node.type,
                active=node.active,
            )

        for link in self.links:
            if only_active:
                if not link.active:
                    continue
                if link.source not in G or link.destination not in G:
                    continue

            G.add_edge(
                link.source,
                link.destination,
                latency=link.latency,
                bandwidth=link.bandwidth,
                congestion=link.congestion,
                packet_loss=link.packet_loss,
                reliability=link.reliability,
                active=link.active,
                weight=1.0,  # Default hop-based weight for standard unweighted Dijkstra
            )

        return G

    def enumerate_paths(
        self, source: str, destination: str, max_hops: int = 8
    ) -> List[List[str]]:
        """Enumerate all simple active paths between source and destination up to max_hops.

        Args:
            source: Source node ID.
            destination: Destination node ID.
            max_hops: Maximum number of hops (edges) allowed along the path.

        Returns:
            List of node ID sequences representing valid paths.
        """
        if source not in self.nodes or destination not in self.nodes:
            return []
        if not self.nodes[source].active or not self.nodes[destination].active:
            return []
        if source == destination:
            return [[source]]

        G = self.to_networkx(only_active=True)
        if source not in G or destination not in G:
            return []

        try:
            paths = list(
                nx.all_simple_paths(
                    G, source=source, target=destination, cutoff=max_hops
                )
            )
            return paths
        except nx.NetworkXNoPath:
            return []

    def get_path_metrics(self, path: List[str]) -> Dict[str, float]:
        """Aggregate link metrics along a given path.

        Rules:
        - Latency = Sum of link latencies
        - Packet Loss = 1 - product(1 - p_link)
        - Reliability = Product of link reliabilities
        - Congestion = Max of link congestions (bottleneck)
        - Hop count = Number of links (len(path) - 1)
        """
        if not path or len(path) <= 1:
            return {
                "latency": 0.0,
                "packet_loss": 0.0,
                "reliability": 1.0,
                "congestion": 0.0,
                "hop_count": 0,
            }

        total_latency = 0.0
        success_prob = 1.0
        reliability_prod = 1.0
        congestions: List[float] = []

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            link = self.get_link(u, v)
            if link is None:
                raise ValueError(f"No link found between {u} and {v}")
            total_latency += link.latency
            success_prob *= 1.0 - link.packet_loss
            reliability_prod *= link.reliability
            congestions.append(link.congestion)

        aggregated_loss = 1.0 - success_prob
        max_congestion = max(congestions) if congestions else 0.0

        return {
            "latency": round(total_latency, 2),
            "packet_loss": round(aggregated_loss, 4),
            "reliability": round(reliability_prod, 4),
            "congestion": round(max_congestion, 4),
            "hop_count": len(path) - 1,
        }

    def find_route(
        self, source: str, destination: str, algorithm: str = "dijkstra"
    ) -> RouteResult:
        """Find a route between source and destination using the specified algorithm.

        Args:
            source: Source node ID.
            destination: Destination node ID.
            algorithm: 'dijkstra', 'link_state', 'distance_vector', or 'xar'.

        Returns:
            RouteResult: {'path': [...], 'hop_count': int, 'latency': float, 'status': 'success'|'no_route'|'invalid'}
        """
        # Validate node existence
        if source not in self.nodes or destination not in self.nodes:
            return {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "invalid",
            }

        # Check active status
        if not self.nodes[source].active or not self.nodes[destination].active:
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

        algo = algorithm.lower().strip()

        if algo in ("dijkstra", "link_state"):
            from network.link_state import link_state_dijkstra

            return link_state_dijkstra(self, source, destination)

        elif algo in ("distance_vector", "dv"):
            from network.distance_vector import distance_vector_routing

            dv_result = distance_vector_routing(self, source, destination)
            return dv_result["route"]

        elif algo == "xar":
            try:
                from adaptive.xar import xar_find_route

                return xar_find_route(self, source, destination)
            except (ImportError, NotImplementedError):
                # Fallback to link state if XAR not yet implemented
                from network.link_state import link_state_dijkstra

                return link_state_dijkstra(self, source, destination)

        else:
            return {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "invalid",
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Topology:
        """Build Topology instance from a parsed dictionary."""
        name = data.get("name", "custom")
        desc = data.get("description", "")
        topo = cls(name=name, description=desc)

        for n_data in data.get("nodes", []):
            node = Node.from_dict(n_data)
            topo.add_node(node)

        for l_data in data.get("links", []):
            link = Link.from_dict(l_data)
            topo.add_link(link)

        return topo

    @classmethod
    def load_json(cls, file_path: Union[str, Path]) -> Topology:
        """Load Topology instance from a JSON file."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Topology file not found: {file_path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Topology to a serializable dictionary matching the schema."""
        return {
            "name": self.name,
            "description": self.description,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "links": [link.to_dict() for link in self.links],
        }
