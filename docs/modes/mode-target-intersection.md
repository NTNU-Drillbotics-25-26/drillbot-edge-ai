---
id: mode-target-intersection
title: Target Intersection mode
aliases:
  - what is target intersection mode
  - what happens in target intersection mode
  - how does the rig steer toward the target
  - how does directional drilling work
  - what is the dubins path
  - directional drilling state
  - what happens during target intersection
screen: right_monitor
component: state_panel
raw_tags:
  - AutonomousOperationCurrentState
  - TargetIntersection
  - DubinsPath
status: confirmed_on_current_rig
source_type: control_mode
historic: false
---

In Target Intersection mode, the rig drills directionally toward the target using active steering control.

**What happens in Target Intersection:**
- A planned reference Dubins path is followed
- The controller adjusts azimuth to keep inclination and azimuth close to the reference
- Downhole surveys are performed periodically by stopping azimuth rotation
- WOB and RPM are managed to balance ROP with steering accuracy

**Steering mechanism:** The bent sub in the BHA creates inclination. By controlling the azimuth (toolface orientation), the system steers the wellbore along the planned path.

**Transition conditions:**
- Final target depth is reached, OR
- Rock boundary is approached

**Next state:** Drill Towards Exit or Rock Exit Detection, depending on target configuration.
