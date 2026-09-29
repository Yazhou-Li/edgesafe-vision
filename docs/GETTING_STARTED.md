# Getting Started

This guide gets the public EdgeSafe Vision toolkit running without production cameras, customer infrastructure, or private credentials.

## 1. Requirements

- Python 3.10+
- Windows, Linux, or macOS for the pure-Python reference modules
- Optional: a reachable HTTP/TCP service if you want to exercise `edgesafe-doctor`

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
cd edgesafe-vision
python -m pip install -e .
```

## 2. Run the regression tests

```bash
python -m unittest discover -s tests -v
```

The reference modules are deterministic and intentionally small so behavior can be reviewed and tested without a GPU or camera.

## 3. Run the synthetic demo

```bash
python examples/demo.py
```

The demo uses public synthetic data. It is safe to run without connecting to a production system.

## 4. Try EdgeSafe Doctor

Baseline checks:

```bash
edgesafe-doctor
```

Resolve a hostname without opening a TCP/HTTP connection:

```bash
edgesafe-doctor --dns localhost
```

Probe a local HTTP endpoint:

```bash
edgesafe-doctor --http http://127.0.0.1:5000
```

Probe HTTP and TCP targets and return machine-readable output:

```bash
edgesafe-doctor \
  --http http://127.0.0.1:5000 \
  --tcp 127.0.0.1:1883 \
  --json
```

Run a reusable check plan and write a structured evidence bundle:

```bash
edgesafe-doctor \
  --config examples/doctor.example.json \
  --evidence evidence.json
```

A check-plan file can contain:

```json
{
  "dns": ["localhost"],
  "http": ["http://127.0.0.1:5000"],
  "tcp": ["127.0.0.1:1883"],
  "files": ["./pyproject.toml"]
}
```

Evidence bundles include platform/Python metadata and PASS/WARN/FAIL checks,
but intentionally do not collect the machine hostname. HTTP result labels also
remove embedded URL credentials, query strings, and fragments before output.

Review evidence before sharing it externally: TCP targets, file paths, and
service URLs may still reveal deployment details supplied by the operator.

EdgeSafe Doctor is read-only by design.

## 5. Use the occupancy rule engine

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

The caller supplies timestamps, which makes persistence and cooldown behavior deterministic in tests.

## 6. Normalize Frigate / MQTT events

Run the synthetic adapter demo:

```bash
python examples/adapter_demo.py
```

Or normalize a Frigate tracked-object message directly:

```python
from edgesafe.adapters import parse_frigate_mqtt_message

event = parse_frigate_mqtt_message(
    "frigate/events",
    {
        "type": "new",
        "after": {
            "id": "demo-event-1",
            "camera": "demo_entrance",
            "frame_time": 100.0,
            "label": "person",
            "score": 0.91,
        },
    },
)

print(event.to_dict())
```

The adapter layer does not connect to an MQTT broker itself, so applications
remain free to use the client library or bridge that fits their environment.

See [Integrations](INTEGRATIONS.md) for the supported topic contracts.

## 7. Run the end-to-end synthetic pipeline

```bash
python examples/end_to_end_demo.py
```

This deterministic scenario composes the normalized-event adapter, occupancy
rule engine, and alarm lifecycle with no camera, GPU, broker, or customer
infrastructure.

See [Reproducible Pipeline Demo](DEMO.md) to customize the JSONL scenario.

## 8. Integration path

A typical integration is:

```text
camera / detector
      ↓
adapter (Frigate / MQTT / webhook / custom)
      ↓
EdgeEvent
      ↓
rule engine
      ↓
alarm lifecycle
      ↓
operator feedback + acceptance evidence
```

See:

- [Architecture](ARCHITECTURE.md)
- [Event schema](EVENT_SCHEMA.md)
- [Acceptance checklist](ACCEPTANCE_CHECKLIST.md)
- [Sanitized field case study](CASE_STUDY.md)

## 9. Before connecting real infrastructure

Do not paste production credentials or customer data into the repository, examples, Issues, or Pull Requests. Use synthetic addresses and sanitized logs.

EdgeSafe Vision is an engineering reference toolkit. It is not a certified life-safety system and does not replace legally required alarms, emergency procedures, or site-specific safety controls.
