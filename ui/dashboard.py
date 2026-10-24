"""Algorithm comparison dashboard, Race Mode, and XAR analytics (Member 3).

Evaluates Dijkstra (Hop Count), Dijkstra (Latency), Distance Vector, and XAR side-by-side
on identical network topology snapshots, with comparative KPI tables, bar charts,
and the explainable decision justification panel.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from network.distance_vector import distance_vector_routing
from ui.xar_adapter import (
    FALLBACK_ALGO_LABEL,
    FALLBACK_BADGE_TEXT,
    REAL_ALGO_LABEL,
    generate_xar_explanation,
    resolve_xar_route,
    score_path_by_spec,
)

if TYPE_CHECKING:
    from network.topology import Topology


def build_comparison_benchmark(
    topology: Topology,
    source: str,
    destination: str,
    traffic_profile: str = "standard",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Execute all routing algorithms across identical graph state and collect metrics.

    Args:
        topology: Active authoritative Topology.
        source: Source node ID.
        destination: Destination node ID.
        traffic_profile: Active XAR traffic profile.

    Returns:
        Tuple of (table_rows_list, metadata_dict).
    """
    rows: List[Dict[str, Any]] = []

    # 1. Dijkstra (Hop Count)
    dijk_hop_route = topology.find_route(source, destination, algorithm="dijkstra", metric="hop")
    dijk_hop_path = dijk_hop_route.get("path", [])
    if dijk_hop_route.get("status") == "success" and dijk_hop_path:
        m_dh = topology.get_path_metrics(dijk_hop_path)
        score_dh, _ = score_path_by_spec(topology, dijk_hop_path, profile=traffic_profile)
        rows.append({
            "Algorithm": "Dijkstra (Hop Count)",
            "Badge": "Standard",
            "Path": " ➔ ".join(dijk_hop_path),
            "Hop Count": m_dh["hop_count"],
            "Latency (ms)": m_dh["latency"],
            "Packet Loss": f"{m_dh['packet_loss']*100:.2f}%",
            "Loss_Numeric": m_dh["packet_loss"] * 100.0,
            "Congestion": f"{int(m_dh['congestion']*100)}%",
            "Congestion_Numeric": m_dh["congestion"] * 100.0,
            "Reliability": f"{m_dh['reliability']*100:.2f}%",
            "Adaptive Score": score_dh,
            "Convergence": "1 round (SPF)",
        })
    else:
        rows.append({
            "Algorithm": "Dijkstra (Hop Count)",
            "Badge": "Standard",
            "Path": "No Route",
            "Hop Count": 0,
            "Latency (ms)": 0.0,
            "Packet Loss": "100.0%",
            "Loss_Numeric": 100.0,
            "Congestion": "100%",
            "Congestion_Numeric": 100.0,
            "Reliability": "0.0%",
            "Adaptive Score": 1.0,
            "Convergence": "Unconverged",
        })

    # 2. Dijkstra (Latency)
    dijk_lat_route = topology.find_route(source, destination, algorithm="dijkstra", metric="latency")
    dijk_lat_path = dijk_lat_route.get("path", [])
    if dijk_lat_route.get("status") == "success" and dijk_lat_path:
        m_dl = topology.get_path_metrics(dijk_lat_path)
        score_dl, _ = score_path_by_spec(topology, dijk_lat_path, profile=traffic_profile)
        rows.append({
            "Algorithm": "Dijkstra (Latency)",
            "Badge": "Standard",
            "Path": " ➔ ".join(dijk_lat_path),
            "Hop Count": m_dl["hop_count"],
            "Latency (ms)": m_dl["latency"],
            "Packet Loss": f"{m_dl['packet_loss']*100:.2f}%",
            "Loss_Numeric": m_dl["packet_loss"] * 100.0,
            "Congestion": f"{int(m_dl['congestion']*100)}%",
            "Congestion_Numeric": m_dl["congestion"] * 100.0,
            "Reliability": f"{m_dl['reliability']*100:.2f}%",
            "Adaptive Score": score_dl,
            "Convergence": "1 round (SPF)",
        })
    else:
        rows.append({
            "Algorithm": "Dijkstra (Latency)",
            "Badge": "Standard",
            "Path": "No Route",
            "Hop Count": 0,
            "Latency (ms)": 0.0,
            "Packet Loss": "100.0%",
            "Loss_Numeric": 100.0,
            "Congestion": "100%",
            "Congestion_Numeric": 100.0,
            "Reliability": "0.0%",
            "Adaptive Score": 1.0,
            "Convergence": "Unconverged",
        })

    # 3. Distance Vector
    try:
        dv_res = distance_vector_routing(topology, source, destination, metric="hop")
        dv_route = dv_res["route"]
        dv_rounds = dv_res.get("convergence_rounds", 0)
        dv_path = dv_route.get("path", [])
        if dv_route.get("status") == "success" and dv_path:
            m_dv = topology.get_path_metrics(dv_path)
            score_dv, _ = score_path_by_spec(topology, dv_path, profile=traffic_profile)
            rows.append({
                "Algorithm": "Distance Vector",
                "Badge": "Standard",
                "Path": " ➔ ".join(dv_path),
                "Hop Count": m_dv["hop_count"],
                "Latency (ms)": m_dv["latency"],
                "Packet Loss": f"{m_dv['packet_loss']*100:.2f}%",
                "Loss_Numeric": m_dv["packet_loss"] * 100.0,
                "Congestion": f"{int(m_dv['congestion']*100)}%",
                "Congestion_Numeric": m_dv["congestion"] * 100.0,
                "Reliability": f"{m_dv['reliability']*100:.2f}%",
                "Adaptive Score": score_dv,
                "Convergence": f"{dv_rounds} rounds (Bellman-Ford)",
            })
        else:
            rows.append({
                "Algorithm": "Distance Vector",
                "Badge": "Standard",
                "Path": "No Route",
                "Hop Count": 0,
                "Latency (ms)": 0.0,
                "Packet Loss": "100.0%",
                "Loss_Numeric": 100.0,
                "Congestion": "100%",
                "Congestion_Numeric": 100.0,
                "Reliability": "0.0%",
                "Adaptive Score": 1.0,
                "Convergence": f"{dv_rounds} rounds",
            })
    except Exception:
        rows.append({
            "Algorithm": "Distance Vector",
            "Badge": "Standard",
            "Path": "Error / Unconverged",
            "Hop Count": 0,
            "Latency (ms)": 0.0,
            "Packet Loss": "100.0%",
            "Loss_Numeric": 100.0,
            "Congestion": "100%",
            "Congestion_Numeric": 100.0,
            "Reliability": "0.0%",
            "Adaptive Score": 1.0,
            "Convergence": "N/A",
        })

    # 4. XAR via Adapter (calls adaptive.xar or automatic reference preview fallback)
    xar_route, xar_metrics, xar_score, is_fallback = resolve_xar_route(
        topology, source, destination, profile=traffic_profile
    )
    xar_path = xar_route.get("path", [])
    xar_label = FALLBACK_ALGO_LABEL if is_fallback else REAL_ALGO_LABEL
    xar_badge = FALLBACK_BADGE_TEXT if is_fallback else "Live Engine"

    if xar_route.get("status") == "success" and xar_path:
        rows.append({
            "Algorithm": xar_label,
            "Badge": xar_badge,
            "Path": " ➔ ".join(xar_path),
            "Hop Count": xar_metrics.get("hop_count", len(xar_path) - 1),
            "Latency (ms)": xar_metrics.get("latency", 0.0),
            "Packet Loss": f"{xar_metrics.get('packet_loss', 0.0)*100:.2f}%",
            "Loss_Numeric": xar_metrics.get("packet_loss", 0.0) * 100.0,
            "Congestion": f"{int(xar_metrics.get('congestion', 0.0)*100)}%",
            "Congestion_Numeric": xar_metrics.get("congestion", 0.0) * 100.0,
            "Reliability": f"{xar_metrics.get('reliability', 1.0)*100:.2f}%",
            "Adaptive Score": xar_score,
            "Convergence": "Evaluated candidate paths",
        })
    else:
        rows.append({
            "Algorithm": xar_label,
            "Badge": xar_badge,
            "Path": "No Route",
            "Hop Count": 0,
            "Latency (ms)": 0.0,
            "Packet Loss": "100.0%",
            "Loss_Numeric": 100.0,
            "Congestion": "100%",
            "Congestion_Numeric": 100.0,
            "Reliability": "0.0%",
            "Adaptive Score": 1.0,
            "Convergence": "N/A",
        })

    # Explanation generation
    explanation_text, expl_is_fallback = generate_xar_explanation(
        topology, xar_path, dijk_hop_path, profile=traffic_profile
    )

    metadata = {
        "xar_is_fallback": is_fallback,
        "explanation": explanation_text,
        "explanation_is_fallback": expl_is_fallback,
        "dijkstra_hop_path": dijk_hop_path,
        "xar_path": xar_path,
    }

    return rows, metadata


