"""Protocol Lab UI component for TCP/UDP and CRC error detection (Member 3).

Renders side-by-side transport layer comparisons (TCP sliding window vs UDP datagrams)
and data-link layer Cyclic Redundancy Check (CRC) polynomial division with interactive
error injection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from protocols.crc import (
    CRC_4,
    CRC_8,
    corrupt_bits,
    crc_check,
    crc_encode,
    crc_remainder,
    run_crc_demo,
    validate_bitstring,
    validate_generator,
)
from protocols.tcp_udp import simulate_tcp, simulate_udp

if TYPE_CHECKING:
    from network.topology import Topology


def render_protocol_lab_tab(
    topology: Topology,
    active_path: Optional[List[str]] = None,
) -> None:
    """Render complete Tab 5: Protocol Lab view."""
    st.subheader("🔬 Protocol Lab: Transport & Data-Link Demonstration")
    st.caption("Interactive simulations of TCP connection control, UDP fire-and-forget, and CRC polynomial division.")

    sub1, sub2 = st.tabs(["📦 Transport Layer: TCP vs UDP", "🛡️ Data Link Layer: CRC Error Detection"])

    # SUBTAB 1: TCP vs UDP
    with sub1:
        st.markdown("### 🔄 TCP Sliding Window vs UDP Datagram Burst")
        st.caption(
            "TCP guarantees in-order reliable delivery via 3-way handshakes, sequence numbers, timeouts, "
            "and retransmissions. UDP transmits connectionless datagrams with minimal overhead."
        )

        # Retrieve default packet loss from the current active route
        default_loss_pct = 5.0
        if active_path and len(active_path) >= 2:
            try:
                m = topology.get_path_metrics(active_path)
                default_loss_pct = round(m.get("packet_loss", 0.05) * 100.0, 1)
            except Exception:
                pass

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            num_pkts = st.slider("Payload Segments (KB)", min_value=1, max_value=30, value=10, step=1)
        with col_c2:
            loss_rate = st.slider(
                "Channel Packet Loss (%)",
                min_value=0.0,
                max_value=40.0,
                value=float(min(40.0, max(0.0, default_loss_pct))),
                step=1.0,
                help=f"Defaults to active route packet loss ({default_loss_pct:.1f}%). Adjust with slider to test scenarios.",
            )
        with col_c3:
            w_size = st.slider("TCP Window Size", min_value=1, max_value=4, value=2, step=1)
        with col_c4:
            lab_seed = st.number_input("Simulation Seed", min_value=1, max_value=9999, value=42)

        loss_prob = loss_rate / 100.0

        # Run simulations
        tcp_res = simulate_tcp(
            num_packets=num_pkts,
            loss_probability=loss_prob,
            seed=int(lab_seed),
            window_size=w_size,
            rtt_ms=40.0,
            timeout_ms=80.0,
        )
        udp_res = simulate_udp(
            num_packets=num_pkts,
            loss_probability=loss_prob,
            seed=int(lab_seed),
            rtt_ms=40.0,
        )

        # Summary KPIs Side-by-Side
        st.markdown("#### Transmission Summary")
        col_tcp_kpi, col_udp_kpi = st.columns(2)

        with col_tcp_kpi:
            st.markdown("##### 🟦 TCP (Transmission Control Protocol)")
            t1, t2, t3 = st.columns(3)
            with t1:
                st.metric("Total Sent", f"{tcp_res['sent']} segs")
            with t2:
                st.metric("Retransmissions", f"{tcp_res['retransmitted']}", delta="Resent on Drop", delta_color="inverse")
            with t3:
                st.metric("Delivered", f"{tcp_res['delivered']} segs")

            t4, t5, t6 = st.columns(3)
            with t4:
                st.metric("Handshake", f"{tcp_res['handshake_latency_ms']:.1f} ms")
            with t5:
                st.metric("Total Duration", f"{tcp_res['total_time_ms']:.1f} ms")
            with t6:
                st.metric("Throughput", f"{tcp_res['effective_throughput_mbps']:.2f} Mbps")

            if tcp_res["failed"] > 0:
                st.warning(f"⚠️ {tcp_res['failed']} segment(s) reached max retries under heavy channel loss.")
            else:
                st.success("✅ 100% Reliable Delivery (All segments acknowledged)")

        with col_udp_kpi:
            st.markdown("##### 🟧 UDP (User Datagram Protocol)")
            u1, u2, u3 = st.columns(3)
            with u1:
                st.metric("Total Sent", f"{udp_res['sent']} datagrams")
            with u2:
                st.metric("Delivered", f"{udp_res['delivered']} datagrams")
            with u3:
                st.metric("Dropped in Transit", f"{udp_res['lost']}", delta=f"{100 - udp_res['delivered_percentage']:.1f}% loss", delta_color="inverse")

            u4, u5, u6 = st.columns(3)
            with u4:
                st.metric("Handshake", "0.0 ms (None)")
            with u5:
                st.metric("Total Duration", f"{udp_res['total_time_ms']:.1f} ms")
            with u6:
                st.metric("Delivery Rate", f"{udp_res['delivered_percentage']:.1f}%")

            if udp_res["lost"] > 0:
                st.info(f"ℹ️ {udp_res['lost']} datagram(s) dropped permanently (no retransmissions in UDP).")
            else:
                st.success("✅ 100% of datagrams arrived safely.")

        st.markdown("---")
        st.markdown("#### Message Sequence Event Timelines")
        col_tcp_tl, col_udp_tl = st.columns(2)

        with col_tcp_tl:
            st.markdown("**TCP Event Timeline**")
            tcp_df = pd.DataFrame([
                {
                    "Time (ms)": f"{e['time_ms']:.1f}",
                    "Type": e["event_type"],
                    "Details": e["description"],
                }
                for e in tcp_res["events"]
            ])
            st.dataframe(tcp_df, use_container_width=True, hide_index=True)

        with col_udp_tl:
            st.markdown("**UDP Event Timeline**")
            udp_df = pd.DataFrame([
                {
                    "Time (ms)": f"{e['time_ms']:.1f}",
                    "Type": e["event_type"],
                    "Details": e["description"],
                }
                for e in udp_res["events"]
            ])
            st.dataframe(udp_df, use_container_width=True, hide_index=True)

    # SUBTAB 2: CRC ERROR DETECTION
    with sub2:
        st.markdown("### 🛡️ Cyclic Redundancy Check (CRC) Polynomial Division")
        st.caption(
            "Cyclic Redundancy Check uses modulo-2 polynomial division (XOR) to append a remainder checksum "
            "to message bits. Any transmission bit flips are detected at the receiver via syndrome verification."
        )

        col_in1, col_in2 = st.columns([2, 1])
        with col_in1:
            data_input = st.text_input("Message Data Bitstring (Binary 0/1)", value="1101011011")
        with col_in2:
            poly_choice = st.selectbox(
                "Generator Polynomial Divisor",
                options=["CRC-4 (10011)", "CRC-8 (100000111)", "Custom Generator"],
                index=0,
            )

        if poly_choice == "CRC-4 (10011)":
            selected_poly = CRC_4
        elif poly_choice == "CRC-8 (100000111)":
            selected_poly = CRC_8
        else:
            selected_poly = st.text_input("Enter Custom Polynomial (e.g. 1011)", value="10011")

        # Validate inputs gracefully
        try:
            validate_bitstring(data_input, name="Data bits")
            validate_generator(selected_poly)
            valid_inputs = True
        except ValueError as err:
            st.error(f"Input Error: {err}")
            valid_inputs = False

        if valid_inputs:
            k = len(selected_poly) - 1
            remainder, steps = crc_remainder(data_input, selected_poly)
            transmitted_frame = crc_encode(data_input, selected_poly)

            st.markdown("#### 1. Sender Calculation (Modulo-2 Division)")
            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                st.code(f"Original Data:\n{data_input}\n(Length: {len(data_input)} bits)")
            with c_s2:
                st.code(f"Appended Zeros (k={k}):\n{data_input + ('0' * k)}\n(Divisor: {selected_poly})")
            with c_s3:
                st.code(f"CRC Checksum (Remainder):\n{remainder}\nTransmitted Frame:\n{transmitted_frame}")

            with st.expander(f"🔍 Show {len(steps)} Intermediate XOR Division Steps"):
                step_records = [
                    {
                        "Step #": s["step_index"],
                        "Bit Pos": s["bit_index"],
                        "Current Dividend": s["current_dividend"],
                        "Divisor Applied": s["divisor"],
                        "Intermediate State": s["intermediate_remainder"],
                    }
                    for s in steps
                ]
                st.dataframe(pd.DataFrame(step_records), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### 2. Communication Channel & Bit Corruption")
            corrupt_toggle = st.checkbox("Inject Transmission Bit Error", value=False)
            corrupt_pos = -1

            if corrupt_toggle:
                corrupt_pos = st.slider(
                    "Select Bit Position to Flip (0-indexed)",
                    min_value=0,
                    max_value=len(transmitted_frame) - 1,
                    value=0,
                )
                received_frame = corrupt_bits(transmitted_frame, corrupt_pos)
                st.warning(
                    f"⚠️ Injected bit flip at position `{corrupt_pos}`: "
                    f"Transmitted `{transmitted_frame[corrupt_pos]}` ➔ Received `{received_frame[corrupt_pos]}`"
                )
            else:
                received_frame = transmitted_frame
                st.success("Channel Status: Clean (No transmission errors injected)")

            st.markdown("#### 3. Receiver Syndrome Verification")
            is_valid = crc_check(received_frame, selected_poly)

            # Calculate receiver remainder
            rec_div = list(received_frame)
            for i in range(len(received_frame) - k):
                if rec_div[i] == "1":
                    for j in range(len(selected_poly)):
                        rec_div[i + j] = str(int(rec_div[i + j]) ^ int(selected_poly[j]))
            syndrome = "".join(rec_div[-k:]) if k > 0 else "0"

            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.code(f"Received Frame:\n{received_frame}\nCalculated Syndrome:\n{syndrome}")
            with r_col2:
                if is_valid:
                    st.success("✅ **Frame Integrity Verified**: Syndrome is all zeros (0000). No transmission errors detected.")
                else:
                    st.error(f"❌ **Transmission Error Detected!**: Syndrome `{syndrome}` is non-zero. The frame is corrupt and must be rejected.")
