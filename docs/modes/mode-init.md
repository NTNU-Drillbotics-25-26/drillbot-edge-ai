---
id: mode-init
title: Init mode
aliases:
  - what is init mode
  - what happens in init mode
  - what does init mode do
  - is drilling active in init
  - why are the motors not running
  - autonomous mode init
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - Init
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

In Init mode, autonomous operation is deactivated. Controller outputs are disabled and all motor setpoints are zero. No drilling occurs in this state.

**What happens in Init:**
- Hoisting motor: disabled
- Rotation motor: disabled
- Azimuth motor: disabled
- WOB setpoint: zero

**Next state:** The operator activates autonomous operation from the GUI by pressing the green Start Autonomous button on the right joystick. The system then transitions to Drill Vertically mode.

**When you see Init:** This is the default state before autonomous drilling begins or after a reset.
