# NetSim-X Architecture & Specification

## 1. Executive Summary & Shared Data Schemas

NetSim-X uses a strongly typed, unified data representation across all three submodules (`network/`, `adaptive/`, `ui/`). 
All schemas are defined in `network/devices.py` as Python dataclasses and `TypedDict` specifications.

### Node Schema
Represents either a router or an end host.

```json
{
  "id": "R1",
  "ip": "192.168.1.1",
  "type": "router",
  "active": true
}
```

- `id` (`str`): Unique identifier within the topology (e.g., `PC1`, `R1`).
- `ip` (`str`): Valid IPv4 address string (strictly validated via `network.devices.validate_ipv4`).
- `type` (`str`): `"router"` or `"host"`.
- `active` (`bool`): Operational status (`true` = online, `false` = offline/crashed).

### Link Schema
Represents a bidirectional transmission channel between two nodes.

```json
{
  "source": "R1",
  "destination": "R2",
  "latency": 20.0,
  "bandwidth": 100.0,
  "congestion": 0.30,
  "packet_loss": 0.02,
  "reliability": 0.98,
  "active": true
}
```

- `source`, `destination` (`str`): Node IDs.
- `latency` (`float`): Link propagation + transmission delay in milliseconds ($ms \ge 0$).
- `bandwidth` (`float`): Throughput capacity in Mbps ($> 0$).
- `congestion` (`float`): Current link utilization factor $\in [0.0, 1.0]$.
- `packet_loss` (`float`): Probability of random packet drop $\in [0.0, 1.0]$.
- `reliability` (`float`): Operational availability probability $\in [0.0, 1.0]$.
- `active` (`bool`): Physical link connectivity status.

### Unified RouteResult Schema
Every routing protocol returns results adhering to this schema:

```json
{
  "path": ["PC1", "R1", "R2", "PC2"],
  "hop_count": 3,
  "latency": 22.0,
  "status": "success"
}
```

- `path` (`List[str]`): Sequence of visited node IDs. Empty if no route exists.
- `hop_count` (`int`): Total link traversals ($|path| - 1$).
- `latency` (`float`): Cumulative path latency in milliseconds.
- `status` (`str`): `"success"`, `"no_route"`, or `"invalid"`.

---

## 2. Path-Level Metric Aggregation Rules

Given path $P = (v_1, v_2, \dots, v_k)$ traversing links $e_1, e_2, \dots, e_{k-1}$:

1. **Hop Count ($H$)**:
   $$\text{Hops}(P) = k - 1$$
2. **Cumulative Latency ($L_{\text{raw}}$)**:
   $$L_{\text{raw}}(P) = \sum_{i=1}^{k-1} \text{latency}(e_i)$$
3. **End-to-End Packet Loss Probability ($P_{\text{raw}}$)**:
   $$P_{\text{raw}}(P) = 1 - \prod_{i=1}^{k-1} \left(1 - p_{\text{loss}}(e_i)\right)$$
4. **End-to-End Reliability ($R_{\text{raw}}$)**:
   $$R_{\text{raw}}(P) = \prod_{i=1}^{k-1} \text{reliability}(e_i)$$
5. **Path Bottleneck Congestion ($C_{\text{raw}}$)**:
   $$C_{\text{raw}}(P) = \max_{i=1}^{k-1} \text{congestion}(e_i)$$

---

## 3. Normalization Rules (Fixed Ceilings)

To prevent arbitrary scale dominance, all metrics are normalized to the unit interval $[0.0, 1.0]$ where **0.0 is ideal** and **1.0 is worst**:

- **Hop Ceiling**: $\text{MAX\_HOPS} = 10$
  $$H = \min\left(1.0, \frac{\text{Hops}(P)}{10.0}\right)$$
- **Latency Ceiling**: $\text{MAX\_LATENCY} = 200.0\text{ ms}$
  $$L = \min\left(1.0, \frac{L_{\text{raw}}(P)}{200.0}\right)$$
- **Congestion**:
  $$C = C_{\text{raw}}(P) \in [0.0, 1.0]$$
