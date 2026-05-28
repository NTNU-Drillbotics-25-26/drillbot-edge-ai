---
id: left-joystick-controls
title: Left joystick controls
aliases:
  - left joystick
  - left joystick controls
  - how do I acknowledge alarm
  - how do I clear alarm
  - acknowledge alarm
  - change vibration source
  - set rpm to zero
  - how do I control rpm
screen: left_monitor
component: left_joystick
raw_tags:
  - LeftJoystick
  - JoystickFeedbackMode
  - JoystickGainLeft
  - AcknowledgeAlarm
  - RPMSetpoint
  - TopDriveRPMSetpoint
  - DismissAlarm
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

The left joystick provides control for alarms, RPM, and vibration feedback.

**Button controls:**
| Button | Color | Function |
|--------|-------|----------|
| Acknowledge Alarm | Green | Clear active alarm |
| Disable Drives | Red | Stop all motors immediately |
| Set RPM = 0 | Blue | Zero the RPM setpoint |
| Hold for Vibrations | Black | Feel drilling vibrations while held |

**Hat controls:**
- **Up/Down** - Adjust RPM sensitivity
- **Left/Right** - Change vibration source

**Stick controls:**
- **Forward** - Increase RPM setpoint
- **Back** - Decrease RPM setpoint

**Common procedures:**

*To acknowledge an alarm:*
Press the green button to clear the alarm from the display.

*To feel vibrations:*
Hold the black button and select source with hat left/right.

**Note:** Vibration sources use operator-facing labels. Internally mapped to `JoystickFeedbackMode`.
