# Normalized Event Schema

EdgeSafe Vision separates detector-specific payloads from business rules.

A Frigate event, MQTT message, webhook or custom inference result should first
be translated into a small normalized event contract.

## Example

```json
{
  "eventId": "EV-DEMO-001",
  "cameraId": "CAM-DEMO-01",
  "type": "person",
  "observedAt": 12.4,
  "confidence": 0.93,
  "trackId": "person-7",
  "attributes": {
    "centroid": [0.52, 0.68]
  }
}
```

## Core fields

| Field | Meaning |
| --- | --- |
| `eventId` | Stable event identifier |
| `cameraId` | Logical camera identifier |
| `type` | Normalized event type |
| `observedAt` | Observation timestamp supplied by the adapter |
| `confidence` | Optional normalized confidence from 0 to 1 |
| `trackId` | Optional tracker/object identifier |
| `attributes` | Adapter-specific data that rules may optionally consume |

## Why normalize first

This design keeps business logic independent from a specific detector or
message broker.

It also makes it possible to:

- replay recorded events in tests;
- compare different detector backends;
- isolate adapter bugs from rule-engine bugs;
- preserve consistent alarm behavior when infrastructure changes.

## Supported reference types

The public contract currently defines:

- `person`
- `fire`
- `smoke`
- `camera_offline`
- `camera_online`
- `custom`

Defining an event type does not imply that EdgeSafe Vision ships a trained
detector for that type. Detection backends remain separate integrations.
