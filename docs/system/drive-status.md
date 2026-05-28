---
id: drive-status
title: Drive status indicators
aliases:
  - drive fault
  - fault signal
  - drive error
  - why is the drive faulted
  - how do I check drive status
  - drv-err
  - drv-rdy
  - drive ready
  - check drive status
  - reset drives
  - drive reset
  - how do I reset drives
screen: null
component: drives
raw_tags:
  - DriveStatus
  - DRV_ERR
  - DRV_RDY
  - DriveFault
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

# Drive Status Indicators

Each drive has indicator lights showing its current status.

**Status indicators:**
| Light | Meaning |
|-------|---------|
| **DRV-RDY** | Drive ready, normal operation |
| **DRV-ERR** | Drive error/fault condition |

**To check drive status:**
1. Look at the indicator lights on each drive
2. DRV-RDY lit = drive is operational
3. DRV-ERR lit = drive has a fault

**Common causes of drive faults:**
- Limit switch triggered
- Overcurrent condition
- Communication loss
- E-stop activated

**To reset a faulted drive:**
1. First, address the cause of the fault
2. Try pressing Enable Drives (black button on right joystick)
3. If fault persists, remove and restore power supply to the drives

**Warning:** Always investigate the cause of a fault before resetting.
