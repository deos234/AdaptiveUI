#!/usr/bin/env python
# coding: utf-8

# In[9]:

import streamlit as st
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER_ADDRESS = "localhost"  # Update with your broker address
BROKER_PORT = 1883            # Default MQTT port
LIGHT_TOPIC = "home/lights/living-room"
THERMOSTAT_TOPIC = "home/thermostat/temperature"

# MQTT Client Setup
client = mqtt.Client()

# Connect to the MQTT broker
try:
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    client.loop_start()  # Start the loop for background MQTT operations
    st.success("Connected to MQTT Broker")
except Exception as e:
    st.error(f"Failed to connect to MQTT Broker: {e}")

# Initialize session state variables
if "light_status" not in st.session_state:
    st.session_state.light_status = "off"

if "thermostat_temp" not in st.session_state:
    st.session_state.thermostat_temp = 72  # Default temperature

if "usage_history" not in st.session_state:
    st.session_state.usage_history = {"light_control": 0, "thermostat_control": 0}

# Simulate context-aware defaults
current_hour = datetime.now().hour
if 18 <= current_hour <= 6:  # Evening to early morning
    st.session_state.light_status = "off"

st.title("Smart Home Control Panel")

# UI Component Ordering Logic
components = [
    {"name": "light_control", "count": st.session_state.usage_history["light_control"], "function": None},
    {"name": "thermostat_control", "count": st.session_state.usage_history["thermostat_control"], "function": None},
]
components.sort(key=lambda x: x["count"], reverse=True)

# Define Functions for Light and Thermostat Controls
def light_control():
    st.header("Light Control")
    light_status = st.radio("Light Status:", ["on", "off"], index=0 if st.session_state.light_status == "on" else 1)
    if light_status != st.session_state.light_status:
        st.session_state.light_status = light_status
        # Publish to MQTT
        client.publish(LIGHT_TOPIC, light_status)
        st.write(f"Light turned {light_status}. MQTT message sent.")
        # Increment interaction count
        st.session_state.usage_history["light_control"] += 1

def thermostat_control():
    st.header("Thermostat Control")
    thermostat_temp = st.slider("Set Temperature (°F):", 60, 80, value=st.session_state.thermostat_temp)
    if thermostat_temp != st.session_state.thermostat_temp:
        st.session_state.thermostat_temp = thermostat_temp
        # Publish to MQTT
        client.publish(THERMOSTAT_TOPIC, thermostat_temp)
        st.write(f"Temperature set to {thermostat_temp}°F. MQTT message sent.")
        # Increment interaction count
        st.session_state.usage_history["thermostat_control"] += 1

# Assign Functions to Components
for component in components:
    if component["name"] == "light_control":
        component["function"] = light_control
    elif component["name"] == "thermostat_control":
        component["function"] = thermostat_control

# Render Components Based on Interaction Frequency
for component in components:
    component["function"]()

# Cleanup MQTT connection
if st.button("Stop MQTT"):
    client.loop_stop()
    client.disconnect()
    st.success("MQTT connection stopped.")