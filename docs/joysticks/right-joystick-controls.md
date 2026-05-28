---
id: right-joystick-controls
title: Right joystick controls
aliases:
  - right joystick
  - right joystick controls
  - stop autonomous drilling
  - how do I stop drilling
  - re-enable drives
  - enable drives
  - how do I enable drives
  - start autonomous drilling
  - how do I start autonomous
  - set wob to zero
  - set wob = 0
  - how do I set wob to zero
  - blue button
  - black button
  - green button
  - red button
  - disable drives
  - how do I disable drives
screen: right_monitor
component: right_joystick
raw_tags:
  - RightJoystick
  - WOBSetpoint
  - EnableDrives
  - DisableDrives
  - StartAutonomous
  - JoystickGainRight
  - ROPSetpoint
  - AzimuthOrientation
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

The right joystick provides primary control for autonomous operation and hoisting.

**Button controls:**
| Button | Color | Function |
|--------|-------|----------|
| Start Autonomous | Green | Begin autonomous drilling |
| Disable Drives | Red | Stop all motors immediately |
| Set WOB = 0 | Blue | Zero the WOB setpoint |
| Enable Drives | Black | Re-enable motors after disable |

**Hat controls:**
- **Up/Down** - Adjust ROP sensitivity
- **Left/Right** - Adjust vibration intensity

**Stick controls:**
- **Y-Axis Forward** - Lower (increase depth, apply WOB)
- **Y-Axis Back** - Hoist (decrease depth, lift bit)
- **X-Axis Left** - Rotate azimuth counter-clockwise
- **X-Axis Right** - Rotate azimuth clockwise

**Common procedures:**

*To stop drilling:*
Press the red Disable Drives button.

*To resume after stopping:*
Press the black Enable Drives button.

*To start autonomous mode:*
Press the green Start Autonomous button (targets must be configured).
