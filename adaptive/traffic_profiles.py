"""Traffic profile definitions and metric weighting coefficients for XAR (Member 2).

Traffic profiles steer the Explainable Adaptive Routing (XAR) algorithm by adjusting
the penalty weights assigned to Hop Count, Latency, Congestion, Loss, and Reliability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

ProfileName = Literal["standard", "real_time", "reliable_data_transfer"]


@dataclass(frozen=True)
class ProfileWeights:
    """Weight vector for XAR cost scoring: Score = w_h*H + w_l*L + w_c*C + w_p*P + w_r*(1-R).

    All weights must sum to 1.0 (or be normalized) for intuitive interpretation.
    """
    w_h: float  # Hop count weight
    w_l: float  # Latency weight
    w_c: float  # Congestion weight
    w_p: float  # Packet loss weight
    w_r: float  # Reliability weight

    def __post_init__(self) -> None:
        total = self.w_h + self.w_l + self.w_c + self.w_p + self.w_r
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Profile weights must sum to approximately 1.0 (got {total:.3f})")


TRAFFIC_PROFILES: Dict[ProfileName, ProfileWeights] = {
    # Standard: Balanced multi-objective weighting
    "standard": ProfileWeights(
        w_h=0.20,
        w_l=0.25,
        w_c=0.20,
        w_p=0.20,
        w_r=0.15,
    ),
    # Real-Time: latency > packet loss > congestion > hops > reliability
    "real_time": ProfileWeights(
        w_h=0.10,
        w_l=0.45,
        w_c=0.15,
        w_p=0.25,
        w_r=0.05,
    ),
    # Reliable Data Transfer: packet loss > reliability > latency > hops > congestion
    "reliable_data_transfer": ProfileWeights(
        w_h=0.05,
        w_l=0.15,
        w_c=0.10,
        w_p=0.40,
        w_r=0.30,
    ),
}


def get_profile_weights(profile: str = "standard") -> ProfileWeights:
    """Retrieve ProfileWeights for the requested traffic profile name.

    Args:
        profile: Name of profile ('standard', 'real_time', or 'reliable_data_transfer').

    Returns:
        ProfileWeights instance.
    """
    normalized = profile.lower().strip().replace("-", "_").replace(" ", "_")
    if normalized in TRAFFIC_PROFILES:
        return TRAFFIC_PROFILES[normalized]  # type: ignore
    return TRAFFIC_PROFILES["standard"]
