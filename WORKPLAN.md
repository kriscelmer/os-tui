# OS‑TUI — WORKPLAN

This workplan translates the PRD into **executable milestones** with artifacts, acceptance criteria, and **Codex CLI (GPT‑5‑Codex)** prompts you can run from the terminal.

**Repository:** `kriscelmer/os-tui`
**Languages/Tooling:** Python 3.11/3.12, openstacksdk, Textual, pytest, ruff, mypy, pre‑commit

---

## 0) Pre‑flight

- Install Python 3.11+ and `pipx` (optional).
- Install **pre‑commit**, **ruff**, **mypy** (CI will run them).
- Install GitHub CLI (`gh`) and authenticate: `gh auth login`.
- (Optional) Install **Codex CLI** and choose `gpt-5-codex` as the working model.

```bash
# Create repo
gh repo create kriscelmer/os-tui --public --clone
cd os-tui

# Setup venv & dev deps
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```
---

## Milestones overview

- **M0 Bootstrap** — repo skeleton, CI, docs.
- **M1 Core** — config, auth, encrypted profiles, connection factory, service discovery.
- **M2 Overview** — TUI shell, quotas/usage/orphans/events.
- **M3 Compute & Images** — lists, details, core actions; Launch wizard (minimal).
- **M4 Network** — CRUD + VPC‑like wizard; SG templates & diffs.
- **M5 Block Storage** — CRUD + retype/extend; snapshot/backup.
- **M6 Object Storage (Swift)** — dual‑pane browser + metadata + Temp URLs.
- **M7 Octavia** — E2E LB wizard + rotation helper.
- **M8 Heat** — tree + editor + validate + preview + update.
- **M9 Telemetry** — adapter(s) + sparklines + alarm wizard.
- **M10 Reports & Recipes** — inventory export, orphan cleanup, recipe save/replay, basic Git ops.
- **M11 AI Assistant (feature‑flagged)** — advise/compose schemas; plan w/ preflight + dry‑run + approvals.

Each milestone includes: **tests**, **docs**, and **release notes**.

---

## M0 — Bootstrap

**Deliverables**
- Repo layout, PRD.md, WORKPLAN.md, LICENSE (Apache‑2.0), README, ADR folder.
- Tooling: `pyproject.toml`, pre‑commit, ruff, mypy; CI pipeline (lint/type/tests/coverage).

**Acceptance Criteria**
- CI green on empty skeleton; pre‑commit works locally; README Quickstart verified.

**Suggested Codex prompt**
```
Initialize the OS-TUI repo with the skeleton in WORKPLAN: pyproject.toml, pre-commit, ruff, mypy, CI workflow, README, PRD.md and WORKPLAN.md placeholders.
```

---

## M1 — Core (config, auth, service discovery)

**Deliverables**
- `os_tui.core.config`: precedence (env → clouds.yaml → prompt); encrypted profiles via keyring or Fernet.
- `os_tui.sdk.conn`: ConnectionFactory returning `openstacksdk.Connection` with friendly error mapping and request‑ID surfacing.
- `os_tui.sdk.capabilities`: CapabilitiesMap from service catalog + microversions.

**Tests (TDD)**
- Config precedence & encrypted round‑trip.
- ConnectionFactory: happy path; 401/403/SSL mapped to helpful RuntimeError including request IDs.
- Capabilities detection: presence/absence and microversions.

**Acceptance Criteria**
- Given valid inputs, a ResolvedAuth creates a working Connection and a populated CapabilitiesMap; secrets never appear in logs.

**Suggested Codex prompts**
```
Write tests for config precedence and encrypted profile storage, then implement os_tui/core/config.py to pass.
```
```
Write tests for ConnectionFactory error mapping, then implement os_tui/sdk/conn.py to pass.
```
```
Write tests for CapabilitiesMap with fake catalog, then implement os_tui/sdk/capabilities.py to pass.
```

---

## M2 — Overview screen

**Deliverables**
- Textual **App shell** with tabs, keybar, and a two‑pane Overview screen.
- Quotas vs usage; orphaned resources preview; recent events; token expiry; non‑blocking loads with spinners.

