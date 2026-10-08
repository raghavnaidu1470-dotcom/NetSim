# NetSim-X Contribution Guidelines

Thank you for contributing to NetSim-X! To ensure smooth collaboration across our 3-person team, please follow these rules.

---

## 1. Team Ownership Boundaries
To eliminate git merge conflicts, folders are strictly partitioned:
- **Member 1**: `network/`, `data/topologies/`
- **Member 2 (Harish)**: `adaptive/`, `simulation/`
- **Member 3 (Akhilesh)**: `ui/`, `protocols/`

**Rule**: Do not edit files belonging to other team members unless coordinated in an integration meeting.

---

## 2. Shared Specifications
All three team members must agree before modifying schemas in `docs/spec.md`. Any proposed schema change must be documented in a team issue first.

---

## 3. Pull Request Requirements
1. **Target Branch**: All feature branches must branch off `develop` and target `develop` for PRs.
2. **Testing**: Run `pytest` locally. Zero tests may fail.
3. **Unskipping Tests**: When implementing a feature, remove `@pytest.mark.skip` from the corresponding test in `tests/` and verify it passes.
4. **Status Tracking**: **EVERY PR MUST UPDATE `STATUS.md`** to reflect the state of implemented modules (`done`, `in_progress`, or `stub`).
5. **PR Checklist**: Complete all items in `.github/pull_request_template.md`.
