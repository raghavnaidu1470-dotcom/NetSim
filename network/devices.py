"""Data schemas and device validation for NetSim-X network topologies.

Defines Node, Link, and RouteResult data models conforming to the shared schema,
along with IPv4 validation utilities.
"""

from __future__ import annotations

import ipaddress
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict

NodeType = Literal["router", "host"]
RouteStatus = Literal["success", "no_route", "invalid"]


def validate_ipv4(ip: str) -> bool:
    """Validate whether an IP string is a valid IPv4 address.

    Args:
        ip: String representation of an IPv4 address.

    Returns:
        True if valid IPv4, False otherwise.

    Example:
        >>> validate_ipv4("192.168.1.1")
        True
        >>> validate_ipv4("256.0.0.1")
        False
    """
    if not isinstance(ip, str) or not ip.strip():
        return False
    try:
        ipaddress.IPv4Address(ip.strip())
        return True
    except ValueError:
        return False


def validate_ipv4_address(ip: str) -> Tuple[bool, str]:
    """Validate whether an IP string is a valid IPv4 address with descriptive message.

    Args:
        ip: String representation of an IPv4 address.

    Returns:
        Tuple of (is_valid: bool, message: str).

    Example:
        >>> is_valid, msg = validate_ipv4_address("192.168.1.1")
        >>> is_valid
        True
        >>> is_valid, msg = validate_ipv4_address("invalid_ip")
        >>> is_valid
        False
    """
    if not isinstance(ip, str) or not ip.strip():
        return False, "IP address cannot be empty or non-string"
    try:
        addr = ipaddress.IPv4Address(ip.strip())
        return True, f"Valid IPv4 address: {addr}"
    except ValueError as exc:
        return False, f"Invalid IPv4 address '{ip}': {exc}"


class NodeDict(TypedDict):
    """Dictionary representation of a network Node."""
    id: str
    ip: str
    type: str  # 'router' | 'host'
    active: bool


class LinkDict(TypedDict):
    """Dictionary representation of a network Link."""
    source: str
    destination: str
    latency: float
    bandwidth: float
    congestion: float
    packet_loss: float
    reliability: float
    active: bool


class RouteResult(TypedDict, total=False):
    """Standard routing query return schema across all routing engines.

    Attributes:
        path: Ordered list of node identifiers.
        hop_count: Number of links traversed (len(path) - 1).
        latency: Aggregated path latency in milliseconds.
        status: Status flag ('success', 'no_route', 'invalid').
        message: Explanatory human-friendly status message.
        algorithm: Identifier of the routing algorithm used.
    """
    path: List[str]
    hop_count: int
    latency: float
    status: RouteStatus
    message: str
    algorithm: str


@dataclass
class Node:
    """Represents a network host or router.

    Attributes:
        id: Unique identifier (e.g. 'R1', 'PC1').
        ip: Valid IPv4 address string (e.g. '192.168.1.1').
        type: 'router' or 'host'.
        active: Operational status flag (True = active/up, False = down/failed).

    Example:
        >>> node = Node(id="R1", ip="192.168.1.1", type="router", active=True)
        >>> node.to_dict()["id"]
        'R1'
    """
    id: str
    ip: str
    type: NodeType = "router"
    active: bool = True

    def __post_init__(self) -> None:
        if not self.id or not isinstance(self.id, str):
            raise ValueError(f"Invalid node id: {self.id}")
        is_valid, msg = validate_ipv4_address(self.ip)
        if not is_valid:
            raise ValueError(f"Invalid IPv4 address '{self.ip}' for node '{self.id}': {msg}")
        if self.type not in ("router", "host"):
            raise ValueError(f"Invalid node type '{self.type}'. Must be 'router' or 'host'")

    def to_dict(self) -> NodeDict:
        return {
            "id": self.id,
            "ip": self.ip,
            "type": self.type,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Node:
        return cls(
            id=str(data["id"]),
            ip=str(data["ip"]),
            type=data.get("type", "router"),
            active=bool(data.get("active", True)),
        )


@dataclass
class Link:
    """Represents a bidirectional network link between two nodes.

    Attributes:
        source: Source node ID.
        destination: Destination node ID.
        latency: Link delay in milliseconds (ms), >= 0.
        bandwidth: Link throughput in Mbps, > 0.
        congestion: Fraction in [0.0, 1.0], 0 = idle, 1 = saturated.
        packet_loss: Probability of loss in [0.0, 1.0].
        reliability: Link operational reliability in [0.0, 1.0].
        active: Link operational state (True = up, False = severed/down).

    Example:
        >>> link = Link(source="R1", destination="R2", latency=10.0, bandwidth=100.0)
        >>> link.source
        'R1'
    """
    source: str
    destination: str
    latency: float = 10.0
    bandwidth: float = 100.0
    congestion: float = 0.0
    packet_loss: float = 0.0
    reliability: float = 1.0
    active: bool = True

    def __post_init__(self) -> None:
        if not self.source or not self.destination:
            raise ValueError(f"Link source and destination cannot be empty ({self.source} -> {self.destination})")
        if self.source == self.destination:
            raise ValueError(f"Self-loop link not allowed: {self.source}")
        if self.latency < 0:
            raise ValueError(f"Link latency cannot be negative: {self.latency}")
        if self.bandwidth <= 0:
            raise ValueError(f"Link bandwidth must be positive: {self.bandwidth}")
        if not (0.0 <= self.congestion <= 1.0):
            raise ValueError(f"Link congestion must be within [0.0, 1.0]: {self.congestion}")
        if not (0.0 <= self.packet_loss <= 1.0):
            raise ValueError(f"Link packet_loss must be within [0.0, 1.0]: {self.packet_loss}")
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError(f"Link reliability must be within [0.0, 1.0]: {self.reliability}")

    def to_dict(self) -> LinkDict:
        return {
            "source": self.source,
            "destination": self.destination,
            "latency": float(self.latency),
            "bandwidth": float(self.bandwidth),
            "congestion": float(self.congestion),
            "packet_loss": float(self.packet_loss),
            "reliability": float(self.reliability),
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Link:
        return cls(
            source=str(data["source"]),
            destination=str(data["destination"]),
            latency=float(data.get("latency", 10.0)),
            bandwidth=float(data.get("bandwidth", 100.0)),
            congestion=float(data.get("congestion", 0.0)),
            packet_loss=float(data.get("packet_loss", 0.0)),
            reliability=float(data.get("reliability", 1.0)),
            active=bool(data.get("active", True)),
        )
