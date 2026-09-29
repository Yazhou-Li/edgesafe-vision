# Reproducible Showcase

This walkthrough is for reviewers, contributors, and engineers who want to understand EdgeSafe Vision in about three minutes without a camera, GPU, MQTT broker, or production credential.

The goal is not to simulate a full production site. The goal is to demonstrate the project's core engineering idea:

> **A useful AI delivery is a verifiable chain from input to operator outcome, not just a model prediction.**

## 1. Install and verify

```bash
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
cd edgesafe-vision
python -m pip install -e .
python -m unittest discover -s tests -v
```

A green test run verifies the public deterministic modules and examples against the current repository state.

## 2. Run the end-to-end synthetic pipeline

```bash
python examples/end_to_end_demo.py
```

The demo executes this real code path:

```text
synthetic event
  → normalized EdgeEvent
  → occupancy rule
  → alarm lifecycle
  → deterministic trace
```

The included fixture contains eight events. The expected summary is:

```text
SUMMARY events=8 alarms_opened=2 alarms_resolved=1
```

Why this matters: the demo proves persistence, trigger, cooldown/recovery behavior, and alarm state transitions without pretending that a single detector output is a finished safety workflow.

## 3. Run a read-only deployment diagnosis

Baseline:

```bash
edgesafe-doctor
```

Reusable check plan + evidence:

```bash
edgesafe-doctor \
  --config examples/doctor.example.json \
  --evidence evidence.json
```

EdgeSafe Doctor performs bounded observations such as platform, disk, HTTP/TCP reachability, and required-file checks. It does **not** restart services or edit configuration.

The evidence bundle intentionally omits the machine hostname and redacts URL credentials, query strings, and fragments from diagnostic labels. Review evidence before sharing it because operator-supplied paths or endpoints can still contain deployment details.

## 4. Let an Agent follow the same discipline

The repository includes a portable Agent Skill:

```text
.agents/skills/edge-ai-deployment-doctor/
```

The skill tells a skills-compatible agent to:

1. define the expected and observed outcome;
2. run the smallest non-invasive checks;
3. trace source → event → rule → alarm → operator feedback;
4. stop at the first unsupported transition;
5. report evidence and the next verification step instead of guessing a root cause.

Package the skill as a deterministic zip:

```bash
python scripts/package_skill.py \
  .agents/skills/edge-ai-deployment-doctor
```

The archive is written to:

```text
dist/edge-ai-deployment-doctor.zip
```

## 5. What this showcase proves — and does not prove

It **does** demonstrate:

- reusable event normalization;
- deterministic rule behavior;
- alarm lifecycle behavior;
- read-only deployment diagnostics;
- structured evidence;
- an agent-ready operational workflow;
- automated regression tests.

It **does not** claim:

- certification as a life-safety system;
- validation against a particular production camera or customer network;
- that HTTP/TCP reachability proves end-to-end business behavior;
- that a synthetic demo replaces site acceptance testing.

## 6. One-minute explanation

If you only have one minute:

> Most computer-vision demos stop at "the model detected a person." Real delivery fails later: stale streams, event mismatch, persistence rules, restart behavior, alarms that never reach the operator, and weak evidence during troubleshooting. EdgeSafe Vision turns those last-mile problems into reusable rule engines, adapters, diagnostics, acceptance thinking, tests, and an Agent Skill. The synthetic demo is intentionally small so anyone can reproduce the full event → rule → alarm path without private infrastructure.

For deeper details, continue with [Getting Started](GETTING_STARTED.md), [Architecture](ARCHITECTURE.md), and the [field case study](CASE_STUDY.md).
