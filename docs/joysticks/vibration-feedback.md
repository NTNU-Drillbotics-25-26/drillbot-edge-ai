---
id: vibration-feedback
title: How to receive vibration feedback
aliases:
  - vibration feedback
  - drillfeel
  - how do I get vibration feedback
  - how do I receive vibration feedback
  - how do I feel the drilling
  - change vibration source
  - haptic feedback
screen: left_monitor
component: left_joystick
raw_tags:
  - VibrationFeedback
  - JoystickFeedbackMode
  - JoystickGainLeft
  - DrillFeel
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

Vibration feedback lets the operator feel drilling conditions through the left joystick.

**To receive vibration feedback:**
- Hold the black button on the left joystick
- Vibrations are transmitted while the button is held

**To change vibration source:**
- Use the left joystick hat left/right control
- Cycle through available sources

**Available vibration sources:**
1. **Torsional + Lateral** - Combined rotational and side-to-side vibrations
2. **Torsional only** - Rotational vibrations only
3. **Lateral only** - Side-to-side vibrations only
4. **Axial only** - Up-and-down vibrations only

**Use cases:**
- Feel stuck bit conditions (high torsional vibration)
- Detect formation changes
- Monitor drilling smoothness

**Technical note:** The selected source is stored as `JoystickFeedbackMode` internally.
