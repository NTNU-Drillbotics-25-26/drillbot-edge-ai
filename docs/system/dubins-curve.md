---
id: dubins-curve
title: How the rig calculates the path to target points
aliases:
  - how does the rig hit target points
  - how does autonomous drilling reach targets
  - what is dubins curve
  - what is a dubins path
  - how is the trajectory calculated
  - how does the rig steer to targets
  - path planning algorithm
  - why dubins curve instead of bezier
  - trajectory optimization
  - how is the path planned
screen: right_monitor
component: state_panel
raw_tags:
  - DubinsCurve
  - DubinsPath
  - TrajectoryPlanning
  - PathOptimization
status: confirmed_on_current_rig
source_type: control_algorithm
historic: false
---

The rig uses 3D Dubins curves to calculate the optimal drilling path to target points.

**What is a Dubins curve:**
The shortest path between two directional points using a curve-straight-curve (CSC) sequence with maximum curvature arcs.

**Path families used:**
- RSR (Right-Straight-Right)
- LSL (Left-Straight-Left)
- RSL (Right-Straight-Left)
- LSR (Left-Straight-Right)

**Why CSC and not CCC:**
Curve-curve-curve families require multiple turning angles which are unsuitable for drilling applications.

**Why Dubins over Bezier:**
Simulations showed Dubins curves provide:
- 4-10% better positional accuracy
- Shorter overall well paths
- Lower inclination in straight sections

**How it works:**
1. Target points are defined by the operator
2. System calculates optimal Dubins path connecting all targets
3. The path is displayed as the grey "Planned" curve
4. Controller steers the bit to follow this path
