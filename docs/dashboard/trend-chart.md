---
id: trend-chart
title: Trend chart operations
aliases:
  - trend chart
  - how do I use the trend chart
  - what parameters are on the trend chart
  - trend traces
  - trend scaling
  - trend chart parameters
  - how do I scale the trend chart
  - trend window
screen: right_monitor
component: trend_chart
raw_tags:
  - TrendChart
  - TrendTraces
  - TrendScaling
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

The trend chart displays historical parameter data on the right monitor with a 240-second (4-minute) window.

## Available Parameters

| Parameter | Signal Name | Color |
|-----------|-------------|-------|
| Weight on Bit | WOB | Blue |
| WOB Setpoint | WOB_SP | Light Blue |
| Rate of Penetration | ROP | Pink-Purple |
| RPM | RPM | Teal-Green |
| RPM Setpoint | RPM_SP | Light Teal |
| Azimuth | AZIMUTH | Gray |
| Top Drive Torque | TD_TOR | Orange |
| Hoisting Torque | HOIST_TOR | Vermillion |
| Measured Depth | MD | Black |
| True Vertical Depth | TVD | Dark Gray |
| Flow | FLOW | Sky Blue |
| Pressure | PRESSURE | Wine |
| Raw WOB | WOB_RAW | Indigo |

## Scaling Individual Parameters

1. **Click** on a trend line or its legend label to select it
2. **Scroll** mouse wheel to zoom the Y-axis in or out
3. **Drag up/down** to pan the scale range
4. **Double-click** the legend to reset to default scale

## Right-Click Menu Options

- **Scaling Presets** - Choose predefined scale ranges
- **Show/Hide Events** - Toggle alarm event markers
- **Clear** - Reset the trend data

## Alarm Event Markers

The trend chart shows annotations when alarms occur:
- **STUCK** - Stuck bit event
- **WOB!** - Critical WOB event
- **LIFT** - Bit lifted event
- **MD** - MD target reached