- **Packet Loss**:
  $$P = P_{\text{raw}}(P) \in [0.0, 1.0]$$
- **Reliability Penalty**:
  $$\text{Penalty}_R = 1.0 - R_{\text{raw}}(P) \in [0.0, 1.0]$$

---

## 4. XAR Mathematical Formulation & Traffic Profiles

### Scoring Equation
$$\text{Score}(P) = w_h \cdot H + w_l \cdot L + w_c \cdot C + w_p \cdot P + w_r \cdot (1 - R)$$

**Evaluation Rule**: **Lower score is strictly better.**

### Weight Matrix
All profiles are normalized such that $\sum w = 1.00$:

| Profile Name | $w_h$ (Hops) | $w_l$ (Latency) | $w_c$ (Congestion) | $w_p$ (Loss) | $w_r$ (Reliability) | Primary Objective |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Standard** | 0.20 | 0.25 | 0.20 | 0.20 | 0.15 | Balanced multi-criteria |
| **Real-Time** | 0.10 | 0.45 | 0.15 | 0.25 | 0.05 | Minimizing jitter & delay |
| **Reliable Data Transfer** | 0.05 | 0.15 | 0.10 | 0.40 | 0.30 | Zero packet drops & high integrity |

---

## 5. Worked Mathematical Example

Using `data/topologies/why_shortest_is_not_best.json` between `PC1` and `PC2`:

- **Route A (Shortest Hop / Dijkstra)**: `PC1 -> R1 -> R2 -> R5 -> PC2` (4 hops)
  - Raw: Latency = $79.0\text{ ms}$, Loss = $0.188$, Bottleneck Congestion = $0.82$, Reliability = $0.655$.
  - Normalized:
    - $H = 4 / 10 = 0.400$
    - $L = 79.0 / 200 = 0.395$
    - $C = 0.820$
    - $P = 0.188$
    - $1 - R = 1 - 0.655 = 0.345$
  - Standard Score:
    $$\text{Score}(A) = 0.20(0.40) + 0.25(0.395) + 0.20(0.82) + 0.20(0.188) + 0.15(0.345) = \mathbf{0.432}$$

- **Route B (Alternative / XAR Choice)**: `PC1 -> R1 -> R3 -> R4 -> R5 -> PC2` (5 hops)
  - Raw: Latency = $36.0\text{ ms}$, Loss = $0.029$, Bottleneck Congestion = $0.12$, Reliability = $0.969$.
  - Normalized:
    - $H = 5 / 10 = 0.500$
    - $L = 36.0 / 200 = 0.180$
    - $C = 0.120$
    - $P = 0.029$
    - $1 - R = 1 - 0.969 = 0.031$
  - Standard Score:
    $$\text{Score}(B) = 0.20(0.50) + 0.25(0.180) + 0.20(0.12) + 0.20(0.029) + 0.15(0.031) = \mathbf{0.179}$$

**Result**: $\text{Score}(B) = 0.179 < \text{Score}(A) = 0.432$.
XAR picks Route B even though it is 1 hop longer, because it reduces latency by $43\text{ ms}$, reduces congestion by $70\%$, and drops loss by $15.9\%$.

---

## 6. Resilience & Formal Recovery Time Definition

When a network component fails, total system recovery time is formally defined as:

$$\text{Recovery Time} = T_{\text{detect}} + (N_{\text{rounds}} \times T_{\text{round}})$$

- $T_{\text{detect}}$: Heartbeat loss / keepalive timeout delay (typically $100\text{ ms} - 300\text{ ms}$).
- $N_{\text{rounds}}$: Number of iterative routing protocol convergence rounds required for graph synchronization.
- $T_{\text{round}}$: Exchange propagation and processing latency per round (typically $50\text{ ms}$).

Example: With $T_{\text{detect}} = 150\text{ ms}$, $N_{\text{rounds}} = 4$, and $T_{\text{round}} = 50\text{ ms}$:
$$\text{Recovery Time} = 150 + (4 \times 50) = 350\text{ ms}$$

During this window, packets in flight traversing failed devices are counted as lost and require retransmission.
