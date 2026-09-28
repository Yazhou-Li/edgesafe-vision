# EdgeSafe Vision

> Edge AI safety monitoring and alerting reference platform for real-world multi-camera deployment.

EdgeSafe Vision is an open-source project maintained by **Yazhou Li**. It turns practical edge-AI delivery experience into reusable engineering assets for developers, FDEs, solution engineers and implementation teams.

The project focuses on the full delivery path:

**camera input → inference → events → business rules → alarms → operator feedback → acceptance**

rather than on training a vision model from scratch.

## Highlights

- Multi-camera RTSP integration patterns
- Frigate / OpenVINO edge inference integration
- Occupancy / overcrowding rules with persistence and cooldown
- Restricted-zone intrusion rule design
- Video / AI metadata freshness and temporal-skew checks
- Explicit alarm lifecycle
- Windows / Ubuntu deployment diagnostics
- Reboot / persistence / acceptance thinking for field delivery
- Sanitized field notes based on real delivery lessons
- Automated tests and CI

## Current modules

The repository contains working, customer-agnostic reference code:

- `src/edgesafe/rules.py` — occupancy / overcrowding state engine
- `src/edgesafe/zones.py` — normalized polygon zone-intrusion engine
- `src/edgesafe/freshness.py` — video / AI metadata freshness and temporal-skew monitor
- `src/edgesafe/alarms.py` — explicit alarm lifecycle model
- `src/edgesafe/events.py` — normalized detector-agnostic event contract
- `src/edgesafe/doctor.py` — dependency-free cross-platform diagnostic CLI
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
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/demo.py
edgesafe-doctor --http http://127.0.0.1:5000
```

The examples are synthetic and do not contain production credentials, customer data or private deployment material.

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

## Engineering principles

**Evidence over assumptions.** A process starting successfully is not the same as an operator receiving the expected result.

**Delivery over demos.** Edge AI is useful only when streams, rules, alerts, audio, authentication and reboot behavior work together.

**Safe by default.** Production data is never copied directly into this repository.

## Security

Please do not publish credentials, personal data, private deployment details or other secrets in issues, logs, examples or pull requests.

For vulnerability reporting and safe disclosure guidance, see [SECURITY.md](SECURITY.md).

## Field notes

The public field notes explain representative deployment problems—such as video/AI freshness, desktop audio, authentication persistence and acceptance testing—without exposing customer assets.

Read: [From Camera Feed to Verifiable Alarm Workflow](docs/CASE_STUDY.md).

## Support

Contributions are welcome through pull requests. For deployment, integration or support options, see [SUPPORT.md](SUPPORT.md).

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

## License

Apache License 2.0. Third-party components retain their original licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

**Maintainer:** Yazhou Li  
**GitHub:** [github.com/Yazhou-Li](https://github.com/Yazhou-Li)
