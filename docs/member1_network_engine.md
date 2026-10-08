# Member 1 Handbook: Network & Routing Engine

**Owner**: Ragghav Kamaraj (Member 1)  
**Packages Owned**: `network/`, `data/topologies/`, and associated `tests/` (`test_devices.py`, `test_topology.py`, `test_link_state.py`, `test_distance_vector.py`, `test_routing_table.py`).

---

## 1. Overview & Responsibilities
Ragghav Kamaraj provides the mathematical graph substrate and traditional routing baseline for NetSim-X.
All other team members depend on Member 1's topology abstractions and routing interfaces.

### Key Deliverables
1. **Topology Schema & Ingestion**:
   - Parse JSON topology scenarios into validated `Node` and `Link` models.
   - Enforce IPv4 validation for all nodes using `validate_ipv4()`.
2. **Graph Representation & Candidate Enumeration**:
   - Convert network topologies into `networkx.Graph` instances filtering out inactive entities.
   - Enumerate all simple loop-free paths up to a hop cutoff via `enumerate_paths(src, dst, max_hops)`.
3. **Traditional Routing Engines**:
   - **Link State / Dijkstra**: Shortest path computation based on hop count or latency.
   - **Distance Vector**: Iterative round-by-round Bellman-Ford simulation with convergence round counting and routing table updates.
4. **Router Forwarding Tables**:
   - `RoutingTable` structures and dynamic invalidation when next-hop routers crash.
5. **Unified Route Resolution**:
   - `find_route(source, destination, algorithm)` returning standard `RouteResult` schema.

---

## 2. Core File Layout & Function Signatures

```text
network/
├── __init__.py           # Exports Topology, Node, Link, RouteResult, etc.
├── devices.py            # Node, Link, RouteResult schemas and validate_ipv4
├── topology.py           # Topology class, JSON parser, NetworkX builder, path enumeration
├── link_state.py         # Dijkstra Link State algorithm
├── distance_vector.py    # Bellman-Ford round-based simulation & convergence counter
└── routing_table.py      # Routing table generation and failure invalidation
```

### Signature: `find_route`
```python
def find_route(
    self, source: str, destination: str, algorithm: str = "dijkstra"
) -> RouteResult:
    """Returns:
    {
        "path": ["PC1", "R1", "R2", "PC2"],
        "hop_count": 3,
        "latency": 22.0,
        "status": "success" | "no_route" | "invalid"
    }
    """
```

### Signature: `enumerate_paths`
```python
def enumerate_paths(
    self, source: str, destination: str, max_hops: int = 8
) -> List[List[str]]:
    """Returns list of candidate paths (e.g. [['PC1', 'R1', 'R2', 'PC2'], ...])"""
```

---

## 3. Definition of Done Checklist for Ragghav Kamaraj

- [x] All demo topologies in `data/topologies/` pass validation.
- [x] Invalid IPv4 strings rejected with clean `ValueError`.
- [x] Dijkstra correctly finds shortest paths and handles disconnected topologies without crashing.
- [x] Distance Vector simulation tracks convergence rounds and outputs populated next-hop tables.
- [x] Routing tables successfully invalidate routes passing through failed nodes.
- [x] All 30 unit tests pass cleanly with `pytest`.
