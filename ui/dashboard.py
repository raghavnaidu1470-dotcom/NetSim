"""Algorithm comparison dashboard and KPI metrics display (Member 3).

Renders side-by-side performance tables comparing Dijkstra, Distance Vector,
and XAR across latency, hop count, packet loss, congestion, and recovery time.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def render_comparison_dashboard(comparison_data: List[Dict[str, Any]]) -> None:
    """Render comparative performance metrics and summary table in Streamlit.

    Args:
        comparison_data: List of dicts with algorithm metrics.
    """
    st.subheader("📊 Algorithm Performance Benchmark")

    if not comparison_data:
        st.info("No route data available for comparison.")
        return

    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)

    # Highlight key metrics using Streamlit KPI columns
    cols = st.columns(len(comparison_data))
    for i, data in enumerate(comparison_data):
        with cols[i]:
            st.metric(
                label=f"🏁 {data.get('Algorithm', 'Unknown')}",
                value=f"{data.get('Latency (ms)', 0)} ms",
                delta=f"{data.get('Hop Count', 0)} hops",
                delta_color="inverse",
            )
