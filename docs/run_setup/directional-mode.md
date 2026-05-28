---
id: directional-mode
title: How to start a directional run
aliases:
  - directional mode
  - directional run
  - start directional drilling
  - start autonomous drilling
  - how do I start autonomous
  - autonomous run
  - add target points
screen: startup_dialog
component: run_configuration
raw_tags:
  - DirectionalMode
  - AutonomousMode
  - target_points
  - RunConfiguration
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

Directional mode enables autonomous drilling toward specified target points.

**To start a directional run:**
1. Open the Run Configuration dialog
2. Select "Live Run"
3. Fill in Well and Wellbore names
4. Add one or more **Target Points** (X, Y, Z coordinates)
5. Click Start

**What happens with target points:**
- Targets are sent to the trajectory planning system
- A Dubins path is calculated to intersect all targets
- The system drills autonomously along this planned path

**When to use directional mode:**
- Competition runs requiring specific targets
- Testing trajectory control
- Any run where autonomous steering is desired

**Starting autonomous drilling:**
After setup, press the green Start Autonomous button on the right joystick to begin autonomous operation.
