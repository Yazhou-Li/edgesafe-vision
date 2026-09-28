# Architecture

EdgeSafe Vision separates the system into observable stages so each failure can be diagnosed independently.

```text
Camera / RTSP
     |
     v
Stream Processor  ---> stream health
     |
     v
Inference / Tracking ---> objects + track IDs
     |
     v
Event Adapter ---> normalized observations
     |
     v
Rule Engine
  |       |
  |       +--> Zone intrusion
  +----------> Occupancy / overcrowding
     |
     v
Alarm Lifecycle
  |       |        |
snapshot  voice   operator workflow
     |
     v
Acceptance / Evidence
```

## Design principles

### Separate video from metadata

Video freshness and AI-object freshness are different signals. A healthy object API does not prove the browser is displaying a fresh frame, and a fresh video stream does not prove overlays are current.

### Make rules deterministic

Rule engines should consume explicit observations and timestamps. This makes persistence windows, cooldown and recovery behavior reproducible in tests.

### Keep deployment diagnostics non-invasive

Health checks should be read-only by default and clearly distinguish PASS, WARN and FAIL.

### Treat reboot behavior as part of correctness

Authentication state, runtime configuration and service startup are part of the product. A deployment is not considered stable until reboot persistence is verified.

## Integration boundaries

The Community Edition avoids embedding production authentication, licensing or device-control infrastructure. Integrations should be passed through adapters with synthetic examples and documented contracts.
