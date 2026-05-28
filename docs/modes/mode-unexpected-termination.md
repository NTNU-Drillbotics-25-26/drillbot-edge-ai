---
id: mode-unexpected-termination
title: Unexpected Termination mode
aliases:
  - what is unexpected termination
  - what does unexpected termination mean
  - why did the run terminate unexpectedly
  - what happens in unexpected termination
  - autonomous unexpected termination
  - emergency state
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - UnexpectedTermination
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

Unexpected Termination is the emergency stop state in the autonomy logic. The system has stopped due to a critical event.

**What happens in Unexpected Termination:**
- All motors are stopped immediately
- The operator is notified that the operation has ended abnormally
- The system waits for operator intervention

**How this state is triggered:**
- Critical alarm condition (e.g., excessive torque, WOB limit exceeded)
- Safety limit switch activated
- Communication failure with low-level system
- Operator-initiated emergency stop

**Operator actions:**
1. Identify the cause of termination from alarms or logs
2. Address the issue before resuming
3. Reset to Init mode when safe to continue

**Note:** This state can be entered from any other autonomous state.
