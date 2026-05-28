---
id: drillbot-chat
title: Drillbot assistant chat
aliases:
  - drillbot chat
  - assistant
  - chat interface
  - how do I ask the assistant
  - drillbot assistant
  - rag assistant
  - help chat
  - ask a question
screen: left_monitor
component: drillbot_chat
raw_tags:
  - DrillbotChat
  - RAGAssistant
  - OperatorAssistant
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

The Drillbot chat interface provides an AI assistant to help operators with questions during drilling.

## Location

The chat panel appears on the left monitor, typically in the left column below the azimuth gauge.

## Using the Assistant

**To ask a question:**
1. Click in the text input field
2. Type your question
3. Press Enter or click Send

**Example questions:**
- "What does stuck bit mean?"
- "How do I start autonomous drilling?"
- "What is the WOB limit?"
- "How do I acknowledge an alarm?"

## What the Assistant Can Help With

- Alarm meanings and troubleshooting
- Operating procedures
- Joystick controls and buttons
- GUI features and displays
- System parameters and limits
- Autonomous state explanations
- Competition rules

## What the Assistant Cannot Do

- Read real-time values from sensors
- Control the rig or change settings
- Predict future events
- Access historical data from past runs

## Network Configuration

The assistant connects to a server at:
- Host: `10.22.61.83` (configurable)
- Port: `8000`
- Timeout: `120 seconds`

If the assistant doesn't respond, check network connectivity to the assistant server.
