---
id: mode-drill-towards-exit
title: Drill Towards Exit mode
aliases:
  - what is drill towards exit mode
  - what happens in drill towards exit mode
  - what happens after the last target is passed
  - why is wob higher now
  - exit drilling state
  - autonomous drill towards exit
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - DrillTowardsExit
  - ToExit
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

In Drill Towards Exit mode, the rig drills toward the rock exit without active steering. All targets have been passed.

**What happens in Drill Towards Exit:**
- No azimuth steering is performed
- WOB may be increased to improve ROP (since steering accuracy is no longer critical)
- The bit follows its natural trajectory toward the exit

**Why WOB increases:** Without the need for precise steering, higher WOB can be applied to maximize drilling speed.

**Transition condition:** The bit approaches the rock boundary.

**Next state:** Rock Exit Detection.
