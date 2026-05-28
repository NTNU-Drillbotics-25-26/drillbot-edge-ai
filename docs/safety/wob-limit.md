---
id: software-wob-limit
title: Software WOB limit
aliases:
  - what happens when wob limit is reached
  - what is the wob limit
  - what is the safe wob limit
  - does the rig stop on too much weight on bit
  - how is wob protected
  - wob limit behavior
  - maximum wob
screen: left_monitor
component: wob_gauge
raw_tags:
  - WOBLimit
  - WOB
  - SafetyLimit
status: confirmed_on_current_rig
source_type: alarm_meaning
historic: false
---

The low-level software includes a WOB (Weight on Bit) limit to protect the drill string and mechanical components.

**What happens when the limit is reached:**
- The lowering control signal is set to zero
- The carriage stops moving downward
- An alarm may be triggered (Critical WOB)

**Purpose:** Keeps the drill string within safe load limits and reduces the chance of mechanical damage to the bit, rod, or BHA.

**The WOB limit value:** Check the current limit in the system settings. The exact value depends on the configuration for the current run.

**If WOB limit is triggered:**
1. The system automatically stops lowering
2. Check for bit wear or formation change
3. Adjust WOB setpoint to a lower value
4. Resume drilling within safe limits
