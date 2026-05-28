---
id: wob-zero
title: WOB zero meaning
aliases:
  - wob zero
  - why is the wob zero
  - why is wob showing zero
  - wob is zero
  - weight on bit zero
  - zero wob button
  - how to zero wob
screen: left_monitor
component: wob_gauge
raw_tags:
  - WOB
  - WeightOnBit
  - WOBZero
status: confirmed_on_current_rig
source_type: explanation
historic: false
---

# WOB Zero

WOB (Weight on Bit) of zero means no weight is being applied to the bit.

**Common reasons for zero WOB:**
- Bit is lifted off bottom (intentional or unintentional)
- WOB setpoint was set to zero (blue button pressed)
- Carriage is hoisting or not lowering
- Load cell calibration issue

**When zero WOB is normal:**
- During connections or tripping
- During surveys (stationary)
- After pressing the blue "Set WOB = 0" button
- In Init or Completed modes

**When zero WOB is unexpected:**
- During active drilling (should have positive WOB)
- If the bit lifted alarm also appears

**To resume drilling with WOB:**
1. Verify the bit is on bottom
2. Lower the carriage to apply weight
3. Increase WOB setpoint as needed

**To zero the WOB sensor:** Press the blue "Set WOB = 0" button on the right joystick before starting a run to calibrate for string weight.
