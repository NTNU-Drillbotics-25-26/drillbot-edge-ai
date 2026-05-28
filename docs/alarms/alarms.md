---
id: alarms
title: Alarm meanings
aliases:
  - alarms
  - alarm reference
  - what does the alarm mean
  - what does the red alarm mean
  - bit lifted
  - what does bit lifted mean
  - stuck bit
  - what does stuck bit mean
  - critical wob
  - what does critical wob mean
  - rod windup
  - what does rod windup mean
  - out of range
  - what does out of range mean
  - lithology change
  - what does lithology change mean
  - md target reached
  - what does md target reached mean
  - why do I see stuck bit so often
  - alarm troubleshooting
screen: left_monitor
component: alarm_panel
raw_tags:
  - Alarm
  - critical_wob
  - stuck_bit
  - bit_lifted
  - rod_windup
  - out_of_range
  - lithology_change
  - md_target
  - CriticalWOB
  - StuckBit
  - BitLifted
  - RodWindup
  - OutOfRange
  - LithologyChange
  - MDTargetReached
  - isStuckBit
  - isRodWindup
  - WOBSetpoint
  - LithologyChanged
status: confirmed_on_current_rig
source_type: alarm_meaning
historic: false
---

# Drilling Alarm Reference

This document describes all alarms that may appear on the alarm panel (left monitor).

---

## Bit Lifted

**Meaning:** No weight is being applied to the bit.

**Trigger condition:** `WOBSetpoint == 0` (setpoint is zero).

**Actions:**
1. Check if this is intentional (e.g., during survey or tripping)
2. If unintentional, verify carriage position
3. Lower the carriage to re-establish weight on bit
4. Resume drilling with appropriate WOB setpoint

---

## Stuck Bit

**Meaning:** Pipe rotation is blocked or restricted.

**Trigger condition:** `isStuckBit > 0.5` (signal from low-level system).

**Actions:**
1. Stop drilling immediately
2. Reduce WOB to zero
3. Hoist the bit slightly
4. Attempt to free by working the pipe (rotate and reciprocate)
5. Check for pack-off or formation issue

**Note:** In autonomous mode, the system handles stuck bit automatically by hoisting and re-entering. Occasional stuck bit alarms are normal during autonomous drilling.

---

## Critical WOB

**Meaning:** Measured weight on bit has exceeded the safety threshold.

**Trigger condition:** `WOB > 50.0 kg`.

**Action:**
1. Reduce WOB immediately to safe operating range

---

## Rod Windup

**Meaning:** Excessive torsional energy stored in the drill string, typically caused by the sensor cable winding around the pipe.

**Trigger condition:** `isRodWindup > 0.5` (signal from control system).

**Actions:**
1. Stop drilling
2. Check for cable windup visually
3. Rotate azimuth in the opposite direction to unwind the cable
4. Resume drilling once cable is straightened

---

## Out of Range

**Meaning:** One or more parameters are outside acceptable operating bounds.

**Trigger condition:** Any monitored parameter (WOB, RPM, torque, flow, etc.) exceeds configured limits.

**Actions:**
1. Check dashboard to identify which parameter is out of range
2. Adjust the corresponding setpoint to bring parameter within limits
3. Acknowledge the alarm
4. Update operating limits if formation conditions require different parameters

---

## Lithology Change

**Meaning:** A change in formation rock type has been detected.

**Trigger condition:** `LithologyChange > 0.5` (signal from mahcine learning detection algorithm).

**Actions:**
1. Review current drilling parameters
2. Adjust WOB and RPM for the new formation
3. Monitor closely for the next few centimeters

---

## MD Target Reached

**Meaning:** The drill bit has reached the planned measured depth target.

**Trigger condition:** `MDTargetReached > 0.5` (signal from autonomous system).

**Actions:**
1. Drilling will stop automatically (in autonomous mode)
2. Verify depth measurement accuracy
4. Document final depth
