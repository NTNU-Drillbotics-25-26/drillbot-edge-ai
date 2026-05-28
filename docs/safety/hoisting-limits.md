---
id: hoisting-limit-switches
title: Upper and lower hoisting limit switches
aliases:
  - what stops the carriage from going too high
  - what stops the carriage from going too low
  - how do the hoisting limit switches work
  - why did the hoisting drive fault after a limit switch
  - why did hoisting stop
  - limit switch triggered
screen: null
component: hoisting_system
raw_tags:
  - LimitSwitch
  - HoistingLimit
  - SafetySystem
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

Two normally closed safety limit switches protect the hoisting system from mechanical damage.

**Upper limit switch:**
- Prevents collision with the top of the derrick
- Triggered when carriage moves too high

**Lower limit switch:**
- Prevents interference with the drill floor and stabilizer
- Triggered when carriage moves too low

**What happens when triggered:**
- The hoisting drive disables itself immediately
- A drive fault is generated
- The operator must reset the system

**Soft stops:** Two proximity-sensor soft stops provide early warning before the hard limit switches are reached. These stop hoisting without faulting the drive.

**If a limit switch is triggered:**
1. Note which limit was triggered (upper or lower)
2. Manually jog the carriage away from the limit
3. Reset the drive fault
4. Re-enable drives to continue operation
