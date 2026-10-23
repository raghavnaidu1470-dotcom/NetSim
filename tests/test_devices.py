"""Unit tests for network devices, schemas, and IPv4 validation (Member 1 - Ragghav Kamaraj)."""

import pytest

from network.devices import Link, Node, validate_ipv4


def test_validate_ipv4_valid() -> None:
    assert validate_ipv4("192.168.1.1") is True
    assert validate_ipv4("10.0.0.1") is True
    assert validate_ipv4("172.16.254.1") is True
    assert validate_ipv4("127.0.0.1") is True


def test_validate_ipv4_invalid() -> None:
    assert validate_ipv4("999.999.999.999") is False
    assert validate_ipv4("192.168.1") is False
    assert validate_ipv4("abc.def.ghi.jkl") is False
    assert validate_ipv4("") is False
    assert validate_ipv4("256.100.0.1") is False


def test_node_creation_and_dict() -> None:
    node = Node(id="R1", ip="192.168.1.1", type="router", active=True)
    assert node.id == "R1"
    assert node.ip == "192.168.1.1"
    assert node.type == "router"
    assert node.active is True

    d = node.to_dict()
    assert d == {"id": "R1", "ip": "192.168.1.1", "type": "router", "active": True}

    reconstructed = Node.from_dict(d)
    assert reconstructed.id == node.id
    assert reconstructed.ip == node.ip


def test_node_invalid_ip_raises() -> None:
    with pytest.raises(ValueError, match="Invalid IPv4 address"):
        Node(id="R1", ip="999.1.1.1")


def test_node_invalid_type_raises() -> None:
    with pytest.raises(ValueError, match="Invalid node type"):
        Node(id="R1", ip="10.0.0.1", type="switch")  # type: ignore


def test_link_creation_and_dict() -> None:
    link = Link(
        source="R1",
        destination="R2",
        latency=15.5,
        bandwidth=100.0,
        congestion=0.25,
        packet_loss=0.01,
        reliability=0.99,
        active=True,
    )
    assert link.source == "R1"
    assert link.destination == "R2"
    assert link.latency == 15.5

    d = link.to_dict()
    assert d["source"] == "R1"
    assert d["destination"] == "R2"
    assert d["latency"] == 15.5

    reconstructed = Link.from_dict(d)
    assert reconstructed.source == link.source
    assert reconstructed.latency == link.latency


def test_link_validation_bounds() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        Link(source="R1", destination="R2", latency=-5.0)

    with pytest.raises(ValueError, match="must be positive"):
        Link(source="R1", destination="R2", bandwidth=0.0)

    with pytest.raises(ValueError, match="within \\[0.0, 1.0\\]"):
        Link(source="R1", destination="R2", congestion=1.5)

    with pytest.raises(ValueError, match="Self-loop"):
        Link(source="R1", destination="R1")
