---
id: udp-signals
title: UDP telemetry signal reference
aliases:
  - udp signals
  - telemetry signals
  - what signals are available
  - signal names
  - data fields
  - telemetry reference
  - what data comes from the rig
screen: null
component: data_acquisition
raw_tags:
  - UDP
  - Telemetry
  - DataSource
  - SignalNames
status: confirmed_on_current_rig
source_type: telemetry_definition
historic: false
---

# UDP Telemetry Signal Reference

The GUI receives real-time data from the rig via UDP on port 5005.

## Core Drilling Parameters

| Signal Name | Unit | Description |
|-------------|------|-------------|
| `time` | s | Timestamp |
| `WOB` | kN | Weight on bit (measured) |
| `WOBSetpoint` | kN | WOB target value |
| `ROP` | cm/min | Rate of penetration |
| `ROPSetpoint` | cm/min | ROP target value |
| `TopDriveRPM` | rpm | Rotation speed (measured) |
| `TopDriveRPMSetpoint` | rpm | RPM target value |
| `TopDriveTorque` | kN·m | Drive torque |
| `HoistingTorque` | kN·m | Hoisting torque |
| `HoistingPosition` | cm | Measured depth (MD) |

## Position & Orientation

| Signal Name | Unit | Description |
|-------------|------|-------------|
| `PositionX` | m | X coordinate |
| `PositionY` | m | Y coordinate |
| `PositionZ` | cm | Z coordinate (TVD) |
| `AzimuthOrientation` | ° | Current azimuth (0-360) |
| `AzimuthTarget` | ° | Target azimuth angle |
| `AzimuthSetpoint` | ° | Azimuth setpoint (alt) |
| `AzimuthRotationVelocity` | °/s | Azimuth angular velocity |

## Autonomous State

| Signal Name | Values | Description |
|-------------|--------|-------------|
| `AutonomousOperationCurrentState` | 0-5 | Current state ID |

State values: 0=Init, 1=Vertical, 2=Target Intersection, 3=To Exit, 4=Exit Detection, 5=Completed

## Alarm Flags

| Signal Name | Type | Description |
|-------------|------|-------------|
| `isStuckBit` | bool | Stuck bit condition (>0.5 = true) |
| `isRodWindup` | bool | Rod windup condition |
| `MDTargetReached` | bool | Target depth reached |
| `LithologyChange` | bool | Formation change detected |

## Joystick Feedback

| Signal Name | Range | Description |
|-------------|-------|-------------|
| `JoystickFeedbackMode` | 1-4 | Vibration mode selection |
| `JoystickGainLeft` | 0-1 | Left stick vibration intensity |
| `JoystickGainRight` | 0-1 | Right stick vibration intensity |
| `DismissAlarm` | 0/1 | Dismiss alarm trigger |

## Optional Sensors

| Signal Name | Unit | Description |
|-------------|------|-------------|
| `Flow` | L/min | Flow rate |
| `Pressure` | bar | Fluid pressure |
| `WOBRaw` | kN | Raw WOB reading |
| `ArduinoConnected` | bool | Downhole sensor status |
| `IsDownholeSignal` | bool | Downhole signal valid |
