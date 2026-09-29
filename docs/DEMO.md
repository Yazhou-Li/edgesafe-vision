# Reproducible Pipeline Demo

The end-to-end demo shows the public EdgeSafe Vision engineering path without a
camera, GPU, MQTT broker, customer network, or production credentials.

It composes real public modules:

```text
synthetic JSONL observation
        ↓
normalized MQTT adapter
        ↓
EdgeEvent
        ↓
occupancy rule engine
        ↓
alarm lifecycle
        ↓
deterministic console evidence
```

## Run it

```bash
python -m pip install -e .
python examples/end_to_end_demo.py
```

Expected behavior includes:

- a below-threshold observation returning `clear`;
- persistence before an overcrowding trigger;
- one alarm opening after the configured duration;
- cooldown behavior while the condition remains active;
- alarm resolution after the count clears;
- a second trigger after a later sustained condition.

The fixture is:

```text
examples/pipeline_events.jsonl
```

Every line uses the public normalized EdgeEvent JSON contract and synthetic
identifiers only.

## Modify the scenario

Copy the fixture and change the `observedAt` or `personCount` values:

```bash
python examples/end_to_end_demo.py --input my_scenario.jsonl
```

Each line must be a JSON object accepted by the normalized MQTT adapter and
contain a non-negative integer `attributes.personCount`.

## Why this matters

The demo is deliberately deterministic. A contributor can change a rule,
adapter, or alarm behavior and immediately verify the end-to-end effect without
requiring access to a field deployment.

It is also covered by an automated regression test, so the documented scenario
cannot silently drift away from the public code.

## Scope

This is an engineering demonstration, not a certified safety workflow. Real
deployments still require site-specific camera, inference, network, alarm,
security, and acceptance validation.
