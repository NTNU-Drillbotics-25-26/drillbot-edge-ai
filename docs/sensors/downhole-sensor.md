---
id: downhole-sensor
title: Downhole sensor overview
aliases:
  - what is the downhole sensor
  - what does the arduino measure
  - what does the downhole sensor measure
  - how are inclination and azimuth measured downhole
  - downhole measurements
  - where is the inclination sensor
  - bha sensor
screen: null
component: downhole_sensor
raw_tags:
  - DownholeSensor
  - ArduinoNano33BLE
  - Inclination
  - Azimuth
status: confirmed_on_current_rig
source_type: telemetry
historic: false
---

The downhole sensor provides real-time measurements of bit orientation and position during drilling.

**Hardware:** Arduino Nano 33 BLE mounted in the sensor housing within the BHA.

**Measurements provided:**
- Inclination (deviation from vertical)
- Azimuth (compass direction)
- Bit position estimation using inertial data
- Accelerometer and gyroscope readings

**How it works:** The sensor uses inertial measurement (accelerometer + gyroscope) to track orientation. Data is transmitted via BLE to the surface system.

**Data integration:** Downhole measurements are combined with surface data (depth, torque, WOB) by the high-level control system for trajectory estimation and steering control.

**Location in BHA:** Mounted in the sensor housing between the upper stabilizer and the bent sub.
