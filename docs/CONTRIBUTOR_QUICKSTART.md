# Contributor Quick Start

A short, focused path to making your first contribution to EdgeSafe
Vision. This is the **first-pr-orientation** document: it assumes you
have never touched the repo and wants you contributing something small,
safe, and reviewable within an hour.

Read it top to bottom the first time; afterwards, use it as a checklist
before you open a pull request.

---

## 1. What this project is (and is not)

EdgeSafe Vision is a set of **reusable, verifiable building blocks** for
edge-AI delivery: event normalization, deterministic rules, alarm
lifecycle, a read-only deployment doctor, and synthetic examples. The
core stays **dependency-light** so a contributor can run every test
without a GPU, a camera, or any network.

It is **not** a customer deployment dump, a generic AI playground, or a
certified life-safety system. Keep that line in view on every PR.

## 2. Five minutes on a fresh clone

From the repository root:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

That second command is the single most important habit in this repo:
**run the suite before you claim anything works.** A process starting
successfully is not the same as a feature working for an operator.

For focused work, run the smallest relevant test first, then the full
suite before you open the PR:

```bash
python -m unittest tests.test_freshness -v   # one module
python -m unittest discover -s tests -v       # everything
```

## 3. How a change flows through the codebase

Adapters, detectors, and transports are **edges** of the system.
Everything normalizes into the durable event / rule / alarm model:

```text
Frigate / MQTT / webhook  (adapters, in src/edgesafe/adapters/)
          ↓
Event + Rule + Occupancy + Restricted-zone model (src/edgesafe/*.py)
          ↓
Alarm lifecycle + deterministic report (alarms.py, doctor.py, freshness.py)
```

Prefer a small **adapter or extension point** over hard-coding one
vendor's behavior into the core. The core must stay
vendor-neutral and deterministic; that is what makes its output
reviewable.

## 4. A small, safe first contribution (worked example)

The best first contribution is one that needs no camera, no network, and
no customer data. A realistic one is adding a **deterministic boundary
test** to an existing pure module.

Worked example — `FreshnessMonitor.report()` for a camera it has never
seen:

```python
# tests/test_freshness.py  (added by this contribution)
def test_unknown_camera_is_not_healthy(self):
    report = self.monitor.report("CAM-NEW", 100.0)
    # No video and no metadata have been observed for this camera yet,
    # so nothing may be asserted as fresh or aligned.
    self.assertFalse(report.video_fresh)
    self.assertFalse(report.metadata_fresh)
    self.assertFalse(report.aligned)
    self.assertFalse(report.healthy)
    self.assertIsNone(report.video_age)
```

Why this is a good first contribution:

- it is **synthetic** — no camera, no RTSP URL, no customer data;
- it is **deterministic** — the same input always yields the same
  report, so it runs on any platform;
- it is **one bounded assertion set** about one narrow behavior
  ("unknown camera ⇒ not healthy"), not a broad rewrite;
- it can be verified with a single command:
  `python -m unittest tests.test_freshness -v`.

That pattern — *pick one narrow behavior, assert exactly what it should
do, and nothing more* — is the shape we want from first contributions.

## 5. Common mistakes when sharing logs and deployment details

This is where most first PRs get rejected. The rules are strict and
come from `AGENTS.md` / `SECURITY.md`:

| Do **not** put in the repo | Why / what to do instead |
|---|---|
| Real passwords, API keys, tokens, private keys, certificates, license files | Never. Use placeholders or omit. |
| Production RTSP URLs, private IPs, deployment hostnames | They leak your network. Use `192.0.2.0/24`-style TEST-NET or obvious `example` hosts. |
| Customer screenshots, real alarm history, private deployment identifiers | Sanitize to synthetic values. The repo ships `examples/` with fake cameras and events for this reason. |
| A failed probe presented as a root-cause claim | Report *what you observed* ("expected X, got Y, stack trace Z"), not *"the cause is …"*. |
| Arbitrary shell execution wired into a config or contract | Probes must be explicit; the doctor is read-only. |
| Weakening a privacy check just to make a demo pass | If a check is too strict for a demo, fix the demo, not the check. |

When you must show a log or a config in a PR or issue, **redact first**:
replace hostnames, keys, and ports with clearly synthetic values, then
paste. If you are unsure whether something is safe to share, ask in the
issue instead.

## 6. Before you open the PR

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Then make sure the PR description can answer:

1. What real delivery problem does this solve?
2. Why is the change reusable (not customer-specific)?
3. What changed?
4. How was it verified? (a command + its observed result)
5. What was intentionally left out?
6. Does it preserve the privacy and read-only boundaries above?

If the requested behavior is ambiguous, make the **smallest reviewable
interpretation** and say so in the description.
