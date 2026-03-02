import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Smart Gas Leakage Monitoring System",
    layout="wide"
)

st.title("Smart Gas Leakage Detection & Prevention System")

# ----------------------------
# SIDEBAR - THRESHOLD SETTINGS
# ----------------------------
st.sidebar.header("Risk Threshold Configuration")

medium_threshold = st.sidebar.slider(
    "Medium Gas Threshold",
    min_value=100,
    max_value=1000,
    value=400
)

high_threshold = st.sidebar.slider(
    "High Gas Threshold",
    min_value=200,
    max_value=1500,
    value=700
)

temp_threshold = st.sidebar.slider(
    "High Temperature Threshold",
    min_value=30,
    max_value=150,
    value=80
)

# ----------------------------
# FILE UPLOAD
# ----------------------------
uploaded_file = st.file_uploader("Upload IoT Sensor CSV File", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    df["Gas Readings"] = pd.to_numeric(df["Gas Readings"], errors="coerce")
    df["Temperature"] = pd.to_numeric(df["Temperature"], errors="coerce")
    df["Vibration"] = pd.to_numeric(df["Vibration"], errors="coerce")

    avg_gas = df["Gas Readings"].mean()
    avg_temp = df["Temperature"].mean()
    avg_vib = df["Vibration"].mean()
    max_gas = df["Gas Readings"].max()

    high_risk = df[df["Gas Readings"] > high_threshold]
    medium_risk = df[(df["Gas Readings"] > medium_threshold) & 
                     (df["Gas Readings"] <= high_threshold)]

    high_temp = df[df["Temperature"] > temp_threshold]
    vibration_detected = df[df["Vibration"] > 0]

    # ----------------------------
    # Leak Logic
    # ----------------------------
    leak_detected = False
    reason = ""

    if len(high_risk) > 0:
        leak_detected = True
        reason = "High gas concentration detected above critical threshold."
    elif len(medium_risk) > 0 and len(high_temp) > 0:
        leak_detected = True
        reason = "Moderate gas combined with high temperature suggests leak risk."
    elif len(vibration_detected) > 0 and avg_gas < medium_threshold:
        leak_detected = False
        reason = "Vibration detected but gas levels are safe — likely external disturbance."
    else:
        reason = "System parameters within safe limits."

    valve_closed = leak_detected

    # ----------------------------
    # METRICS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average Gas", round(avg_gas, 2))
    col2.metric("Average Temperature", round(avg_temp, 2))
    col3.metric("Average Vibration", round(avg_vib, 2))
    col4.metric("Max Gas", max_gas)

    # ----------------------------
    # VALVE STATUS
    # ----------------------------
    st.subheader("Automatic Safety Valve Status")

    if valve_closed:
        st.error("VALVE CLOSED — Leak Prevention Activated")
    else:
        st.success("VALVE OPEN — System Operating Normally")

    st.write("Reason:", reason)

    # ----------------------------
    # ALERT DETAILS
    # ----------------------------
    st.subheader("Detected Events")

    if len(high_risk) > 0:
        st.error(f"{len(high_risk)} High Gas Events Detected")

    if len(high_temp) > 0:
        st.warning(f"{len(high_temp)} High Temperature Events Detected")

    if len(vibration_detected) > 0:
        st.info(f"{len(vibration_detected)} Vibration Events Detected")

    # ----------------------------
    # GRAPHS
    # ----------------------------
    st.subheader("Gas Trend")
    st.line_chart(df["Gas Readings"])

    st.subheader("Temperature Trend")
    st.line_chart(df["Temperature"])

    st.subheader("Vibration Trend (Amplified)")
    st.line_chart(df["Vibration"] * 10)

    # ----------------------------
    # REPORT DOWNLOAD
    # ----------------------------
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="Download Sensor Report",
        data=buffer,
        file_name="sensor_report.csv",
        mime="text/csv"
    )

    # ----------------------------
    # SMART RULE-BASED CHAT
    # ----------------------------
    st.subheader("Smart Safety Assistant")

    user_input = st.text_input("Ask about system status...")

    if user_input:

        q = user_input.lower()

        if "safe" in q:
            if leak_detected:
                st.error("System is NOT safe. Immediate inspection required.")
            else:
                st.success("System is currently safe.")

        elif "why valve" in q:
            st.info(reason)

        elif "average gas" in q:
            st.info(f"Average gas level is {round(avg_gas,2)}")

        elif "high risk" in q:
            st.info(f"There are {len(high_risk)} high risk gas events.")

        elif "temperature" in q:
            st.info(f"Average temperature is {round(avg_temp,2)}")

        elif "vibration" in q:
            st.info("Vibration detected. If gas is low, likely external disturbance.")

        elif "summary" in q:
            st.info(f"""
            Executive Summary:
            - Average Gas: {round(avg_gas,2)}
            - Max Gas: {max_gas}
            - High Risk Events: {len(high_risk)}
            - High Temperature Events: {len(high_temp)}
            - Valve Status: {"Closed" if valve_closed else "Open"}
            """)

        else:
            st.info("Please ask about safety, valve, gas levels, temperature, vibration, risk, or summary.")

else:
    st.info("Upload a CSV file to begin monitoring.")