**Tests**
- Widget snapshot tests (Textual testing utilities).
- Quota math correctness; pagination/incremental rendering with large lists.

**Acceptance Criteria**
- First paint ≤ ~1.5s for lists (paginated); correct quota/usage values; no UI lockups during fetch.

**Suggested Codex prompts**
```
Scaffold Textual app with Overview screen, using CapabilitiesMap + ConnectionFactory. Add snapshot tests for widgets.
```

---

## M3 — Compute & Images

**Deliverables**
- Lists: instances, images, keypairs, flavors.
- Right‑pane **show** view (relationships and metadata).
- Actions: start/stop/reboot; pause/suspend/resume; shelve/unshelve; snapshot; lock/unlock; attach/detach volume; associate/disassociate FIP (preflight & confirmations).
- **Launch wizard** (minimal) with validation and **quota preview**; **save as recipe**.

**Tests**
- Action preconditions & friendly error mapping (403 → policy hint).
- Launch validation (image min_ram/min_disk vs flavor).
- Integration with simulated long lists & transient failures (retry/backoff).

**Acceptance Criteria**
- All actions return request IDs and accurate status transitions; wizard prevents invalid combos.

**Codex prompts**
```
Add Compute & Images screen, lists+details+actions, with tests. Implement a minimal Launch wizard with validation and quota preview.
```

---

## M4 — Network

**Deliverables**
- Networks, subnets, routers, ports, floating IPs, security groups (+rules), trunks.
- **VPC‑like wizard**; **Security hardening** templates; optional ASCII topology mini‑map.

**Tests**
- SG diff engine; idempotent templates; FIP association flows; rollback on wizard failure.

**Acceptance Criteria**
- Create a VPC‑like setup in ≤ 90s with defaults; traffic e2e verified in tests.

---

## M5 — Block Storage

**Deliverables**
- Volumes, types, snapshots, backups (if enabled).
- Actions: create/extend/retype (migration policy), attach/detach, snapshot/backup; from image/snapshot.

**Tests**
- Retype safety checks; extend constraints; backup gating.

**Acceptance Criteria**
- Retype preserves data; rollback on policy denial is clear and safe.

---

## M6 — Object Storage (Swift)

**Deliverables**
- Dual‑pane browser: containers ↔ objects; upload/download; metadata; Temp URLs; CORS.

**Tests**
- Large listings & prefix filters; metadata persistence; Temp URL generation edge cases.

---

## M7 — Load Balancers (Octavia)

**Deliverables**
- LBs, listeners, pools, members, health monitors, L7 rules.
- **End‑to‑end wizard** (TLS via Barbican); **rolling rotation** helper.

**Tests**
- Wizard previews and final SERVING state; drain/update/undrain sequence correctness.

---

## M8 — Stacks (Heat)

**Deliverables**
- Tree view, parameters/outputs, **template editor**, **validate**, **preview**, **update**.
- Failed resource triage; jump to underlying resources.

**Tests**
- `stack preview` diff parsing; editor validation feedback.

---

## M9 — Telemetry

**Deliverables**
- Detect Ceilometer/Gnocchi/Monasca; **sparklines**; **alarm wizard**.

**Tests**
- Adapter fallback when metrics missing; alarm creation happy/edge flows.

---

## M10 — Reports & Recipes

**Deliverables**
- Inventory export (CSV/JSON); Orphan cleanup (with confirmation); Tag compliance.
- Recipes (Jinja2) MVP; save Launch as recipe; basic Git ops (commit/branch/diff).

**Tests**
- Export schema; recipe replay idempotency on a clean project.

---

## M11 — AI Assistant (feature‑flagged)

**Deliverables**
- Ask/Compose/Advise modes with **schema‑gated** outputs (no direct execution).
- Optional Plan mode with **preflight + dry‑run + approvals**.

**Tests**
- Schema validation; unknown actions ignored; privacy redaction tested.

---

## Cross‑cutting: Quality gates & governance

