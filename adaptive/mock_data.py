"""Mock routing results and metrics fixtures for early UI and algorithm development.

Allows Member 2 and Member 3 to build and test UI widgets and comparative tables
without needing a live dependency on unresolved components.
"""

from __future__ import annotations

from typing import Any, Dict

MOCK_ROUTE_RESULTS: Dict[str, Dict[str, Any]] = {
    # Demo 1: Why shortest is not best
    "why_shortest_is_not_best": {
        "dijkstra": {
            "path": ["PC1", "R1", "R2", "R5", "PC2"],
            "hop_count": 4,
            "latency": 79.0,
            "status": "success",
            "congestion": 0.82,
            "packet_loss": 0.19,
            "reliability": 0.655,
            "score": 0.684,
        },
        "distance_vector": {
            "path": ["PC1", "R1", "R2", "R5", "PC2"],
            "hop_count": 4,
            "latency": 79.0,
            "status": "success",
            "convergence_rounds": 5,
            "congestion": 0.82,
            "packet_loss": 0.19,
            "reliability": 0.655,
            "score": 0.684,
        },
        "xar": {
            "path": ["PC1", "R1", "R3", "R4", "R5", "PC2"],
            "hop_count": 5,
            "latency": 36.0,
            "status": "success",
            "congestion": 0.12,
            "packet_loss": 0.029,
            "reliability": 0.969,
            "score": 0.288,
        },
        "explanation": (
            "XAR selected PC1 -> R1 -> R3 -> R4 -> R5 -> PC2 because latency was 43.0 ms lower, "
            "congestion was 70.0% lower, and expected packet loss was 16.1% lower. Although the alternative "
            "had 1 fewer hop, its adaptive score was 0.68 vs 0.29 under the Standard profile."
        ),
    },
    # Demo 2: Router failure
    "router_failure": {
        "healthy_route": {
            "path": ["PC1", "R1", "R2", "PC2"],
            "hop_count": 3,
            "latency": 14.0,
            "status": "success",
            "congestion": 0.10,
            "packet_loss": 0.007,
            "reliability": 0.988,
        },
        "post_failure_route": {
            "path": ["PC1", "R1", "R3", "R4", "PC2"],
            "hop_count": 4,
            "latency": 44.0,
            "status": "success",
            "congestion": 0.15,
            "packet_loss": 0.025,
            "reliability": 0.960,
        },
        "recovery_metrics": {
            "failed_node": "R2",
            "detection_delay_ms": 150.0,
            "recomputation_rounds": 4,
            "per_round_delay_ms": 50.0,
            "recovery_time_ms": 350.0,  # 150 + (4 * 50)
            "packets_lost": 12,
            "extra_hops": 1,
            "latency_increase_ms": 30.0,
        },
    },
    # Demo 3: Traffic profile change
    "traffic_profile_change": {
        "real_time": {
            "path": ["PC1", "R1", "R3", "R4", "PC2"],
            "hop_count": 4,
            "latency": 17.0,
            "packet_loss": 0.145,
            "reliability": 0.801,
            "score": 0.231,
            "rationale": "Real-time profile prioritizes 17.0 ms latency over loss, selecting the fast path.",
        },
        "reliable_data_transfer": {
            "path": ["PC1", "R1", "R2", "R4", "PC2"],
            "hop_count": 4,
            "latency": 69.0,
            "packet_loss": 0.003,
            "reliability": 0.997,
            "score": 0.185,
            "rationale": "Reliable profile heavily penalizes packet loss and unreliability, choosing the lossless path.",
        },
    },
}
