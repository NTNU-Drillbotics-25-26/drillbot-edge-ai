---
id: well-progress
title: Well progress display
aliases:
  - well progress
  - target coordinates
  - where can I see coordinates
  - where can I see the current depth
  - see coordinates
  - on the right path
  - are we on the right path
  - difference from target
  - how far from target
  - current position
screen: right_monitor
component: well_progress
raw_tags:
  - WellProgress
  - Trajectory
  - TargetCoordinates
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

# Well Progress Display

The Well Progress panel shows the 3D trajectory and target coordinates on the right monitor.

**Elements displayed:**
- **3D plot** - Visualization of wellbore path
- **Coordinate table** - X, Y, Z values next to the plot
- **Target markers** - Orange nodes indicating target points
- **Planned path** - Grey curve showing intended trajectory
- **Actual path** - Blue curve showing drilled trajectory

**How to check path accuracy:**
1. Compare the grey (Planned) curve with the blue (Actual) curve
2. Small deviations are normal; large deviations may indicate steering issues
3. Orange target nodes should be near or on the blue actual path

**Coordinate system:**
- X, Y = Horizontal position
- Z = Vertical depth (measured from surface)

**Note:** The assistant cannot read real-time values from this display. Check the screen directly to verify current position and path status.
