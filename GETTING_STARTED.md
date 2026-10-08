# Getting Started with NetSim-X

Welcome to **NetSim-X**! This guide gets you up and running in under 5 minutes and points you directly to your role-specific documentation and tasks.

---

## 1. 5-Minute Setup

### Prerequisites
- Python 3.11+ (or Python 3.9+)
- `git`
- Virtual environment tool (`venv`)

### Setup Commands
```bash
# 1. Clone repository
git clone https://github.com/raghavnaidu1470-dotcom/netsim-x.git
cd netsim-x

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify test suite (all active tests must pass!)
pytest

# 5. Run a sample route query from the CLI
python3 -c "from network.topology import Topology; t = Topology.load_json('data/topologies/why_shortest_is_not_best.json'); print('Dijkstra route:', t.find_route('PC1', 'PC2', 'dijkstra'))"

# 6. Launch the interactive Streamlit dashboard
streamlit run ui/app.py
```

---

## 2. Find Your Role

| Role | Teammate | Folders Owned | Handbook to Read | First 3 Tasks |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** | Raghav | `network/`, `data/topologies/` | [`docs/member1_network_engine.md`](docs/member1_network_engine.md) | 1. Review NetworkX graph and path enumeration.<br>2. Extend Bellman-Ford convergence round counting.<br>3. Add routing table invalidation tests. |
| **Member 2** | Harish | `adaptive/`, `simulation/` | [`docs/member2_xar_simulation.md`](docs/member2_xar_simulation.md) | 1. Implement `adaptive/metrics.py` (aggregation & normalization).<br>2. Implement `adaptive/xar.py` and unskip tests.<br>3. Implement failure and recovery simulation in `simulation/`. |
| **Member 3** | Akhilesh | `ui/`, `protocols/` | [`docs/member3_ui_analytics.md`](docs/member3_ui_analytics.md) | 1. Run `streamlit run ui/app.py` and test the 5 tabs.<br>2. Wire up live comparison dashboard with mock/live data.<br>3. Implement TCP/UDP and CRC demos in `protocols/`. |

---

## 3. Branch & Pull Request Workflow

We use a feature branch workflow off `develop`. `main` is protected and receives only verified milestone releases.

### Exact Git Commands:
```bash
# 1. Fetch latest develop branch
git checkout develop
git pull origin develop

# 2. Create your feature branch (choose corresponding branch name)
# Member 1:
git checkout -b feature/network-engine
# Member 2:
git checkout -b feature/xar-simulation
# Member 3:
git checkout -b feature/ui-analytics

# 3. Work on your files, write tests, and verify
pytest

# 4. Update STATUS.md to reflect current progress!

# 5. Commit changes with clear message
git add .
git commit -m "feat(xar): implement path metric normalization and unskip tests"

# 6. Push to GitHub
git push -u origin feature/<your-branch-name>

# 7. Open a Pull Request targeting 'develop'
# Fill out the PR template checklist in GitHub.
```

---

## 4. Communication & Governance ("Who to Ask for What")

- **Topology & Routing Interfaces**: Ask **Member 1**. He owns `network/` and the NetworkX graph abstractions.
- **XAR Formula & Resilience Calculations**: Ask **Member 2 (Harish)**. He owns metric weights, scoring, and failure recovery.
- **Streamlit Layout, Visuals & Protocols**: Ask **Member 3 (Akhilesh)**. He owns GUI tabs and TCP/UDP/CRC labs.
- **Shared Schemas (`docs/spec.md`)**: **Requires consensus across ALL 3 members**. Do not modify `docs/spec.md` without agreement.
