---
id: trajectory-3d
title: 3D trajectory display
aliases:
  - 3d trajectory
  - 3d well path
  - trajectory visualization
  - dubins curve display
  - planned path display
  - actual path display
  - well trajectory
  - where can I see the well path
screen: right_monitor
component: trajectory_3d
raw_tags:
  - Trajectory3D
  - DubinsCurve
  - WellPath
  - TargetPoints
  - PositionX
  - PositionY
  - PositionZ
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

The 3D trajectory display shows the wellbore path and targets on the right monitor.

## Display Elements

**Planned Path (Grey curve):**
- The Dubins curve calculated to intersect all target points
- Shows the intended trajectory before drilling
- Received via TCP on port 4050

**Actual Path (Blue curve):**
- The real drilled trajectory
- Updated in real-time from position data
- Signals: `PositionX`, `PositionY`, `PositionZ`

**Target Points (Orange markers):**
- The waypoints the drill must pass through
- Shown as spheres or markers on the 3D view

## Coordinates

| Axis | Signal | Description |
|------|--------|-------------|
| X | PositionX | Horizontal position (meters) |
| Y | PositionY | Horizontal position (meters) |
| Z | PositionZ | Vertical depth (cm, TVD) |

## Interpreting the Display

- Compare grey (planned) to blue (actual) to assess accuracy
- Deviation between curves indicates steering error
- Target markers should be close to the actual path

## Data Sources

- **Position data:** UDP telemetry (port 5005)
- **Planned curve:** TCP trajectory server (port 4050)
- **Target points:** TCP trajectory server (message type 2)
