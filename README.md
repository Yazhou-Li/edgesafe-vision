# EdgeSafe Vision

> Edge AI safety monitoring reference implementation for multi-camera environments.

EdgeSafe Vision is an open-source reference project extracted from real-world edge AI delivery experience. It focuses on the engineering path from **camera input → AI events → business rules → alarms → operator workflow**, rather than on training a new vision model from scratch.

## What this project aims to cover

- Multi-camera RTSP integration
- Frigate / OpenVINO based edge inference integration
- Occupancy / overcrowding rules
- Restricted-zone intrusion rules
- Fire / smoke event integration
- Alarm snapshots and alarm lifecycle
- Local voice alerts
- Windows / Ubuntu deployment diagnostics
- Health checks and acceptance checklists

## Project status

This repository is currently being prepared as a **sanitized Community Edition**.

The original production project contains customer-specific configuration, credentials, commercial licensing components, runtime data and deployment details. Those materials will **not** be published directly. Public code will be extracted into a clean repository after security and privacy review.

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

## Open-source scope

The Community Edition is intended to include reusable, non-customer-specific capabilities such as:

- rule engine examples
- sanitized configuration examples
- camera / event integration examples
- deployment diagnostics
- troubleshooting guides
- acceptance checklists
- demo data and reproducible test scenarios

## Commercial scope

Some enterprise capabilities are intentionally kept outside the public repository, including:

- commercial license / activation infrastructure
- private keys, signing keys and device authorization logic
- customer-specific deployment packages
- fleet / multi-site administration
- proprietary operations tooling
- paid support, deployment and SLA services

See [docs/COMMERCIAL.md](docs/COMMERCIAL.md).

## Security and privacy

Never commit real production secrets or customer data to this repository.

Examples of prohibited content:

- camera usernames / passwords
- RTSP URLs containing credentials
- real customer IP addresses
- tokens or activation credentials
- private keys or certificates
- production license files
- device fingerprints tied to a customer
- customer screenshots or alarm history
- production `data.json`
- trusted-time files
- runtime logs containing sensitive data

See [SECURITY.md](SECURITY.md).

## Why this project exists

This project is intended to turn practical edge-AI delivery experience into reusable engineering assets for developers, FDEs, solution engineers and implementation teams.

The focus is on making edge vision systems easier to **deploy, diagnose, operate and validate in real environments**.

## Roadmap

- [ ] Publish sanitized architecture and configuration examples
- [ ] Publish occupancy-rule reference implementation
- [ ] Publish zone-intrusion reference implementation
- [ ] Publish Linux diagnostic script
- [ ] Publish Windows diagnostic script
- [ ] Add reproducible demo environment
- [ ] Add regression tests for alarm lifecycle
- [ ] Add deployment and acceptance documentation

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

Community Edition code is intended to be released under the Apache License 2.0 unless otherwise noted. Third-party components retain their original licenses.

---

**Maintainer:** Yazhou-Li  
**Repository owner:** [Yazhou-Li](https://github.com/Yazhou-Li)
