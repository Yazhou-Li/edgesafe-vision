# Case Study: From Camera Feed to Verifiable Alarm Workflow

This case study documents the engineering lessons behind EdgeSafe Vision without exposing customer data, credentials or production infrastructure.

## Problem

A real edge-AI deployment needed to turn multiple camera feeds into reliable operational alerts. The difficult part was not object detection alone. The system also needed to handle:

- multi-camera stream health
- occupancy thresholds
- persistence windows before triggering
- restricted-zone events
- alarm snapshots
- local voice playback
- browser stream recovery
- authentication persistence
- Windows and Ubuntu deployment differences
- repeatable acceptance testing

## Engineering focus

The project treated AI inference as one component in a larger delivery chain:

```text
camera -> stream -> inference -> event -> rule -> alarm -> operator feedback
```

Every stage needed observable evidence. A process reporting "started" was not treated as proof that an operator actually received the alert.

## Representative production lessons

### 1. Separate video freshness from AI metadata freshness

A live video stream and a bounding-box API can remain individually healthy while becoming temporally misaligned. Monitoring both paths independently makes stale overlays easier to diagnose.

### 2. Treat audio as an end-to-end user experience

Launching a player process successfully does not prove that sound reached the desktop audio session. Validation must include the actual operating-system audio path and a real audible check.

### 3. Make authentication survive reboot

Bootstrap logic that is safe for first installation can become dangerous in production if it recreates administrative state after a data-path error. Production initialization should be idempotent and explicit.

### 4. Keep field diagnostics reproducible

Operational scripts should produce concise PASS/WARN/FAIL evidence that can be reviewed remotely without requiring a customer to interpret low-level logs.

## Acceptance philosophy

A fix is considered complete only after:

1. the root cause is identified;
2. the smallest reasonable change is applied;
3. configuration and syntax checks pass;
4. the service is restarted when required;
5. the real workflow succeeds;
6. regression checks pass;
7. reboot behavior is verified when persistence matters.

## Open-source boundary

This document describes reusable engineering patterns only. It does not include customer identities, production credentials, alarm history, commercial licensing keys or private deployment assets.