- **Definition of Done (per milestone)**
  - Tests passing (unit/integration); coverage at or above target.
  - Lint + type checks pass locally and in CI.
  - User docs updated (README/Docs).
  - Release notes/changelog updated.

- **Branching & reviews**
  - Trunk‑based, PRs from feature branches, squash merge, CODEOWNERS for reviews.
  - Labels: `area:*`, `type:*`, `priority:*`, `good-first-issue`, `blocked`, `help-wanted`.

- **Risk controls**
  - Capability gating blocks unavailable features (tests for “no Octavia”, “no telemetry”).
  - Secrets never logged; redaction helpers; TLS verify on.
  - Pagination + incremental render to prevent UI stalls.

---

## Ready‑to‑run helper commands

```bash
# Run quality gates locally
pre-commit run --all-files
mypy os_tui
pytest -q

# Build & run entrypoint (UI lands in M2)
python -m os_tui
ostui --help  # once console script is wired
```

---

## Appendix — Issue bootstrap (optional)

Use a small bash script with GitHub CLI to create labels and issues for M0/M1. Keep it idempotent, and run:
`chmod +x tools/bootstrap_issues.sh && ./tools/bootstrap_issues.sh`

---

## **Quickstart**

Quickstart assumes you want a **local‑first → create remote from source** workflow (recommended). A note for the remote‑first flow is at the end.

---

### **0\) Prereqs (one‑time on your machine)**

`gh auth status                    # GitHub CLI logged in`
`git config --global init.defaultBranch main`
`python3 --version                 # Prefer 3.12`
`codex --version                   # Codex CLI installed & signed in`

---

### **1\) Create the repo locally and seed docs**

`mkdir -p ~/code/os-tui && cd ~/code/os-tui`

`# Add your docs now so the first commit includes them:`
`cp /path/to/PRD.md .`
`cp /path/to/WORKPLAN.md .`

Create a **.gitignore** up front (prevents the venv from ever being tracked):

`cat > .gitignore <<'EOF'`
`# Python artifacts`
`__pycache__/`
`*.py[cod]`
`*.pyo`
`*.pyd`
`*.so`
`*.egg-info/`
`.eggs/`
`.build/`
`dist/`
`build/`
`.mypy_cache/`
`.ruff_cache/`
`.pytest_cache/`
`.coverage`
`htmlcov/`

`# Environments`
`.venv/`
`venv/`
`.env/`
`.tox/`

`# Editors/OS`
`.DS_Store`
`.idea/`
`.vscode/`
`EOF`

Initialize and commit:

`git init`
`git add PRD.md WORKPLAN.md .gitignore`
`git commit -m "docs: add PRD and work plan (v0.1)"`

---

### **2\) Create the GitHub repo from this source**

`gh repo create kriscelmer/os-tui --public --source=. --remote=origin --push`

---

### **3\) Scaffold the project with Codex (files only)**

Codex edits files in your current directory. We’ll run shell commands (venv, pre‑commit) **manually** for reliability.

`codex --model gpt-5-codex \`
  `"Add pyproject.toml (python 3.12), dependencies textual, openstacksdk, pytest, ruff, mypy, pre-commit.`
   `Create .github/workflows/ci.yml (lint, typecheck, tests).`
   `Scaffold package dirs os_tui/{core,sdk,store,ui} and tests/ with a sample test."`

Review diffs with `git status` / `git diff`.

---

### **4\) Create a virtualenv and install dependencies**

`python3 -m venv .venv`
`# macOS/Linux:`
`source .venv/bin/activate`
`# Windows PowerShell:`
`# .\.venv\Scripts\Activate.ps1`

`python -m pip install -U pip setuptools wheel`
`# If pyproject defines dev extras, prefer them:`
`pip install -e ".[dev]" || pip install textual openstacksdk pytest ruff mypy pre-commit`

---

### **5\) Add pre‑commit configuration (before installing hooks)**

Create **.pre-commit-config.yaml** with official hooks for ruff & mypy and project‑scoped file patterns:

`# .pre-commit-config.yaml`
`exclude: ^(\.venv|venv|\.tox|build|dist|\.mypy_cache|\.ruff_cache|node_modules)/`

