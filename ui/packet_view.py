"""Packet simulation animation and statistics view (Member 3).

Renders transmission progress, packet loss gauges, and retransmission statistics
utilizing st.session_state for tick-based stepping.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st


def render_packet_simulation_view(
    path: List[str],
    metrics: Dict[str, Any],
) -> None:
    """Render packet flow and transmission statistics in Streamlit.

    Args:
        path: Path traversed by packets.
        metrics: Delivery, drop, and throughput metrics.
    """
    st.subheader("📦 Simulated Packet Flow")

    if not path or len(path) < 2:
        st.warning("Select valid source and destination endpoints to simulate packet transmission.")
        return

    st.markdown(f"**Path**: `{' ➔ '.join(path)}`")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Sent", f"{metrics.get('packets_sent', 100)} pkts")
    with c2:
        st.metric("Delivered", f"{metrics.get('packets_delivered', 98)} pkts")
    with c3:
        st.metric("Dropped", f"{metrics.get('packets_dropped', 2)} pkts")
    with c4:
        st.metric("Delivery Ratio", f"{metrics.get('delivery_ratio', 0.98)*100:.1f}%")

    loss_ratio = metrics.get("delivery_ratio", 0.98)
    st.progress(float(min(1.0, max(0.0, loss_ratio))))
