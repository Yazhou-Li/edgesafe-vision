# AGENTS.md

This file is the working contract for coding agents contributing to EdgeSafe Vision.

## Mission

Improve reusable, verifiable edge-AI delivery engineering: diagnostics, event normalization, rules, alarms, deployment guidance, tests, and privacy-preserving examples.

The repository is not a customer deployment dump, a generic AI playground, or a certified life-safety product.

## Read first

Before changing code, read:

1. `README.md`
2. `CONTRIBUTING.md`
3. `SECURITY.md`
4. the relevant file under `docs/`
5. the Issue or PR that defines the requested scope

For deployment-diagnosis tasks, also read:

- `.agents/skills/edge-ai-deployment-doctor/SKILL.md`

## Non-negotiable boundaries

- Never add real passwords, API keys, private keys, tokens, certificates, license files, or customer credentials.
- Never add production RTSP URLs, private IP addresses, customer screenshots, real alarm history, or private deployment identifiers.
- Use synthetic or clearly sanitized examples only.
- Do not weaken security or privacy controls just to make a demo pass.
- Do not claim a feature is validated unless there is observable evidence: tests, logs, deterministic output, or documented acceptance steps.
- Do not present this repository as a certified safety system.
- Keep core modules dependency-light unless the change clearly justifies a new dependency.
- Keep changes narrowly scoped. Prefer one reusable fix over a broad rewrite.

## Engineering style

The project values:

- evidence over assumptions;
- delivery behavior over demo behavior;
- deterministic tests over manual confidence;
- explicit state transitions over hidden side effects;
- small adapters and extension points over customer-specific branches;
- cross-platform behavior where practical.

When fixing a bug, first reproduce it with the smallest safe example. Then add or update a regression test when feasible.

## Validation

From the repository root:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

For focused work, run the smallest relevant test first, then the full suite before claiming completion.

Examples:

```bash
python -m unittest tests.test_doctor -v
python -m unittest tests.test_agent_skill -v
```

If a change affects documentation or an example, verify paths and commands against the current repository layout.

## EdgeSafe Doctor changes

`edgesafe-doctor` is read-only by design.

A diagnostic check should:

- make one bounded observation;
- return a clear PASS, WARN, or FAIL result;
- avoid collecting secrets by default;
- redact credentials/query data from labels where appropriate;
- avoid mutating services or configuration;
- be testable without production infrastructure whenever possible.

Do not turn diagnosis into remediation unless the Issue explicitly scopes a separate, user-approved action.

## Adapter changes

Adapters normalize external detector/event payloads into the repository's public event contract.

They should:

- accept only documented input shapes;
- reject malformed input with explicit errors;
- avoid opening network connections in the core adapter itself unless the module is explicitly a transport;
- use synthetic fixtures in tests;
- avoid leaking transport-specific behavior into the normalized event model.

## Agent Skill changes

Agent Skills must follow the current `SKILL.md` structure used in this repository.

- The `name` must match the parent directory.
- The `description` must state what the skill does and when to use it.
- Put detailed procedures in `references/` when the main skill would become bloated.
- Put reusable templates/config examples in `assets/`.
- Keep examples synthetic.
- A Skill should encode a repeatable workflow, not a long one-off prompt.

## Pull-request standard

A good PR should make it easy to answer:

1. What real problem does this solve?
2. Why is the change reusable?
3. What changed?
4. How was it verified?
5. What was intentionally left out?
6. Does the change preserve privacy and safety boundaries?

If the requested change is ambiguous, prefer a small, reviewable interpretation and state the assumption instead of expanding scope silently.
