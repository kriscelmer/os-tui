# OS‑TUI — Product Requirements Document (PRD)
**Version:** 0.1
**Date:** October 30, 2025
**Author:** Kris Celmer & contributors
**Status:** Draft for discussion

---

## 1) Executive Summary

OS‑TUI is a **keyboard‑first, text‑based console** for OpenStack **project operators**. It provides fast inventory views, safe, guided actions, and wizards across Compute, Network, Storage, Object Storage, Load Balancing (Octavia), and Orchestration (Heat). OS‑TUI reads the **service catalog** and **capabilities** at runtime to enable only what is available in the target cloud. It aims to be **functionally equivalent** to Horizon/Skyline for project‑scope tasks, but optimized for **speed, repeatability, and automation** from the terminal. A later‑stage **AI Assistant** (feature‑flagged, off by default) adds explainable advice and plan generation—never silent automation.

**Design tenets**
- **Keyboard‑first** UX with discoverable hotkeys and a function‑key bar
- **Service‑aware**: enable/disable screens and actions based on Keystone catalog and microversions
- **Safe by default**: confirmations, previews, dry‑runs when feasible
- **Extensible**: plugin architecture (stevedore), screen/action add‑ons
- **Telemetry‑aware**: show metrics when available; degrade gracefully when not
- **Explainable**: surface RBAC denials, request IDs, and raw error bodies on demand

---

## 2) Problem Statement & Goals

### Problems
- Operators oscillate between **raw CLIs** (fast, fragmented) and **web GUIs** (visual, click‑heavy).
- Common tasks—**triage**, **bulk operations**, **repeatable deployments**, **policy compliance**—are cumbersome to perform and audit.
- Heterogeneous cloud deployments and microversions cause **feature ambiguity**.

### Goals
- Deliver a **fast, service‑aware, keyboard‑driven** TUI for project operations.
- Provide **guided wizards** and **recipes** for “cattle over pets,” drift control, and day‑2 work.
- Make **RBAC and capability constraints visible**; reduce trial‑and‑error.
- Provide **observability** (if telemetry exists) with pragmatic fallbacks.
- Establish a **plugin architecture** for optional services (Designate, Magnum, Barbican, etc.).
- (Later) Add **AI‑assisted advice and plan generation** with strict safety rails.

---

## 3) Personas

- **Project Operator (primary)** — Manages instances, networks, volumes, stacks, LBs for their project.
- **Power User / SRE** — Bulk operations, hygiene/cleanup, scripting, runbooks, Git workflows, drift control.
- **Cloud Support Engineer (read‑mostly)** — Investigates states, gathers evidence (logs/events/metrics), suggests or enacts approved fixes.

---

## 4) Scope

### In Scope (MVP → later phases)
- **Auth** via env vars, `clouds.yaml`, or prompted input with secure local save.
- **Service discovery** & **capability gating** (Keystone catalog + microversions).
- Screens: **Overview**, **Compute & Images**, **Network**, **Block Storage**, **Object Storage (Swift)**, **Load Balancers (Octavia)**, **Stacks (Heat)**, **Telemetry** (if present), **Identity**, **Reports**, **Automations (Recipes)**, **Settings**.
- **CRUD and actions** per resource with confirmations; **dry‑runs** where feasible.
- **Wizards** for common multi‑step tasks (launch instance, VPC‑like network, LB end‑to‑end, Heat template edit/validate/preview).
- **Exports** (CSV/JSON) and **orphan cleanup** workflows.
- **Recipes & VCS** integration (Jinja2 + Git) to convert interactive sequences into repeatable artifacts.
- **Accessibility** (color‑blind palette), **keyboard discoverability**, **high‑contrast/no‑color** modes.

### Out of Scope (initially)
- Cloud‑admin features (hypervisors, host aggregates mgmt).
- Autonomous “self‑healing.”
- Detailed cost/billing unless CloudKitty is present (later).

---

## 5) Assumptions & Constraints

- Terminal size **≥ 33×120**; multi‑color preferred; mouse optional.
- Python 3.11+; platforms: Linux/macOS/WSL.
- Primary API client: **openstacksdk**; avoid shelling to `openstack` CLI.
- Networks may be **air‑gapped**; telemetry may be absent.
- Users may have **limited RBAC**; UI must surface policy denials clearly.

---

## 6) Success Metrics (KPIs)

