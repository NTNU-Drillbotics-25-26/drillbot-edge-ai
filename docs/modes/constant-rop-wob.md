---
id: constant-rop-wob
title: Constant ROP and WOB mode
aliases:
  - constant rop
  - constant wob
  - set constant rop
  - set constant wob
  - rop control mode
  - wob control mode
  - is constant rop available
  - is constant wob available
screen: null
component: control_system
raw_tags:
  - ConstantROP
  - ConstantWOB
  - ControlMode
status: not_implemented
source_type: specification
historic: false
---

# Constant ROP and WOB Mode

**Status: NOT AVAILABLE** in the current GUI.

Constant ROP and constant WOB control modes are not implemented in the current system. There is no button or setting to enable these modes.

**What these modes would do (if implemented):**
- **Constant ROP:** Automatically adjust WOB to maintain a target rate of penetration
- **Constant WOB:** Maintain a fixed weight on bit regardless of ROP

**Current behavior:**
The system uses direct WOB setpoint control. The operator or autonomous system sets a WOB target, and the control loop maintains that WOB.

**Alternative:**
If constant ROP or WOB control is required, use the legacy GUI (old GUI) which may have this feature.
