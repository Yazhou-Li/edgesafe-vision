# Optional local container demo

This stack is an evaluation aid, not a production deployment asset. Docker is
not required by the EdgeSafe Python package.

## Requirements

- Docker with Compose support
- roughly 512 MiB free memory for the two small demo containers
- no camera, GPU, credentials, private endpoints, or customer data

## Run

```bash
docker compose -f demo-stack/compose.yaml up --build --abort-on-container-exit
```

The EdgeSafe container runs the same deterministic synthetic pipeline used by
the pure-Python quick start. Expected application summary:

```text
SUMMARY events=8 alarms_opened=2 alarms_resolved=1
```

The local Mosquitto service exists only to make the optional integration stack
ready for broker-oriented experiments; this first demo does not claim that the
synthetic pipeline has exercised MQTT delivery.

## Cleanup

```bash
docker compose -f demo-stack/compose.yaml down --volumes --remove-orphans
```

Do not add production RTSP URLs, tokens, private IPs, customer screenshots, or
deployment logs to this demo. Passing this stack demonstrates only that the
packaged synthetic components can start in the documented local environment;
it is not evidence of production readiness or a physical safety system.
