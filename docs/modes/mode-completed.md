---
id: mode-completed
title: Completed mode
aliases:
  - what is completed mode
  - what happens in completed mode
  - what happens when the run is finished
  - what happens when drilling is done
  - why did all motor actions stop
  - autonomous completed state
  - is drilling finished
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - Completed
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

In Completed mode, the autonomous drilling run has finished successfully. The bit has exited the rock sample.

**What happens in Completed:**
- All motor actions are stopped
- Hoisting, rotation, and azimuth motors are disabled
- The system waits for operator input

**Operator actions:**
1. Review the drilling log and verify target accuracy
2. Reset the operation back to Init if another run is needed
3. Proceed with sample removal or next steps

**What this means:** The drilling objective has been achieved and the wellbore has reached the planned exit point.
