# Changelog

All notable public changes to EdgeSafe Vision are documented here.

## [Unreleased]

### Added

- structured bug-report and feature-request forms
- pull-request privacy and validation checklist
- practical getting-started guide
- occupancy / overcrowding rule engine
- zone-intrusion rule engine
- video / AI metadata freshness monitor
- alarm lifecycle model
- normalized edge-event contract
- Frigate tracked-object and camera-status event adapter
- broker-agnostic normalized MQTT event adapter
- synthetic adapter demo and integration guide
- deterministic end-to-end pipeline demo, JSONL fixture, and regression test
- EdgeSafe Doctor diagnostic CLI
- reusable Doctor JSON check plans, file checks, and structured evidence bundles
- Windows and Linux diagnostic starter scripts
- synthetic demo configuration and event examples
- automated unit tests and GitHub Actions CI
- architecture, acceptance and security documentation

### Changed

- expanded CI coverage across supported Python versions
- improved English and Chinese onboarding for users and contributors
- enriched Python package metadata with project URLs and discovery keywords
- HTTP diagnostic labels now redact URL credentials, query strings, and fragments

### Security

- production credentials, customer data, private keys, license material and
  runtime state are explicitly excluded from the public repository.
- issue and pull-request templates now remind contributors to sanitize
  customer and production data before submission.
