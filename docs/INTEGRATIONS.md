# Integrations

EdgeSafe Vision keeps external integrations behind small adapters so business
rules remain deterministic and detector-agnostic.

The current public adapter layer is intentionally broker-client agnostic: it
parses topic/payload values but does not open network connections or require a
specific MQTT library.

## Frigate events

Frigate publishes tracked-object changes to its events topic. EdgeSafe Vision
can normalize those messages:

```python
from edgesafe.adapters import parse_frigate_mqtt_message

payload = {
    "type": "new",
    "after": {
        "id": "1700000000.123-demo",
        "camera": "front_door",
        "frame_time": 1700000001.5,
        "label": "person",
        "score": 0.91,
        "current_zones": ["entrance"],
    },
}

event = parse_frigate_mqtt_message("frigate/events", payload)
print(event.to_dict())
```

The adapter currently maps:

- `person` -> `EventType.PERSON`
- `fire` -> `EventType.FIRE`
- `smoke` -> `EventType.SMOKE`
- any other Frigate object label -> `EventType.CUSTOM`

The original label is retained in event attributes.

## Frigate camera role status

Frigate camera role status topics are also supported:

```python
event = parse_frigate_mqtt_message(
    "frigate/front_door/status/detect",
    "offline",
)
```

Supported values:

- `online` -> `CAMERA_ONLINE`
- `offline` -> `CAMERA_OFFLINE`
- `disabled` -> `CUSTOM`

`disabled` is not treated as a fault because it can represent an intentional
runtime state.

A custom Frigate MQTT prefix can be supplied with `topic_prefix=`.

## Generic normalized MQTT events

Other detectors can publish EdgeSafe's normalized event schema to
`edgesafe/events`:

```json
{
  "eventId": "EV-42",
  "cameraId": "CAM-42",
  "type": "fire",
  "observedAt": 1700000010.0,
  "confidence": 0.97,
  "trackId": "track-42",
  "attributes": {
    "source": "synthetic-detector"
  }
}
```

Parse it with:

```python
from edgesafe.adapters import parse_normalized_mqtt_event

event = parse_normalized_mqtt_event("edgesafe/events", payload)
```

## Why there is no MQTT client dependency

The public core deliberately avoids coupling to a broker library. A deployment
can connect with paho-mqtt, an asyncio client, Home Assistant, Node-RED, or a
vendor-specific bridge and pass only the received topic/payload pair into the
adapter.

This keeps:

- rules easy to unit test;
- adapters usable in different runtimes;
- the public package lightweight;
- credentials and broker configuration outside reusable business logic.

## Supported Frigate surface

The adapter currently supports only the documented tracked-object events topic
and camera role status topics. Unsupported topics raise
`UnsupportedMqttMessage` instead of being silently misinterpreted.

This narrow contract is intentional. New Frigate topic families should be
added with fixtures and regression tests before being treated as supported.

Reference: https://docs.frigate.video/integrations/mqtt/


## Generic webhook events

HTTP servers can pass an already-decoded JSON object, a JSON string, or UTF-8
JSON bytes to the dependency-free webhook adapter. The core package does not
open a socket or depend on a web framework.

```python
from edgesafe.adapters import parse_webhook_event

event = parse_webhook_event(
    {
        "eventId": "EV-WEB-1",
        "cameraId": "CAM-WEB-1",
        "type": "person",
        "observedAt": 1700000020.0,
        "confidence": 0.9,
        "trackId": "track-web-1",
        "attributes": {"source": "synthetic-webhook"},
    }
)
```

The supported payload fields match the normalized EdgeSafe event contract:
`eventId`, `cameraId`, `type`, and `observedAt` are required;
`confidence`, `trackId`, and `attributes` are optional. Malformed JSON,
non-object JSON, invalid UTF-8, missing core fields, invalid event types, and
invalid optional values raise `ValueError`.

Applications remain responsible for HTTP routing, authentication, request-size
limits, and transport security before passing a payload to this adapter.
