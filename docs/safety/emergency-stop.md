---
id: emergency-stop
title: Emergency stop behavior
aliases:
  - what does the emergency stop do
  - what happens when e-stop is pressed
  - what happens when I press the emergency stop
  - does the emergency stop stop every motor
  - how is the emergency stop wired
  - where is the emergency stop button
  - e-stop behavior
screen: null
component: emergency_stop
raw_tags:
  - EmergencyStop
  - EStop
  - SafetySystem
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

The emergency stop (E-stop) immediately disables the hoisting and rotation drives by breaking the 24 V signal.

**What the E-stop stops:**
- Hoisting motor (vertical movement)
- Rotation motor (drill string rotation)

**What the E-stop does NOT stop:**
- Data acquisition system
- GUI and monitoring
- Sensor readings

**Location:** Positioned next to the operator for quick access.

**How it works:** The E-stop is hardwired into the 24 V safety circuit. When pressed, it physically breaks the enable signal to the drives, causing them to disable themselves independent of software.

**To resume operation:**
1. Release/reset the E-stop button
2. Address the cause of the emergency
3. Re-enable drives using the black Enable Drives button on the right joystick
