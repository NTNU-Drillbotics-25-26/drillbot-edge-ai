---
id: parameter-limits
title: System parameter limits
aliases:
  - max wob
  - maximum wob
  - what is the wob limit
  - max torque
  - maximum torque
  - max azimuth torque
  - azimuthal torque limit
  - max rop
  - rop limit
  - how fast can it drill
  - hoisting torque
  - top drive torque
  - parameter limits
  - system limits
  - what are the safe limits
screen: null
component: control_system
raw_tags:
  - WOBLimit
  - TorqueLimit
  - ROPLimit
  - ParameterLimits
  - CRITICAL_WOB_THRESHOLD
  - WOB
  - TopDriveTorque
  - HoistingTorque
  - AzimuthTorque
status: confirmed_on_current_rig
source_type: specification
historic: false
---

# System Parameter Limits

These are the operational limits for the drilling system.

## Weight on Bit (WOB)
| Parameter | Value |
|-----------|-------|
| **Maximum WOB** | 50 kg |

Determined through calculations and experiments on the drill string.

## Rate of Penetration (ROP)
| Condition | Typical Value |
|-----------|---------------|
| Directional drilling | ~5–7 cm/min |
| Vertical drilling (no bent sub) | ~11–13 cm/min |
| Maximum (hoisting limit) | 40 cm/min |

ROP increases with higher WOB setpoints. Always constrained by maximum hoisting velocity.

## GUI Alarm Threshold
| Parameter | Default Value |
|-----------|---------------|
| Critical WOB threshold | 30.0 kN |

This threshold triggers the Critical WOB alarm in the GUI.

## Torque Limits
| System | Limit |
|--------|-------|
| **Top drive torque** | 1 Nm (system), 5 Nm (theoretical max) |
| **Hoisting torque** | 1 Nm (theoretical max) |
| **Azimuth torque** | ±15 Nm (PID controller limited) |

**Note:** Exceeding these limits may trigger safety shutdowns or cause mechanical damage.
