# Contributing

Thanks for your interest in EdgeSafe Vision.

## Good contribution areas

- edge deployment diagnostics
- camera health checks
- event processing
- occupancy rules
- restricted-zone rules
- alarm lifecycle tests
- Linux / Windows deployment guides
- privacy-preserving demo data
- reproducible bug reports

## Before submitting code

1. Remove all customer-specific data.
2. Do not include secrets, tokens, passwords, private keys or license files.
3. Do not include production screenshots or real alarm history.
4. Prefer small, focused pull requests.
5. Include a reproducible test or validation step when possible.

## Bug reports

A useful issue should include:

- environment
- expected behavior
- observed behavior
- minimal reproduction
- sanitized logs
- root-cause evidence if known
- regression test if available

## Engineering principle

This project values **observable evidence over assumptions**.

A process starting successfully is not the same as a feature working for an operator. Validation should be based on real outputs, logs and reproducible behavior.
