---
id: mode-drill-vertically
title: Drill Vertically mode
aliases:
  - what is drill vertically mode
  - what happens in drill vertically mode
  - why is the rig drilling straight down first
  - why does it drill vertically first
  - how deep is the vertical section
  - vertical drilling state
  - autonomous drill vertically
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - DrillVertically
  - Vertical
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

In Drill Vertically mode, the rig drills the initial vertical section before directional steering begins. This establishes a stable wellbore before any trajectory changes.

**What happens in Drill Vertically:**
- The bit drills straight down without azimuth steering
- WOB and RPM are controlled automatically
- No inclination or azimuth adjustments are made

**Transition condition:** When the measured depth reaches 10 cm (the required vertical distance), the state machine moves to Target Intersection mode.

**Why vertical first:** Starting with a vertical section ensures the wellbore is stable and the BHA is properly aligned before directional drilling begins.
