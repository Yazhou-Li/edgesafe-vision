"""Synthetic Frigate/MQTT adapter demo.

No broker, camera, or production credentials are required.
"""

from edgesafe.adapters import (
    parse_frigate_mqtt_message,
    parse_normalized_mqtt_event,
)


def main():
    frigate_payload = {
        "type": "new",
        "after": {
            "id": "1700000000.123-demo",
            "camera": "demo_entrance",
            "frame_time": 1700000001.5,
            "label": "person",
            "score": 0.91,
            "current_zones": ["entrance"],
        },
    }

    event = parse_frigate_mqtt_message(
        "frigate/events",
        frigate_payload,
    )
    print("Frigate -> EdgeEvent")
    print(event.to_dict())

    normalized = parse_normalized_mqtt_event(
        "edgesafe/events",
        {
            "eventId": "EV-DEMO-FIRE",
            "cameraId": "CAM-DEMO-02",
            "type": "fire",
            "observedAt": 1700000010.0,
            "confidence": 0.96,
            "attributes": {"source": "synthetic-detector"},
        },
    )

    print("\nNormalized MQTT -> EdgeEvent")
    print(normalized.to_dict())


if __name__ == "__main__":
    main()
