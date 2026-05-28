---
id: autonomous-states
title: Autonomous state
aliases:
  - autonomous state
  - current drilling state
  - what state is the rig in
  - what does the state number mean
  - autonomousoperationcurrentstate
  - what does autonomousoperationcurrentstate mean
  - state 0
  - state 1
  - state 2
  - state 3
  - state 4
  - state 5
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - StateMachine
  - DrillingState
status: confirmed_on_current_rig
source_type: telemetry_definition
historic: false
---

The autonomous state indicates what the rig is currently doing during autonomous drilling.

**State display:** Shown on the right monitor in the State Panel.

**State values:**
| Number | Name | Progress Weight | Description |
|--------|------|-----------------|-------------|
| 0 | Init | 0.3 (fixed) | Motors disabled, waiting to start |
| 1 | Vertical | Proportional (10cm) | Drilling initial vertical section |
| 2 | Target Intersection | Proportional (dynamic) | Directional drilling toward targets |
| 3 | To Exit | 0.4 (fixed) | Drilling toward rock exit (no steering) |
| 4 | Exit Detection | 0.4 (fixed) | Detecting when bit exits rock |
| 5 | Completed | 0.3 (fixed) | Run finished successfully |

**Error state:**
| Number | Name | Description |
|--------|------|-------------|
| 6 | Error | Held at failed position (shown in red) |

**Technical note:** The GUI displays "Autonomous state" to operators. Internally, this value is transmitted via UDP as `AutonomousOperationCurrentState`.