def render_comparison_dashboard(comparison_data: List[Dict[str, Any]]) -> None:
    """Render comparative performance summary table."""
    if not comparison_data:
        st.info("No comparative data available.")
        return

    # Filter out internal numeric helper keys for table display
    display_records = []
    for r in comparison_data:
        entry = {k: v for k, v in r.items() if not k.endswith("_Numeric")}
        display_records.append(entry)

    df = pd.DataFrame(display_records)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_algorithm_comparison_tab(
    topology: Topology,
    source: str,
    destination: str,
    traffic_profile: str = "standard",
) -> None:
    """Render complete Tab 4: Algorithm Comparison & Race Mode."""
    st.subheader("⚖️ Algorithm Comparison & Race Mode")
    st.caption(
        "Evaluate Dijkstra (Hop Count), Dijkstra (Latency), Distance Vector, and XAR side-by-side "
        "on the identical network topology snapshot."
    )

    if source not in topology.nodes or destination not in topology.nodes:
        st.warning("Selected endpoints do not exist in active topology.")
        return

    if source == destination:
        st.info("Source and destination endpoints are identical.")
        return

    rows, metadata = build_comparison_benchmark(
        topology, source, destination, traffic_profile=traffic_profile
    )

    # 1. Comparative Table
    st.markdown("### 📋 Multi-Algorithm Benchmark Matrix")
    render_comparison_dashboard(rows)

    # Fallback disclosure note
    if metadata.get("xar_is_fallback"):
        st.warning(
            f"🏷️ **Note on XAR [{FALLBACK_BADGE_TEXT}]**: "
            "Member 2's `adaptive.xar` engine is currently pending merge. The XAR results displayed above "
            "are calculated via the spec-compliant reference adapter by scoring candidate paths from Member 1's "
            "`enumerate_paths` against the exact mathematical formula in `docs/spec.md`. "
            "When Member 2 merges `adaptive.xar.xar_find_route`, this badge will automatically drop."
        )

    # 2. Key Metrics Side-by-Side (KPI columns)
    st.markdown("### 🏁 Performance KPI Cards")
    cols = st.columns(len(rows))
    for i, r in enumerate(rows):
        with cols[i]:
            score_val = r.get("Adaptive Score", 1.0)
            st.metric(
                label=r["Algorithm"].split("(")[0].strip(),
                value=f"{r.get('Latency (ms)', 0.0):.1f} ms",
                delta=f"Score: {score_val:.4f}",
                delta_color="inverse",
            )
            st.caption(f"Hops: **{r.get('Hop Count', 0)}** | Loss: **{r.get('Packet Loss', '0%')}**")

    # 3. Bar Charts Comparison
    st.markdown("### 📊 Graphical Metric Comparison")
    df_chart = pd.DataFrame([
        {
            "Algorithm": r["Algorithm"].replace(" (reference preview, not Member 2's implementation)", " [Preview]"),
            "Latency (ms)": r.get("Latency (ms)", 0.0),
            "Hop Count": r.get("Hop Count", 0),
            "Packet Loss (%)": r.get("Loss_Numeric", 0.0),
            "Congestion (%)": r.get("Congestion_Numeric", 0.0),
            "Penalty Score": r.get("Adaptive Score", 0.0),
        }
        for r in rows
    ])

    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.markdown("**Latency (ms) [Lower is Better]**")
        st.bar_chart(df_chart.set_index("Algorithm")[["Latency (ms)"]])
    with c_g2:
        st.markdown("**Bottleneck Congestion (%) [Lower is Better]**")
        st.bar_chart(df_chart.set_index("Algorithm")[["Congestion (%)"]])

    c_g3, c_g4 = st.columns(2)
    with c_g3:
        st.markdown("**Hop Count [Lower is Better]**")
        st.bar_chart(df_chart.set_index("Algorithm")[["Hop Count"]])
    with c_g4:
        st.markdown(f"**Multi-Criteria Adaptive Score ({traffic_profile.title()}) [Lower is Better]**")
        st.bar_chart(df_chart.set_index("Algorithm")[["Penalty Score"]])

    # 4. Explainable Decision Rationale Panel
    st.markdown("### 💡 Explainable Decision Engine (XAR Rationale)")
    badge_label = f"[{FALLBACK_BADGE_TEXT}]" if metadata.get("explanation_is_fallback") else "[Engine Output]"
    st.info(f"**{badge_label} Why This Route?**\n\n{metadata.get('explanation', 'No explanation generated.')}")