- **Time‑to‑task** reduction vs. Horizon for top‑10 workflows (target: −40%).
- **Action failure rate** due to RBAC/feature mismatch (target: <3% after first release).
- **Plan/recipe reuse** rate (target: ≥30% launches via saved recipes by Phase 3).
- **Operator satisfaction** (CSAT ≥ 4.4/5 after 60 days).

---

## 7) UX Principles & Navigation

- **Keyboard‑first**; command palette (`Ctrl+P`), function‑key bar.
- **Two‑pane** layout: **List** (left) + **Details** (right); bottom action bar.
- **Predictable dialogs** for create/edit/confirmations; **scrollable** details.
- **Search/filter** (`/`), multi‑select (`*`), refresh (`R`).

**Default key map** (customizable):
`F1 Help • F2 Actions • F3 View • F4 Edit • F5 Create • F6 Attach/Move • F7 Wizard • F8 Delete • F9 Menu • F10 Quit`

---

## 8) Functional Requirements (by area)

### 8.1 Authentication & Context
- Load from **env**, **clouds.yaml**, or **prompt+save (encrypted)**.
- Profiles & workspaces: multiple clouds/projects/regions; quick switcher.
- Token awareness: show expiry; re‑auth prompt.

### 8.2 Service Discovery & Capability Map
- Build a **CapabilitiesMap** at startup/context‑switch:
  presence of services, negotiated microversions, feature toggles (e.g., Cinder backups, Octavia TLS options, Nova serial console types).
- Gate screens/actions; show **why disabled** (missing service, RBAC, microversion).

### 8.3 Overview
- Quotas vs usage; **hotspots** (largest volumes, busiest instances if metrics).
- **Orphaned resources** (unattached volumes/ports/FIPs).
- Recent events (state changes, stack events), token expiry.
- Quick actions: create instance/network/volume; orphan cleanup wizard.

### 8.4 Compute & Images
- **Instances**: list, filter, tags; details show flavor, image, AZ, IPs, volumes, SGs, metadata, last faults, **console log tail**, **serial console** (if available).
- **Actions**: start/stop/reboot (soft/hard), pause/suspend/resume, shelve/unshelve, rescue/unrescue, snapshot, lock/unlock, attach/detach volume, associate/disassociate FIP, evacuate/migrate/rebuild (guardrails), metadata/tags, download console log, serial console in‑TUI.
- **Launch Wizard**: boot source (image/volume), flavor, AZ, networks/ports (port‑security), SGs, keypair, user‑data, BDM, scheduling hints, tags; **quota/cost preview**; **save as recipe**.
- **Images**: list, properties, visibility, protected flag; upload/import/update metadata.
- **Keypairs/Flavors**: list; basic management.

### 8.5 Network
- Objects: networks, subnets, routers, ports, floating IPs, security groups (+rules), trunks.
- **ASCII topology mini‑map** (collapsible).
- Wizards: **VPC‑like** network; **Security hardening** templates.

### 8.6 Block Storage
- Objects: volumes, types, snapshots, backups (if enabled).
- Actions: create/extend/retype (with migration policy), attach/detach, snapshot/backup, from image/snapshot, encryption metadata.
- Optional: local cron snippets for snapshot/backup retention.

### 8.7 Object Storage (Swift)
- Dual‑pane: containers ↔ objects; upload/download; prefix search; metadata; **Temp URLs**; CORS.

### 8.8 Load Balancers (Octavia)
- LBs, listeners, pools, members, health monitors, L7 rules/policies.
- **End‑to‑end wizard** (VIP → listener/TLS via Barbican → pool → HM → attach members).
- **Rolling rotation** helper (drain → update → undrain).

### 8.9 Stacks (Heat)
- Tree view; parameters/outputs; **template editor** (YAML, inline errors).
- **Validate**, **Preview (stack preview)**, **Update**.
- Failed resource triage; jump to underlying service resources.

### 8.10 Telemetry / Performance
- Detect Ceilometer/Gnocchi/Monasca.
- Per‑instance **sparklines** (CPU/mem/disk/net); alarms list; **create alarm wizard**.
- Fallbacks: Nova diagnostics, console logs.

### 8.11 Identity
- Project, domain, roles; members (read‑only unless permitted); application credentials (if allowed).

### 8.12 Reports
- Inventory export; Orphan finder; Tag compliance (regex + required tags); Trends (if metrics).

### 8.13 Automations (Recipes)
- Parameterized **recipes** (Jinja2) mixing Heat + SDK actions + shell hooks.
- **Macro recording**: capture user session as a replayable recipe.
- **Git** integration: init repo, commit, branch, diff (optional GPG sign).

