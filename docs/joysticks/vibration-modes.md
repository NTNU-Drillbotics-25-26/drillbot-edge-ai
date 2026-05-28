---
id: vibration-modes
title: Vibration feedback modes
aliases:
  - vibration modes
  - what are the vibration modes
  - vibration source options
  - torsional lateral axial
  - feedback mode 1
  - feedback mode 2
  - feedback mode 3
  - feedback mode 4
  - what does each vibration mode feel like
screen: left_monitor
component: left_joystick
raw_tags:
  - JoystickFeedbackMode
  - VibrationModes
  - TorsionalLateral
  - AxialFeedback
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

# Vibration Feedback Modes

The left joystick provides haptic feedback based on drilling conditions. Four modes are available.

## Left Joystick Modes

| Mode | Name | Short | Signal Value |
|------|------|-------|--------------|
| 1 | Torsional + Lateral | T+L | `JoystickFeedbackMode = 1` |
| 2 | Torsional Only | T | `JoystickFeedbackMode = 2` |
| 3 | Lateral Only | L | `JoystickFeedbackMode = 3` |
| 4 | Axial Only | A | `JoystickFeedbackMode = 4` |

## Mode Descriptions

**Mode 1: Torsional + Lateral (T+L)**
- Combined rotation and oscillation
- Rotation proportional to bit angular velocity
- Oscillation proportional to BHA accelerations
- Best for general drilling awareness

**Mode 2: Torsional Only (T)**
- Rotation feedback only
- Angular velocity proportional to bit rotation speed
- Good for detecting stuck bit conditions

**Mode 3: Lateral Only (L)**
- Oscillation feedback only
- Scaled to BHA lateral accelerations
- Good for detecting vibration issues

**Mode 4: Axial Only (A)**
- Vertical oscillation feedback
- Frequency proportional to bit bounce
- Good for detecting weight-on-bit issues

## Right Joystick Mode

The right joystick has a single feedback mode:

| Mode | Name | Description |
|------|------|-------------|
| 1 | Tripping in Feedback | Force opposite to applied, proportional to WOB |

## Changing Modes

**Left joystick:** Use hat left/right to cycle through modes 1-4.

**Intensity:** Use right joystick hat left/right to adjust vibration intensity (`JoystickGainLeft`, `JoystickGainRight` signals, range 0-1).
