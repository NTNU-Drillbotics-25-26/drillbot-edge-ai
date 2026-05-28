---
id: data-acquisition-architecture
title: How data acquisition is split between computers
aliases:
  - how is data acquisition organized
  - which computer reads the sensors
  - how do the computers exchange data
  - daq architecture
  - data acquisition
  - where does sensor data go
screen: null
component: system
raw_tags:
  - DAQ
  - DataAcquisition
  - UDP
status: confirmed_on_current_rig
source_type: system_overview
historic: false
---

The DAQ (Data Acquisition) architecture is split between two computers for reliability and performance.

**Low-level computer responsibilities:**
- Interfaces directly with rig hardware
- Reads surface sensors (load cell, torque, encoders)
- Runs local control loops
- Sends selected signals over UDP

**High-level computer responsibilities:**
- Receives UDP stream from low-level
- Reads downhole sensor data (BLE from Arduino)
- Combines surface and downhole data
- Runs trajectory and steering logic
- Displays data in GUI

**Data flow:**
1. Sensors → Low-level computer
2. Low-level → UDP → High-level
3. Downhole sensor → BLE → High-level
4. High-level → GUI display and logging

**Update rate:** Data exchange occurs at high frequency to support real-time control.
