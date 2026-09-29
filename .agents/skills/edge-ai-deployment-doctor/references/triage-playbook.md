# Evidence-driven triage playbook

This reference helps an agent interpret EdgeSafe Doctor output without overstating what the checks prove.

## Read results narrowly

### Python / platform

A PASS confirms that the diagnostic process can run in the reported Python/platform environment. It does not prove GPU, camera, browser, audio, or model-runtime compatibility.

### Disk

A PASS confirms the configured free-space threshold is met at the checked path. A WARN means free space is low enough to deserve attention; it does not prove that storage is the current root cause.

### File

A PASS proves that the path exists as a regular file and can be read. It does not validate the file's business semantics.

### TCP

A PASS proves a TCP connection could be established to the supplied host and port during the check. It does not prove authentication, protocol correctness, event freshness, or application health.

### HTTP

A 2xx-4xx response is evidence that an HTTP service was reachable. Authentication responses such as 401/403 can still be useful reachability evidence. Do not call the application healthy unless the expected business endpoint and response semantics were actually verified.

## Triage order

Use the earliest failed transition to bound the investigation:

1. **Environment** — Python/runtime, disk, required files.
2. **Reachability** — TCP/HTTP path is reachable from the machine that matters.
3. **Source freshness** — camera/event source is current rather than merely connected.
4. **Normalization** — incoming detector data becomes the expected `EdgeEvent`.
5. **Rule inputs** — rule sees the expected camera, zone, count, duration, and enabled state.
6. **Alarm lifecycle** — condition transitions into active/recovery states correctly.
7. **Operator feedback** — UI, voice, snapshot, or other final feedback actually reaches the operator.
8. **Persistence** — restart/reboot does not silently remove configuration or service behavior.

## Common traps

- "The page loads" is not proof that video frames are fresh.
- "The process is running" is not proof that the endpoint is usable.
- "The detector saw a person once" is not proof that an N-second persistence rule should fire.
- "The API returned 200" is not proof that the operator heard a voice alarm.
- "It worked before restart" is not proof that configuration is persistent.
- A screenshot without timestamps or reproduction steps is weak evidence.

## Evidence handoff template

Use a short handoff:

```text
Expected:
Observed:

Checks:
- PASS ...
- WARN ...
- FAIL ...

First unsupported transition:
...

Next verification:
...

Not tested:
...
```

Do not turn uncertainty into a definitive root cause. If two transitions remain plausible, list both and identify the cheapest check that separates them.
