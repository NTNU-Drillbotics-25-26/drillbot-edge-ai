---
id: autonomy-mode-overview
title: Autonomous mode sequence overview
aliases:
  - what autonomous modes does the rig use
  - what states does autonomous drilling have
  - how does autonomous drilling work
  - what is the state machine
  - autonomous operation states
  - state machine overview
  - list of drilling states
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - StateMachine
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

Autonomous operation is organized as a finite state machine. Each state activates different control logic and determines what the rig is doing.

**State sequence:**
1. **Init** (0) - Motors disabled, waiting for operator to start
2. **Drill Vertically** (1) - Drilling the initial 10 cm vertical section
3. **Target Intersection** (2) - Directional drilling toward targets using Dubins path
4. **Drill Towards Exit** (3) - Drilling to exit without active steering
5. **Rock Exit Detection** (4) - Detecting when the bit exits the rock
6. **Completed** (5) - Run finished successfully

**Special state:**
- **Unexpected Termination** - Emergency stop due to critical event (can occur from any state)

The state number (0-5) is displayed on the right monitor in the State Panel. The raw UDP alias is `AutonomousOperationCurrentState`.
