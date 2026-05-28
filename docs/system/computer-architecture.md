---
id: computer-architecture
title: High-level and low-level computer roles
aliases:
  - why are there two computers
  - what does the high-level computer do
  - what does the low-level computer do
  - computer roles in the rig
  - how do the computers communicate
  - system architecture
screen: null
component: system
raw_tags:
  - ComputerArchitecture
  - HighLevelControl
  - LowLevelControl
  - UDP
status: confirmed_on_current_rig
source_type: system_overview
historic: false
---

The rig uses separate computers for high-level and low-level control, communicating over UDP.

**Low-level computer (Raspberry Pi):**
- Direct hardware interaction with drives and sensors
- Local feedback loops (WOB control, RPM control)
- Safety limit enforcement
- Real-time motor control
- Reads surface sensors

**High-level computer (Operator PC):**
- Trajectory planning and steering logic
- GUI and operator interface
- Data logging and visualization
- Downhole sensor integration
- State machine for autonomous operation

**Communication:** The two systems exchange drilling data over UDP at high frequency.

**Why two computers:** Separating real-time hardware control from higher-level logic improves reliability and response time. Previous NTNU teams attempted single-computer integration without success.
