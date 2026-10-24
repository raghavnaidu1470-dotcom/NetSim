# Member 2 Handbook: Explainable Adaptive Routing (XAR) & Simulation

**Owner**: Harish (Member 2)  
**Packages Owned**: `adaptive/` (`xar.py`, `metrics.py`, `explanation.py`, `traffic_profiles.py`), `simulation/` (`failures.py`, `congestion.py`, `packet_loss.py`), and corresponding tests in `tests/`.

---

## 1. Purpose & Responsibilities
Harish develops the intellectual core of NetSim-X: the Explainable Adaptive Routing (XAR) engine, multi-metric normalization, dynamic traffic weighting, and network disruption simulation.

---

## 2. Files & Exact Function Signatures

### In `adaptive/metrics.py`:
```python
def aggregate_path_metrics(topology: Topology, path: List[str]) -> RawPathMetrics:
    """Aggregates latency (sum), loss (1 - prod(1-p)), reliability (prod),
    bottleneck congestion (max), and hops (len-1).
    """

def normalize_metrics(raw: RawPathMetrics) -> NormalizedMetrics:
    """Normalizes raw metrics into [0.0, 1.0]:
    H = min(1.0, raw['hop_count'] / 10.0)
    L = min(1.0, raw['latency'] / 200.0)
    C = raw['congestion']
    P = raw['packet_loss']
    R_penalty = 1.0 - raw['reliability']
    """

def compute_path_score(norm: NormalizedMetrics, weights: ProfileWeights) -> float:
    """Score(P) = w_h*H + w_l*L + w_c*C + w_p*P + w_r*(1-R)"""
```

### In `adaptive/xar.py`:
```python
def evaluate_all_candidate_paths(
    topology: Topology,
    source: str,
    destination: str,
    profile: str = "standard",
    max_hops: int = 8,
) -> List[PathEvaluation]:
    """Enumerates candidate paths via Member 1's topology.enumerate_paths(),
    scores each path, and returns list sorted by score ascending (lowest/best first).
    """

def xar_find_route(
    topology: Topology,
    source: str,
    destination: str,
    profile: str = "standard",
    max_hops: int = 8,
) -> RouteResult:
    """Returns RouteResult with path, hop_count, latency, and status='success'|'no_route'."""
```

### In `adaptive/explanation.py`:
```python
def compare_routes(
    topology: Topology,
    selected_path: List[str],
    alternative_path: List[str],
    profile: str = "standard",
) -> RouteComparison:
    """Computes metric deltas and generates a human-readable explanation."""
```

### In `simulation/failures.py`:
```python
def calculate_recovery_time(
    detection_delay_ms: float,
    recomputation_rounds: int,
    per_round_delay_ms: float = 50.0,
) -> float:
    """Recovery Time = detection_delay + (recomputation_rounds * per_round_delay)"""

def trigger_node_failure(
    topology: Topology,
    node_id: str,
    source: str,
    destination: str,
    algorithm: str = "xar",
) -> RecoveryMetrics: ...
```

---

## 3. Worked Mathematical Example on `why_shortest_is_not_best.json`

Between `PC1` and `PC2`:
- **Candidate 1 (Dijkstra (hop-count metric))**: `PC1 -> R1 -> R2 -> R5 -> PC2` (4 hops)
  - Hops: 4 $\implies H = 4 / 10 = 0.40$
  - Latency: $2 + 35 + 40 + 2 = 79.0\text{ ms} \implies L = 79.0 / 200 = 0.395$
  - Congestion: $\max(0.05, 0.78, 0.82, 0.05) = 0.82 \implies C = 0.820$
  - Loss: $1 - (0.999 \times 0.91 \times 0.89 \times 0.999) = 0.1917 \implies P = 0.1917$
  - Reliability: $0.999 \times 0.82 \times 0.80 \times 0.999 = 0.6547 \implies 1-R = 0.3453$
  - **Score (Standard Profile)**:
    $$0.20(0.40) + 0.25(0.395) + 0.20(0.82) + 0.20(0.1917) + 0.15(0.3453) = \mathbf{0.4329}$$

- **Candidate 2 (Alternative / XAR)**: `PC1 -> R1 -> R3 -> R4 -> R5 -> PC2` (5 hops)
  - Hops: 5 $\implies H = 5 / 10 = 0.50$
  - Latency: $2 + 10 + 12 + 10 + 2 = 36.0\text{ ms} \implies L = 36.0 / 200 = 0.180$
  - Congestion: $\max(0.05, 0.10, 0.12, 0.10, 0.05) = 0.12 \implies C = 0.120$
  - Loss: $1 - (0.999 \times 0.99 \times 0.99 \times 0.99 \times 0.999) = 0.0316 \implies P = 0.0316$
  - Reliability: $0.999 \times 0.99 \times 0.99 \times 0.99 \times 0.999 = 0.9684 \implies 1-R = 0.0316$
  - **Score (Standard Profile)**:
    $$0.20(0.50) + 0.25(0.180) + 0.20(0.12) + 0.20(0.0316) + 0.15(0.0316) = \mathbf{0.1801}$$

**Outcome**: Score $0.1801 < 0.4329$. XAR chooses Candidate 2.
*Note*: With a latency metric, Dijkstra would also select Candidate 2 ($36.0\text{ ms} < 79.0\text{ ms}$); this demo intentionally runs Dijkstra on hop count to expose the classic shortest-path pitfall.

### Explanation Output Format:
```text
"XAR selected PC1 -> R1 -> R3 -> R4 -> R5 -> PC2 because latency was 43.0 ms lower, 
congestion was 70.0% lower, and expected packet loss was 16.0% lower. Although the 
alternative had 1 fewer hop, its adaptive score was 0.43 vs 0.18 under the standard profile."
```

---

## 4. Member 1 Interfaces to Call (With Code Examples)

```python
# 1. Enumerate all possible candidate paths
paths = topology.enumerate_paths(source="PC1", destination="PC2", max_hops=8)

# 2. Get link attributes
link = topology.get_link("R1", "R2")
latency = link.latency
congestion = link.congestion

# 3. Simulate failure
topology.set_node_active("R2", False)   # Fails router R2
topology.set_link_active("R1", "R2", False) # Cuts link

# 4. Update link metrics
topology.update_link_metrics("R1", "R2", congestion=0.95, latency=120.0)

# 5. Fallback route search
dijkstra_res = topology.find_route("PC1", "PC2", algorithm="dijkstra")
```

---

## 5. Definition of Done Checklist for Harish

- [x] Unskip and pass tests in `tests/test_metrics.py`.
- [x] Unskip and pass tests in `tests/test_xar.py`.
- [x] Unskip and pass tests in `tests/test_explanation.py`.
- [x] Unskip and pass tests in `tests/test_failures.py`.
- [x] Unskip and pass tests in `tests/test_congestion.py`.
- [x] Unskip and pass tests in `tests/test_packet_loss.py`.
- [x] Verify that XAR does not artificially win every race; verify edge cases where routes tie.
- [x] Update `STATUS.md` after each pull request.
