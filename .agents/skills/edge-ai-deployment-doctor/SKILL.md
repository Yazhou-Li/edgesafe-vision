---
name: edge-ai-deployment-doctor
description: Diagnose EdgeSafe Vision and similar edge-AI delivery environments using non-invasive health checks, sanitized evidence, and a repeatable triage workflow. Use when an edge-AI deployment, camera/event pipeline, service endpoint, rule chain, or operator alarm path works in a demo but fails, drifts, or becomes uncertain in a real environment.
license: Apache-2.0
compatibility: Requires an EdgeSafe Vision checkout or installed edgesafe-doctor command. Python 3.10+ is recommended. Network probes are read-only but may still touch operator-supplied endpoints.
metadata:
  author: Yazhou Li
  version: "0.1.0"
---

# Edge AI Deployment Doctor

Use this skill to turn a vague field failure into a small set of observable facts and the next safest verification step.

The core rule is: **evidence over assumptions**. A process starting successfully is not the same as an operator receiving the expected result.

## Safety boundaries

- Never ask the user to paste passwords, API keys, private keys, camera credentials, license files, or production tokens into chat, Issues, logs, or test fixtures.
- Never invent a production endpoint. Use operator-supplied targets or synthetic loopback examples.
- Prefer read-only checks. Do not restart services, edit configuration, change firewall rules, or modify devices unless the user explicitly requests a separate remediation step.
- Treat a successful HTTP/TCP probe as reachability evidence only. It does not prove end-to-end business behavior.
- Review generated evidence before sharing it outside the operator's environment.

## Workflow

1. **Define the failing outcome.** Write one sentence describing what the operator expected and what was actually observed.
2. **Run a baseline.**
   ```bash
   edgesafe-doctor
   ```
3. **Add only the checks needed for the suspected path.** Prefer a small JSON plan based on `assets/check-plan.example.json`.
4. **Collect structured evidence.**
   ```bash
   edgesafe-doctor --config <check-plan.json> --evidence evidence.json
   ```
5. **Classify each result.**
   - `PASS`: the specific check succeeded; do not generalize beyond it.
   - `WARN`: the target responded or exists, but the result is incomplete or unusual.
   - `FAIL`: the check could not establish the expected condition.
6. **Trace the delivery chain in order:** source/camera → detector/event → adapter → rule → alarm lifecycle → operator feedback.
7. **Stop at the first unsupported transition.** Do not patch downstream behavior until the upstream evidence is known.
8. **Produce a handoff** with:
   - observed symptom;
   - checks run;
   - relevant PASS/WARN/FAIL evidence;
   - first unsupported transition;
   - one next verification step;
   - anything intentionally not tested.

For interpretation guidance, read `references/triage-playbook.md`.

## Example

A camera page is visible, but no overcrowding alarm reaches the operator.

Do not jump directly to the rule engine. Verify the chain:

1. Is the camera/event source fresh?
2. Is the expected service reachable?
3. Is normalized event data arriving?
4. Does the rule receive the expected inputs for long enough?
5. Does the alarm enter the expected state?
6. Can the operator actually see or hear the alarm?

The useful result is not "the service is running." The useful result is the earliest transition that cannot be proven.

## Completion criteria

Finish when the user has a reproducible observation, a bounded fault domain, and a concrete next verification step. If the evidence is insufficient, say exactly what is missing instead of guessing.
