# Contributing

Thanks for your interest in EdgeSafe Vision.

If you are using a coding agent, read [AGENTS.md](AGENTS.md) before making changes. It contains the repository's operational boundaries, validation commands, and privacy rules.

The project favors small, evidence-driven contributions that make edge-AI systems easier to deploy, diagnose, operate, and validate.

## Good contribution areas

- edge deployment diagnostics
- camera health checks
- Frigate / MQTT / webhook adapters
- event processing
- occupancy rules
- restricted-zone rules
- alarm lifecycle tests
- Linux / Windows deployment guides
- privacy-preserving demo data
- reproducible bug reports

## Development setup

```bash
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
cd edgesafe-vision
python -m pip install -e .
python -m unittest discover -s tests -v
```

The public reference modules intentionally keep dependencies light so contributors can run the core tests without a GPU or production camera.

## Before submitting code

1. Remove all customer-specific data.
2. Do not include secrets, tokens, passwords, private keys, certificates, or license files.
3. Do not include production RTSP URLs, private deployment addresses, screenshots, or real alarm history.
4. Prefer small, focused pull requests.
5. Include a reproducible test or validation step when possible.
6. Keep public APIs and examples customer-agnostic.
7. Update docs when behavior or usage changes.

## Bug reports

Use the repository bug-report form. A useful report should include:

- affected area
- version or commit
- environment
- expected behavior
- observed behavior
- minimal reproduction
- sanitized evidence
- regression test if available

## Feature requests

Strong feature requests describe:

- the operational problem;
- a reusable use case;
- the proposed capability;
- acceptance criteria;
- alternatives considered.

Product-specific customizations are usually better expressed as adapters or extension points rather than hard-coded core behavior.

## Agent Skill contributions

Agent Skills must remain small, portable, and evidence-driven.

- keep the required `SKILL.md` metadata valid and aligned with the parent directory name;
- prefer reusable procedures over one-off prompts;
- never bundle customer credentials, private endpoints, production payloads, or site-specific secrets;
- put detailed playbooks in `references/` and reusable templates in `assets/` instead of bloating the main skill;
- use synthetic examples and make every external side effect explicit.

## Pull requests

Before opening a PR:

```bash
python -m unittest discover -s tests -v
```

If behavior changes, add a regression test. If a field-deployment behavior cannot be fully automated, document the manual acceptance evidence required.

## Engineering principle

This project values **observable evidence over assumptions**.

A process starting successfully is not the same as a feature working for an operator. Validation should be based on real outputs, logs, deterministic tests, and reproducible behavior.
