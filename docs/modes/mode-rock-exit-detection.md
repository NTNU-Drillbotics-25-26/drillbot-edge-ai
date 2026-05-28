---
id: mode-rock-exit-detection
title: Rock Exit Detection mode
aliases:
  - what is rock exit detection mode
  - what happens in rock exit detection mode
  - how does the rig detect the exit
  - how does the system know when it exits the rock
  - why are wob and rop reduced near exit
  - exit detection state
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - RockExitDetection
  - ExitDetection
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

In Rock Exit Detection mode, the system watches for signs that the bit has exited the rock sample.

**What happens in Rock Exit Detection:**
- WOB is reduced to a low value
- ROP is reduced for careful drilling
- Sensor data is monitored for changes indicating material transition

**Detection method:** The system looks for a change in drilling response (torque, ROP, vibrations) when the bit moves from concrete into the target material, which is usually wood.

**Why reduce WOB/ROP:** Lower drilling parameters make the material transition easier to detect and prevent damage to the bit or exit material.

**Transition condition:** Material change is identified.

**Next state:** Completed.
