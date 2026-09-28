# Field Acceptance Checklist

Use this checklist after deployment or a material repair.

## Camera and stream

- [ ] Every configured camera is reachable.
- [ ] Live timestamps continue to advance.
- [ ] Streams recover after a temporary interruption.
- [ ] No stale duplicate camera configuration is active.

## AI and rules

- [ ] Person detections are visible on the intended cameras.
- [ ] Occupancy threshold uses the expected count.
- [ ] Persistence duration matches the configured rule.
- [ ] A rule does not trigger before the persistence window.
- [ ] Cooldown prevents rapid duplicate alarms.
- [ ] Recovery clears the active state when the condition ends.
- [ ] Zone intrusion uses the intended polygon.

## Alarm workflow

- [ ] Alarm record is created.
- [ ] Snapshot belongs to the correct camera and time.
- [ ] Operator can open alarm detail.
- [ ] Local voice alert is audibly confirmed on the target machine.
- [ ] Program logs agree with the observable result.

## Authentication and reboot

- [ ] The intended administrator account is unique.
- [ ] Fixed credentials survive application restart.
- [ ] Fixed credentials survive operating-system reboot.
- [ ] No unexpected bootstrap account is regenerated.
- [ ] Session behavior is understood and documented.

## Operational handover

- [ ] Diagnostic command or script is available.
- [ ] Backup / rollback location is documented.
- [ ] Customer-specific secrets are excluded from public documentation.
- [ ] The accepted version and configuration are recorded.