### 8.14 Settings
- Profiles, keybindings, themes, telemetry adapters, feature flags, privacy toggles.

---

## 9) Non‑Functional Requirements (NFRs)

- **Performance**: cold start to Overview ≤ 3s; first paint ≤ 1.5s for 500‑item lists (incremental).
- **Reliability**: graceful retries/backoff; atomic writes for config.
- **Security**: TLS verification; secrets encrypted at rest; **no secrets in logs**.
- **Accessibility**: high‑contrast, color‑blind palettes, no‑color mode; full keyboard support.
- **Internationalization**: strings externalized (English first).
- **Observability**: structured logs with request IDs; “Copy as curl” for last failing request.

---

## 10) Architecture Overview

- **Language/libraries**: Python 3.11/3.12; **openstacksdk**, **Textual**/**Rich**, **stevedore**, **ruamel.yaml**, **jinja2**, **cryptography**, **keyring**, **pytest**, **ruff**, **mypy**.
- **Modules**:
  - `os_tui.core` — app boot, config, errors, logging.
  - `os_tui.sdk` — connection lifecycle, capability detection, per‑service thin wrappers.
  - `os_tui.store` — per‑screen stores, pagination, polling, caches.
  - `os_tui.ui` — Textual app, widgets, screens, keybar, dialogs.
  - `os_tui.plugins` — entry‑point loaded extensions.
  - `os_tui.telemetry` — adapters (Gnocchi/Monasca/None).
  - `os_tui.recipes` — Jinja2 engine, repo ops, macro recorder.
- **Plugin system**: stevedore entry points for screens/actions.
- **Concurrency**: `asyncio` + limited thread pools; parallel fetch; rate limits.
- **Error handling**: user‑friendly summary + “Details” pane with request IDs & HTTP body.

---

## 11) Data & Object Model (selected)

### 11.1 Resource Wrapper
- Wraps openstacksdk resources to add: derived fields (status chip, human sizes), related IDs, allowed **Actions** with preconditions and rollback hints, export serializers (CSV/JSON).

### 11.2 Recipe schema (simplified)
```yaml
version: 1
name: "launch-web-tier"
parameters:
  image: {{type: string}}
  flavor: {{type: string}}
  count: {{type: integer, default: 2}}
steps:
  - type: heat.stack_deploy
    template: templates/web.yaml
    env: templates/web.env.j2
  - type: sdk.compute.associate_fips
    selector: "tag=web"
    count: 2
```

---

## 12) AI Assistant (Later Stage Feature)

**Positioning:** Optional copilot translating NL requests into **reviewable artifacts** (filters, CLI/Heat snippets, recommendations, plans). **No autonomous changes** without explicit approvals.

**Modes:** Ask (Q&A), Compose (generate CLI/Heat/recipe; copy‑only), Advise (structured recommendations), Plan (multi‑step plan with dry‑run, preflight, and approvals).

**Safety:** Local models by default; remote only with opt‑in and **redaction**. Tool‑mediated actions only; whitelisted schemas; bounded blast radius; audited like manual actions.

**Recommendation schema (example)**
```json
{
  "id": "REC-001",
  "title": "Right-size instance web-02",
  "severity": "medium",
  "confidence": 0.78,
  "rationale": "CPU 95p 92%/7d; mem 42%",
  "impact": {"quota": {"vcpus": 2}, "cost_hint": "+$12/mo"},
  "preconditions": ["server.status in ['SHUTOFF','ACTIVE']"],
  "actions": [{"type": "nova.resize", "params": {"server_id": "web-02", "flavor": "m1.medium"}}],
  "rollback": [{"type": "nova.resize_revert", "params": {"server_id": "web-02"}}],
  "evidence_refs": ["metric:cpu.95p:7d", "nova:server-show:web-02"]
}
```

---

## 13) Feature Flags

- `telemetry.enabled` (`auto|on|off`)
- `octavia.enabled` (`auto|on|off`)
- `heat.editor.enabled` (default `on`)
- `recipes.enabled` (default `on`)
- `ai.enabled` (default `off`)
- `offline_cache.enabled` (default `off`)

---

## 14) Security

- Secrets via OS keyring if available; else encrypted local file (Fernet with passphrase).
- **Never** log secrets; redact tokens/IPs in copyable logs (toggle to show).
- Validate TLS; allow user‑supplied CA.
- Clipboard hygiene for IDs/IPs (configurable timeout).
- RBAC transparency: show policy rule names on 403 with suggestions.

---

## 15) Packaging & Distribution

- `pipx install os-tui` in dev; release as PyPI package.
- Optional single‑file binaries (PyInstaller) for Linux/macOS.
- Optional container image for controlled environments.
- Config home: `~/.ostui/`.

---

## 16) Rollout Plan & Milestones (with Acceptance Criteria)

- **M0 Bootstrap** — repo, CI, tooling, docs green.
- **M1 Core** — config/auth/service discovery; 90%+ unit coverage for core.
- **M2 Overview** — quotas/usage/orphans/events; snapshot tests.
- **M3 Compute & Images** — lists, details, core actions, Launch wizard; preflight & friendly errors.
- **M4 Network** — CRUD + VPC‑like wizard; SG templates.
- **M5 Block Storage** — CRUD + retype/extend; snapshot/backup flows.
- **M6 Object Storage (Swift)** — dual‑pane browser + metadata + temp URLs.
- **M7 Octavia** — E2E LB wizard + rotation helper.
- **M8 Heat** — tree + editor + validate + preview + update.
- **M9 Telemetry** — adapter(s) + sparklines + alarm wizard.
- **M10 Reports & Recipes** — inventory export + orphan cleanup + recipe save/replay; Git ops.
- **M11 AI Assistant (feature‑flagged)** — advise/compose schemas + viewer; plan mode with preflight/dry‑run/approvals.

Each milestone includes: **tests** (unit/integration), **docs**, and **release notes**.

---

## 17) Test Strategy

- **TDD**: write tests first.
- **Unit tests** for config, capability detection, stores, adapters (≥ 85% coverage for new modules).
- **Integration tests**: DevStack or recorded fixtures; policy denials; microversion variance.
- **Property tests**: quota math, SG diffs.
- **Performance**: large projects (e.g., 10k ports).
- **Security**: ensure secrets never log; verify redaction helpers.
- **AI regression** (later): schema adherence; deterministic tool stubs.

---

## 18) Risks & Mitigations

- **Service heterogeneity** → strict capability detection; feature flags; microversion badges.
- **RBAC surprises** → policy rule display + safer alternatives.
- **Telemetry variance** → adapters with graceful degradation.
- **Terminal constraints** → collapsible panes; pop‑out details.
- **AI hallucinations** → schema‑gated outputs; no silent exec; whitelisted tool calls only.

---

## 19) Open Questions

1. Ship local **SQLite cache** for offline read‑only mode in Phase 2–3?
2. Which **default SG templates** ship vs. org‑supplied?
3. Support **application credentials** creation at MVP?
4. Scope of **cost approximation** without CloudKitty (configurable rate sheet)?
5. Preferred **license** (Apache‑2.0 recommended).

---

## 20) Glossary

- **Recipe** — Parameterized, versioned set of actions (Heat + SDK + hooks).
- **CapabilitiesMap** — Runtime‑detected set of supported services/features/microversions.
- **Plan** — Multi‑step, approval‑gated change set (AI Assistant, later).

---

### Appendix A — ASCII Wireframe (Instances)

```
┌ Project: my-tenant  Region: GRA1  User: alice                    Token: 47m ┐
│ [F1]Help [F2]Actions [F3]View [F4]Edit [F5]Create [F7]Wizard [F9]Menu [F10] │
├ Overview | Compute & Images | Network | Block Storage | LB | Stacks | Tele… │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Instances (20)           │ Instance: web-01 (ACTIVE)                        │
│ > web-01                 │ Flavor: m1.small  Image: ubuntu-22.04            │
│   web-02                 │ AZ: nova  Keypair: alice                          │
│   api-01                 │ IP: 10.0.1.12 / 203.0.113.10 (floating)          │
│ [/] filter  [*] multi    │ Volumes: vol-123 (boot, 20G)                      │
│                          │ SGs: default, http-open                           │
│                          │ CPU: ▄▄▄▄▆▇█▇▆▅ (15m)  Net: ⇡12 Mb/s ⇣18 Mb/s     │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

### Appendix B — Config Precedence

1. CLI flags (future) →
2. `OS_CLOUD` or classic `OS_…` env vars →
3. `clouds.yaml` (default or user‑specified path) →
4. Interactive prompt (with secure save option).

### Appendix C — Example Orphan Cleanup Flow (Acceptance Test)

**Given** unattached volumes `v-1`, unused FIPs `fip-1`, SGs without ports `sg-z`.
**When** Overview → Orphan Cleanup Wizard → select `v-1` and `fip-1` → confirm.
**Then** Preview shows `DELETE v-1`, `RELEASE fip-1`; request IDs logged; final status “completed.”
