from edgesafe.rules import OccupancyRule, OccupancyRuleEngine
from edgesafe.zones import ZoneIntrusionEngine, ZoneIntrusionRule


def main():
    occupancy = OccupancyRule(
        rule_id="demo-overcrowd",
        camera_id="CAM-DEMO-01",
        threshold=4,
        duration_seconds=3,
        cooldown_seconds=10,
    )
    occupancy_engine = OccupancyRuleEngine()

    print("Occupancy demo")
    for timestamp, count in [(0, 4), (1, 4), (3, 4), (4, 4), (15, 2)]:
        decision = occupancy_engine.evaluate(
            occupancy,
            person_count=count,
            timestamp=timestamp,
        )
        print(f"t={timestamp:>2}s count={count} -> {decision.value}")

    zone = ZoneIntrusionRule(
        rule_id="demo-zone",
        camera_id="CAM-DEMO-02",
        polygon=[(0.45, 0.45), (0.95, 0.45), (0.95, 0.95), (0.45, 0.95)],
        duration_seconds=3,
        cooldown_seconds=10,
    )
    zone_engine = ZoneIntrusionEngine()

    print("\nZone demo")
    for timestamp, point in [(0, (0.7, 0.7)), (1, (0.7, 0.7)), (3, (0.7, 0.7)), (5, (0.2, 0.2))]:
        decision = zone_engine.evaluate(
            zone,
            track_id="person-1",
            centroid=point,
            timestamp=timestamp,
        )
        print(f"t={timestamp:>2}s point={point} -> {decision.value}")


if __name__ == "__main__":
    main()
