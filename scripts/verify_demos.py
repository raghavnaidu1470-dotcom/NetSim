#!/usr/bin/env python3
"""NetSim Demo Scenario Verification Script (Member 1 - Ragghav Kamaraj).

Uses ONLY Member 1 code (`network/*`) to compute, verify, and print:
- All candidate paths via `enumerate_paths`
- Dijkstra with hop metric (`metric="hops"`)
- Dijkstra with latency metric (`metric="latency"`)
- Full path metrics: hops, latency, bottleneck congestion, packet loss, reliability
- Explicit per-link math for packet loss: 1 - product(1 - p_link)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure repo root is in python path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from network.link_state import link_state_dijkstra
from network.topology import Topology, enumerate_paths, get_path_metrics

TOPOLOGY_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"


def format_loss_math(topo: Topology, path: List[str]) -> str:
    """Compute and format the exact per-link calculation of 1 - product(1 - p_link).

    Args:
        topo: Active Topology instance.
        path: Ordered list of node identifiers.

    Returns:
        String detailing per-link loss factors and evaluation.
    """
    if len(path) <= 1:
        return "1 - 1.0 = 0.0% (0.0000)"

    link_factors: List[str] = []
    prod_terms: List[float] = []
    running_product = 1.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        link = topo.get_link(u, v)
        p = link.packet_loss if link else 0.0
        term = 1.0 - p
        link_factors.append(f"(1 - {p})")
        prod_terms.append(term)
        running_product *= term

    compound_loss = 1.0 - running_product
    factors_str = " * ".join(link_factors)
    return f"1 - [{factors_str}] = 1 - {running_product:.6f} = {compound_loss * 100:.2f}% ({compound_loss:.4f})"


def compute_demo_verifications() -> Dict[str, Any]:
    """Execute path enumeration and Dijkstra verification across all 3 demo topologies.

    Uses strictly Member 1 code (`network/*`).

    Returns:
        Structured dictionary of computed metrics for all scenarios.
    """
    results: Dict[str, Any] = {}

    # 1. why_shortest_is_not_best.json
    topo1 = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    paths1 = enumerate_paths(topo1, "PC1", "PC2", max_hops=8)
    dijk_hop_1 = link_state_dijkstra(topo1, "PC1", "PC2", metric="hops")
    dijk_lat_1 = link_state_dijkstra(topo1, "PC1", "PC2", metric="latency")

    results["why_shortest_is_not_best"] = {
        "topology_file": "why_shortest_is_not_best.json",
        "source": "PC1",
        "destination": "PC2",
        "paths": [
            {
                "path": p,
                "path_str": " -> ".join(p),
                "metrics": get_path_metrics(topo1, p),
                "loss_math": format_loss_math(topo1, p),
            }
            for p in paths1
        ],
        "dijkstra_hop": {
            "path": dijk_hop_1["path"],
            "path_str": " -> ".join(dijk_hop_1["path"]),
            "metrics": get_path_metrics(topo1, dijk_hop_1["path"]),
            "loss_math": format_loss_math(topo1, dijk_hop_1["path"]),
        },
        "dijkstra_latency": {
            "path": dijk_lat_1["path"],
            "path_str": " -> ".join(dijk_lat_1["path"]),
            "metrics": get_path_metrics(topo1, dijk_lat_1["path"]),
            "loss_math": format_loss_math(topo1, dijk_lat_1["path"]),
        },
    }

    # 2. router_failure.json
    topo2 = Topology.load_json(TOPOLOGY_DIR / "router_failure.json")
    paths2_pre = enumerate_paths(topo2, "PC1", "PC2", max_hops=8)
    dijk_hop_2_pre = link_state_dijkstra(topo2, "PC1", "PC2", metric="hops")
    dijk_lat_2_pre = link_state_dijkstra(topo2, "PC1", "PC2", metric="latency")

    # Simulate R2 failure
    topo2_post = Topology.load_json(TOPOLOGY_DIR / "router_failure.json")
    topo2_post.set_node_active("R2", False)
    paths2_post = enumerate_paths(topo2_post, "PC1", "PC2", max_hops=8)
    dijk_hop_2_post = link_state_dijkstra(topo2_post, "PC1", "PC2", metric="hops")
    dijk_lat_2_post = link_state_dijkstra(topo2_post, "PC1", "PC2", metric="latency")

    results["router_failure"] = {
        "topology_file": "router_failure.json",
        "source": "PC1",
        "destination": "PC2",
        "pre_failure": {
            "paths": [
                {
                    "path": p,
                    "path_str": " -> ".join(p),
                    "metrics": get_path_metrics(topo2, p),
                    "loss_math": format_loss_math(topo2, p),
                }
                for p in paths2_pre
            ],
            "dijkstra_hop": {
                "path": dijk_hop_2_pre["path"],
                "path_str": " -> ".join(dijk_hop_2_pre["path"]),
                "metrics": get_path_metrics(topo2, dijk_hop_2_pre["path"]),
                "loss_math": format_loss_math(topo2, dijk_hop_2_pre["path"]),
            },
            "dijkstra_latency": {
                "path": dijk_lat_2_pre["path"],
                "path_str": " -> ".join(dijk_lat_2_pre["path"]),
                "metrics": get_path_metrics(topo2, dijk_lat_2_pre["path"]),
                "loss_math": format_loss_math(topo2, dijk_lat_2_pre["path"]),
            },
        },
        "post_failure": {
            "failed_node": "R2",
            "paths": [
                {
                    "path": p,
                    "path_str": " -> ".join(p),
                    "metrics": get_path_metrics(topo2_post, p),
                    "loss_math": format_loss_math(topo2_post, p),
                }
                for p in paths2_post
            ],
            "dijkstra_hop": {
                "path": dijk_hop_2_post["path"],
                "path_str": " -> ".join(dijk_hop_2_post["path"]),
                "metrics": get_path_metrics(topo2_post, dijk_hop_2_post["path"]),
                "loss_math": format_loss_math(topo2_post, dijk_hop_2_post["path"]),
            },
            "dijkstra_latency": {
                "path": dijk_lat_2_post["path"],
                "path_str": " -> ".join(dijk_lat_2_post["path"]),
                "metrics": get_path_metrics(topo2_post, dijk_lat_2_post["path"]),
                "loss_math": format_loss_math(topo2_post, dijk_lat_2_post["path"]),
            },
        },
    }

    # 3. traffic_profile_change.json
    topo3 = Topology.load_json(TOPOLOGY_DIR / "traffic_profile_change.json")
    paths3 = enumerate_paths(topo3, "PC1", "PC2", max_hops=8)
    dijk_hop_3 = link_state_dijkstra(topo3, "PC1", "PC2", metric="hops")
    dijk_lat_3 = link_state_dijkstra(topo3, "PC1", "PC2", metric="latency")

    results["traffic_profile_change"] = {
        "topology_file": "traffic_profile_change.json",
        "source": "PC1",
        "destination": "PC2",
        "paths": [
            {
                "path": p,
                "path_str": " -> ".join(p),
                "metrics": get_path_metrics(topo3, p),
                "loss_math": format_loss_math(topo3, p),
            }
            for p in paths3
        ],
        "dijkstra_hop": {
            "path": dijk_hop_3["path"],
            "path_str": " -> ".join(dijk_hop_3["path"]),
            "metrics": get_path_metrics(topo3, dijk_hop_3["path"]),
            "loss_math": format_loss_math(topo3, dijk_hop_3["path"]),
        },
        "dijkstra_latency": {
            "path": dijk_lat_3["path"],
            "path_str": " -> ".join(dijk_lat_3["path"]),
            "metrics": get_path_metrics(topo3, dijk_lat_3["path"]),
            "loss_math": format_loss_math(topo3, dijk_lat_3["path"]),
        },
    }

    return results


def print_verification_report() -> None:
    """Print the complete formatted verification report with metric tables and per-link math."""
    data = compute_demo_verifications()

    print("=" * 105)
    print("NetSim Member 1 Demo Verification Report (Computed Strictly via network/*)")
    print("=" * 105)

    # 1. why_shortest_is_not_best
    d1 = data["why_shortest_is_not_best"]
    print(f"\n1. TOPOLOGY: {d1['topology_file']} ({d1['source']} -> {d1['destination']})")
    print("-" * 105)
    print(f"{'Role / Algorithm':<26} | {'Path':<36} | {'Hops':<5} | {'Latency':<8} | {'Cong (Max)':<10} | {'Loss':<8} | {'Reliability':<11}")
    print("-" * 105)
    for p_info in d1["paths"]:
        m = p_info["metrics"]
        role = "Candidate Path"
        if p_info["path"] == d1["dijkstra_hop"]["path"]:
            role = "Dijkstra (hop metric)"
        elif p_info["path"] == d1["dijkstra_latency"]["path"]:
            role = "Dijkstra (latency metric)"
        print(f"{role:<26} | {p_info['path_str']:<36} | {m['hop_count']:<5} | {m['latency']:<5.1f} ms | {m['congestion']*100:<8.1f}% | {m['packet_loss']*100:<6.2f}% | {m['reliability']*100:<9.2f}%")
    print("-" * 105)
    print("Per-link Packet Loss Math: 1 - product(1 - p_link):")
    for p_info in d1["paths"]:
        print(f"  • {p_info['path_str']}:")
        print(f"    {p_info['loss_math']}")

    # 2. router_failure
    d2 = data["router_failure"]
    print(f"\n2. TOPOLOGY: {d2['topology_file']} ({d2['source']} -> {d2['destination']})")
    print("-" * 105)
    print(f"{'Scenario / Role':<26} | {'Path':<36} | {'Hops':<5} | {'Latency':<8} | {'Cong (Max)':<10} | {'Loss':<8} | {'Reliability':<11}")
    print("-" * 105)
    for p_info in d2["pre_failure"]["paths"]:
        m = p_info["metrics"]
        role = "Pre-failure (active)" if p_info["path"] == d2["pre_failure"]["dijkstra_hop"]["path"] else "Pre-failure (alt)"
        print(f"{role:<26} | {p_info['path_str']:<36} | {m['hop_count']:<5} | {m['latency']:<5.1f} ms | {m['congestion']*100:<8.1f}% | {m['packet_loss']*100:<6.2f}% | {m['reliability']*100:<9.2f}%")
    for p_info in d2["post_failure"]["paths"]:
        m = p_info["metrics"]
        role = f"Post-failure ({d2['post_failure']['failed_node']} down)"
        print(f"{role:<26} | {p_info['path_str']:<36} | {m['hop_count']:<5} | {m['latency']:<5.1f} ms | {m['congestion']*100:<8.1f}% | {m['packet_loss']*100:<6.2f}% | {m['reliability']*100:<9.2f}%")
    print("-" * 105)
    print("Per-link Packet Loss Math: 1 - product(1 - p_link):")
    for p_info in d2["pre_failure"]["paths"]:
        print(f"  • Pre-failure {p_info['path_str']}:")
        print(f"    {p_info['loss_math']}")
    for p_info in d2["post_failure"]["paths"]:
        print(f"  • Post-failure {p_info['path_str']}:")
        print(f"    {p_info['loss_math']}")

    # 3. traffic_profile_change
    d3 = data["traffic_profile_change"]
    print(f"\n3. TOPOLOGY: {d3['traffic_profile_change']['topology_file'] if 'traffic_profile_change' in d3 else d3['topology_file']} ({d3['source']} -> {d3['destination']})")
    print("-" * 105)
    print(f"{'Role / Algorithm':<26} | {'Path':<36} | {'Hops':<5} | {'Latency':<8} | {'Cong (Max)':<10} | {'Loss':<8} | {'Reliability':<11}")
    print("-" * 105)
    for p_info in d3["paths"]:
        m = p_info["metrics"]
        role = "Candidate Path"
        if p_info["path"] == d3["dijkstra_hop"]["path"]:
            role = "Dijkstra (hop metric)"
        elif p_info["path"] == d3["dijkstra_latency"]["path"]:
            role = "Dijkstra (latency metric)"
        print(f"{role:<26} | {p_info['path_str']:<36} | {m['hop_count']:<5} | {m['latency']:<5.1f} ms | {m['congestion']*100:<8.1f}% | {m['packet_loss']*100:<6.2f}% | {m['reliability']*100:<9.2f}%")
    print("-" * 105)
    print("Per-link Packet Loss Math: 1 - product(1 - p_link):")
    for p_info in d3["paths"]:
        print(f"  • {p_info['path_str']}:")
        print(f"    {p_info['loss_math']}")
    print("=" * 105)


if __name__ == "__main__":
    print_verification_report()
