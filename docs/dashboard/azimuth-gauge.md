---
id: azimuth-gauge
title: Azimuth gauge display
aliases:
  - azimuth gauge
  - compass
  - toolface orientation
  - azimuth display
  - what does the compass show
  - current azimuth
  - azimuth target
  - where do I see toolface
screen: left_monitor
component: azimuth_gauge
raw_tags:
  - AzimuthGauge
  - AzimuthOrientation
  - AzimuthTarget
  - AzimuthSetpoint
  - AzimuthRotationVelocity
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

The azimuth gauge displays the current toolface orientation as a compass on the left monitor.

## Display Elements

**Needle (current orientation):**
- Shows the current azimuth angle (0-360°)
- Points in the direction of the bent sub
- Signal: `AzimuthOrientation`

**Target marker:**
- Shows the target azimuth angle
- Indicates where the system is steering toward
- Signal: `AzimuthTarget` or `AzimuthSetpoint`

**Angular velocity indicator:**
- Shows the current rotation speed of the azimuth
- Signal: `AzimuthRotationVelocity`

## Reading the Gauge

- **0°/360°** - North (top)
- **90°** - East (right)
- **180°** - South (bottom)
- **270°** - West (left)

## During Directional Drilling

The controller adjusts the toolface orientation to steer the wellbore. The needle shows where the bent sub is currently pointing, and the target marker shows where it needs to be for the planned trajectory.