`default_language_version:`
  `python: python3.12`

`repos:`
  `- repo: https://github.com/pre-commit/pre-commit-hooks`
    `rev: v4.6.0`
    `hooks:`
      `- id: end-of-file-fixer`
      `- id: trailing-whitespace`
      `- id: check-yaml`
      `- id: check-toml`

  `- repo: https://github.com/astral-sh/ruff-pre-commit`
    `rev: v0.6.9`
    `hooks:`
      `- id: ruff`
        `args: [--fix]`
        `files: ^(os_tui|tests)/`
      `- id: ruff-format`
        `files: ^(os_tui|tests)/`

  `- repo: https://github.com/pre-commit/mirrors-mypy`
    `rev: v1.11.2`
    `hooks:`
      `- id: mypy`
        `pass_filenames: false`
        `args: [--config-file, mypy.ini, os_tui, tests]`
        `additional_dependencies:`
          `- typing-extensions==4.12.2`
          `- mypy-extensions==1.0.0`

Add minimal tool configs (if not already present):

**`pyproject.toml` (ruff section)**

`[tool.ruff]`
`line-length = 100`
`target-version = "py312"`
`extend-exclude = [".venv", "venv", ".tox", "build", "dist", ".mypy_cache", ".ruff_cache", "node_modules"]`

`[tool.ruff.lint]`
`select = ["E", "F", "I"]  # pycodestyle errors, pyflakes, isort`

**`mypy.ini`**

`[mypy]`
`python_version = 3.12`
`warn_unused_ignores = True`
`disallow_untyped_defs = True`
`no_implicit_optional = True`
`check_untyped_defs = True`
`strict_equality = True`
`ignore_missing_imports = True`

`[mypy-tests.*]`
`disallow_untyped_defs = False`

---

### **6\) Install and run pre‑commit hooks (manual; not via Codex)**

`pre-commit install`
`pre-commit run -a || true     # first run may reformat files; re-run if needed`

If you ever accidentally tracked `.venv`, remove it:

`git rm -r --cached .venv || true`

---

### **7\) Run tests and push**

`pytest -q`
`git add -A`
`git commit -m "chore: scaffold project (pyproject, CI, tooling, skeleton)"`
`git push`

---

### **8\) (Optional) Convenience Makefile**

`# Makefile`
`.PHONY: venv deps lint type test precommit all`
`venv:`
	`python3 -m venv .venv`
	`. .venv/bin/activate && python -m pip install -U pip setuptools wheel`
`deps:`
	`. .venv/bin/activate && pip install -e ".[dev]" || pip install textual openstacksdk pytest ruff mypy pre-commit`
`lint:`
	`. .venv/bin/activate && ruff check os_tui tests`
`type:`
	`. .venv/bin/activate && mypy --config-file mypy.ini os_tui tests`
`test:`
	`. .venv/bin/activate && pytest -q`
`precommit:`
	`. .venv/bin/activate && pre-commit install && pre-commit run -a`
`all: venv deps precommit test`

---

## **Alternative: Remote‑first flow (note)**

If you prefer `gh repo create --clone`:

`gh repo create kriscelmer/os-tui --public --clone`
`cd os-tui`
`cp /path/to/PRD.md .`
`cp /path/to/WORKPLAN.md .`
`# Add .gitignore now (same contents as above)`
`git add PRD.md WORKPLAN.md .gitignore`
`git commit -m "docs: add PRD and work plan (v0.1)"`
`git push`

`# Then proceed with steps 3→7 exactly as above.`

---

## **Troubleshooting (common)**

* **Ruff error `--force-exclude cannot be used multiple times`:**
   Remove `--force-exclude` from hook args; the wrapper already adds it.

* **Mypy `Duplicate module named "os_tui"`:**
   Ensure `pass_filenames: false` and specify targets in `args: […, os_tui, tests]`.

* **Tooling scans `.venv` or site‑packages:**
   Confirm `.venv/` is in `.gitignore`, **not tracked** (`git ls-files .venv` → no output), and that your pre‑commit `files:` patterns restrict hooks to `os_tui/` and `tests/`.
