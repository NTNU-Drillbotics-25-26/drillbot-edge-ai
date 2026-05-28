---
id: state-panel
title: State panel display
aliases:
  - state panel
  - state progress bar
  - drilling state display
  - where do I see the current state
  - what state am I in
  - state progress
  - autonomous progress
screen: right_monitor
component: state_panel
raw_tags:
  - StatePanel
  - AutonomousOperationCurrentState
  - PositionZ
  - TargetDepth3D
  - TargetIntersectionDepth
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

The state panel displays autonomous drilling progress as a segmented progress bar on the right monitor.

## Display Elements

The progress bar shows 6 segments representing the autonomous states:

| State | ID | Segment | Progress Calculation |
|-------|-----|---------|---------------------|
| Init | 0 | Fixed width | 30% of first segment |
| Vertical | 1 | Proportional | Based on 10cm vertical target |
| Target Intersection | 2 | Proportional | Based on `TargetDepth3D` |
| To Exit | 3 | Fixed width | 40% of segment |
| Exit Detection | 4 | Fixed width | 40% of segment |
| Completed | 5 | Fixed width | 30% of final segment |

## Visual Indicators

- **Completed states:** Dark green (`#008B0E`)
- **Current state:** Primary blue (`#2B6CB0`) with animation
- **Future states:** Light gray
- **Error state (6):** Red, progress held at failure point

## Progress Tracking

Progress within each state is calculated using:
- `PositionZ` - Current hoisting position (depth)
- `TargetDepth3D` or `TargetIntersectionDepth` - Target intersection depth
- Phase start position (remembered when entering each state)

## Signal Source

The state ID comes from: `AutonomousOperationCurrentState` (UDP signal, values 0-5)

## Interpreting the Display

- The filled portion shows how far through the current state
- Multiple green segments mean previous states completed
- Blue segment with animation indicates current active state
- Red indicates an error occurred at that position
