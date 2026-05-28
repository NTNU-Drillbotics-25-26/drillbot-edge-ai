---
id: stuck-bit
title: Stuck bit behavior
aliases:
  - stuck bit
  - getting stuck bit
  - stuck bit keeps appearing
  - why do I see stuck bit so often
  - bit stuck
  - bit is stuck
  - what to do when bit is stuck
  - bit struggling
screen: left_monitor
component: alarm_panel
raw_tags:
  - StuckBit
  - stuck_bit
  - TorqueMonitoring
status: confirmed_on_current_rig
source_type: troubleshooting
historic: false
---

# Stuck Bit Behavior

Stuck bit occurs when pipe rotation is blocked or restricted. Frequent stuck bit alarms indicate high torque and the bit struggling to rotate.

**Trigger condition:** Torque exceeds threshold while RPM drops below expected value.

## Autonomous Mode

The autonomous system handles stuck bit automatically:
1. Hoisting slightly (lifting the bit)
2. Re-entering the rock
3. Resuming drilling

This is completely normal behavior and part of the autonomous drilling logic. Seeing occasional stuck bit alarms during autonomous drilling is expected.

## Manual Mode

In manual mode, the operator must respond manually:
1. Stop drilling immediately
2. Reduce WOB to zero
3. Hoist the bit slightly
4. Re-enter the rock carefully
5. Resume with lower WOB if needed

**Warning:** Monitor torque carefully to avoid damage to the rotating rod.

**If stuck bit appears frequently:** Check for formation change, inadequate flow, or bit wear.
