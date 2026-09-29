# EdgeSafe Vision

[![CI](https://github.com/Yazhou-Li/edgesafe-vision/actions/workflows/ci.yml/badge.svg)](https://github.com/Yazhou-Li/edgesafe-vision/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/Yazhou-Li/edgesafe-vision)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)

> Open-source toolkit for edge AI safety monitoring, alerting, diagnostics, and real-world multi-camera deployment.

EdgeSafe Vision is an open-source project maintained by **Yazhou Li**. It turns practical edge-AI delivery experience into reusable engineering assets for developers, FDEs, solution engineers, integrators, and implementation teams.

The project focuses on the full delivery path:

**camera input → inference → events → business rules → alarms → operator feedback → acceptance**

rather than on training a vision model from scratch.

## Why EdgeSafe Vision exists

Many computer-vision demos stop at "a person was detected." Real deployments still need to answer harder operational questions:

- Is the stream actually fresh?
- Are AI metadata and displayed video still synchronized?
- Should a condition persist for N seconds before an alarm?
- How does an alarm recover after the condition clears?
- Can the system survive restart and preserve configuration?
- Can an operator hear or see the alarm at the endpoint?
- Can a field engineer collect evidence without changing the system?

EdgeSafe Vision packages those "last-mile" engineering problems into reusable code, diagnostics, tests, and acceptance guidance.

## Highlights

- Multi-camera RTSP integration patterns
- Frigate / OpenVINO edge inference integration
- Occupancy / overcrowding rules with persistence and cooldown
- Restricted-zone intrusion rule design
- Video / AI metadata freshness and temporal-skew checks
- Explicit alarm lifecycle
- Detector-agnostic event normalization
- Frigate tracked-object and camera-status MQTT adapters
- Dependency-free, read-only EdgeSafe Doctor CLI with reusable check plans and structured evidence bundles
- Portable Agent Skill for evidence-driven edge-AI deployment diagnosis
- Windows / Ubuntu deployment diagnostics
- Reboot / persistence / acceptance thinking for field delivery
- Deterministic end-to-end synthetic pipeline demo with regression coverage
- Sanitized field notes based on real delivery lessons
- Automated tests and CI across supported Python versions

## Who this is for

EdgeSafe Vision is useful if you are building or delivering:

- edge-AI video analytics;
- smart retail / warehouse / industrial monitoring;
- multi-camera safety or operations workflows;
- Frigate / MQTT / webhook based event pipelines;
- field diagnostics for Windows or Linux edge systems;
- acceptance tests for AI systems that must work beyond the demo.

## Current modules

The repository contains working, customer-agnostic reference code:

- `src/edgesafe/rules.py` — occupancy / overcrowding state engine
- `src/edgesafe/zones.py` — normalized polygon zone-intrusion engine
- `src/edgesafe/freshness.py` — video / AI metadata freshness and temporal-skew monitor
- `src/edgesafe/alarms.py` — explicit alarm lifecycle model
- `src/edgesafe/events.py` — normalized detector-agnostic event contract
- `src/edgesafe/adapters/` — Frigate and broker-agnostic MQTT adapters
- `src/edgesafe/doctor.py` — dependency-free cross-platform diagnostic CLI
- `.agents/skills/edge-ai-deployment-doctor/` — portable Agent Skill for safe, evidence-driven field diagnosis
- `tests/` — regression tests for public reference modules
- `examples/` — runnable demo and sanitized configuration
- `scripts/` — Windows / Linux non-invasive diagnostic starters
- `docs/` — architecture, acceptance, event schema and field notes
- GitHub Actions CI

Chinese introduction: [README_CN.md](README_CN.md)

## Architecture

```text
IP Cameras / RTSP
        ↓
      Frigate
        ↓
 OpenVINO inference
        ↓
    MQTT / Events
        ↓
     Rule Engine
   ├─ Occupancy
   ├─ Zone Intrusion
   ├─ Fire / Smoke
   └─ Camera Health
        ↓
    Alarm Workflow
   ├─ Snapshot
   ├─ Web UI
   ├─ Local Voice
   └─ Recovery
```

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
cd edgesafe-vision
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/demo.py
python examples/adapter_demo.py
python examples/end_to_end_demo.py
edgesafe-doctor --http http://127.0.0.1:5000
edgesafe-doctor --config examples/doctor.example.json --evidence evidence.json
```

For a guided walkthrough, see [Getting Started](docs/GETTING_STARTED.md). For a judge/user-friendly three-minute walkthrough, see [Reproducible Showcase](docs/SHOWCASE.md). For adapter contracts, see [Integrations](docs/INTEGRATIONS.md). For the deterministic end-to-end scenario, see [Reproducible Demo](docs/DEMO.md).


## Agent Skill

EdgeSafe Vision ships a portable [Agent Skills](https://agentskills.io) workflow at
`.agents/skills/edge-ai-deployment-doctor/`.

The skill turns the project's field-diagnostics practice into a repeatable agent workflow:

- start with non-invasive baseline checks;
- collect only the minimum sanitized evidence needed;
- interpret PASS / WARN / FAIL results without guessing;
- separate reachability, configuration, rule, and operator-feedback failures;
- produce a concise handoff with observed evidence, likely fault domain, and next verification step.

It is designed for skills-compatible coding agents and assistants that can read repository files and run local commands. The skill does not grant credentials, bypass access controls, or replace site-specific safety validation.


The examples are synthetic and do not contain production credentials, customer data, or private deployment material.

## Minimal rule example

```python
from edgesafe.rules import OccupancyRule, OccupancyRuleEngine

rule = OccupancyRule(
    rule_id="entrance-overcrowding",
    camera_id="cam-01",
    threshold=4,
    duration_seconds=10,
    cooldown_seconds=60,
)

engine = OccupancyRuleEngine()

print(engine.evaluate(rule, person_count=5, timestamp=0))
print(engine.evaluate(rule, person_count=5, timestamp=10))
```

The caller supplies timestamps, so rule behavior stays deterministic and testable.

## Open-source scope

EdgeSafe Vision focuses on reusable engineering capabilities such as:

- rule engines
- sanitized configuration examples
- normalized event contracts and camera / event adapters
- deployment diagnostics
- troubleshooting guides
- acceptance checklists
- demo data and reproducible test scenarios

See [ROADMAP.md](ROADMAP.md).

## Project status

EdgeSafe Vision is currently an early-stage public toolkit. The existing modules are runnable and tested, but the project is **not** presented as a certified safety product or as a drop-in production system.

For production use, integrators remain responsible for site-specific validation, security, legal requirements, and any mandatory life-safety systems.

## Engineering principles

**Evidence over assumptions.** A process starting successfully is not the same as an operator receiving the expected result.

**Delivery over demos.** Edge AI is useful only when streams, rules, alerts, audio, authentication, and reboot behavior work together.

**Safe by default.** Production data is never copied directly into this repository.

**Small, reviewable changes.** Reusable fixes should be isolated, testable, and easy to validate.

## Security

Please do not publish credentials, personal data, private deployment details, private network information, or other secrets in issues, logs, examples, or pull requests.

For vulnerability reporting and safe disclosure guidance, see [SECURITY.md](SECURITY.md).

## Field notes

The public field notes explain representative deployment problems—such as video/AI freshness, desktop audio, authentication persistence, and acceptance testing—without exposing customer assets.

Read: [From Camera Feed to Verifiable Alarm Workflow](docs/CASE_STUDY.md).

## Community

Contributions are welcome.

- Found a bug? Use the structured bug report form.
- Have a reusable feature idea? Open a feature request.
- Want to contribute code or docs? Read [CONTRIBUTING.md](CONTRIBUTING.md).
- Need deployment or integration help? See [SUPPORT.md](SUPPORT.md).

The project is especially interested in reproducible edge-AI integration patterns, diagnostics, adapters, tests, and privacy-preserving examples.

## License

Apache License 2.0. Third-party components retain their original licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

**Maintainer:** Yazhou Li  
**GitHub:** [github.com/Yazhou-Li](https://github.com/Yazhou-Li)
