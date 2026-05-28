---
id: software-torque-limit
title: Software torque limit
aliases:
  - what happens when torque limit is reached
  - what is the torque limit
  - what is the safe torque limit
  - does the rig stop on high torque
  - how is rotating torque protected
  - torque limit behavior
  - maximum torque
screen: left_monitor
component: torque_gauge
raw_tags:
  - TorqueLimit
  - Torque
  - SafetyLimit
status: confirmed_on_current_rig
source_type: alarm_meaning
historic: false
---

The low-level software includes a torque limit to protect the drill rod and drill pipe from excessive twisting forces.

**What happens when the limit is reached:**
- The rotational control signal is set to zero
- Rotation stops to prevent rod damage
- An alarm may be triggered

**Purpose:** Keeps the drill rod and drill pipe within safe operating limits and prevents torsional failure.

**Common causes of high torque:**
- Stuck bit condition
- Formation change to harder rock
- Pack-off or cuttings buildup
- Rod windup

**If torque limit is triggered:**
1. Rotation stops automatically
2. Reduce WOB to relieve pressure
3. Check for stuck bit or obstruction
4. Work the pipe if necessary before resuming
