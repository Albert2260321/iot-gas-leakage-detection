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
    min_gas = df["Gas Readings"].min()

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
        reason = "High gas concentration exceeded critical threshold."
    elif len(medium_risk) > 0 and len(high_temp) > 0:
        leak_detected = True
        reason = "Moderate gas combined with high temperature suggests leak risk."
    elif len(vibration_detected) > 0 and avg_gas < medium_threshold:
        leak_detected = False
        reason = "External vibration detected. Gas levels remain safe."
    else:
        reason = "System parameters within safe operating limits."

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

    st.write(f"High Gas Events: {len(high_risk)}")
    st.write(f"Medium Gas Events: {len(medium_risk)}")
    st.write(f"High Temperature Events: {len(high_temp)}")
    st.write(f"Vibration Events: {len(vibration_detected)}")

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
    # SMART RULE-BASED CHAT WITH MANY QUESTIONS
    # ----------------------------
    st.subheader("Smart Safety Assistant")

    suggested_questions = [
        "Is the system safe?",
        "Why is the valve closed?",
        "What caused the leak?",
        "What is the average gas level?",
        "What is the maximum gas level?",
        "What is the minimum gas level?",
        "How many high risk gas events occurred?",
        "How many medium risk events occurred?",
        "Are there temperature issues?",
        "How many high temperature events occurred?",
        "Is vibration causing the leak?",
        "How many vibration events occurred?",
        "What is the average temperature?",
        "What is the average vibration?",
        "Give executive summary",
        "Should management take action?",
        "Is immediate inspection required?",
        "What are the main risk factors?",
        "Explain current valve status",
        "Overall system health status"
    ]

    selected_question = st.selectbox(
        "Select a question:",
        ["-- Select a question --"] + suggested_questions
    )

    user_input = st.text_input("Or type your own question:")

    if user_input:
        q = user_input.lower()
    elif selected_question != "-- Select a question --":
        q = selected_question.lower()
    else:
        q = None

    if q:

        if "safe" in q:
            st.success("System is safe." if not leak_detected else "System is NOT safe.")

        elif "valve" in q:
            st.info(f"Valve is {'Closed' if valve_closed else 'Open'}. Reason: {reason}")

        elif "caused" in q or "risk factor" in q:
            st.info(reason)

        elif "average gas" in q:
            st.info(f"Average gas level: {round(avg_gas,2)}")

        elif "maximum gas" in q:
            st.info(f"Maximum gas level recorded: {max_gas}")

        elif "minimum gas" in q:
            st.info(f"Minimum gas level recorded: {min_gas}")

        elif "high risk" in q:
            st.info(f"High risk gas events: {len(high_risk)}")

        elif "medium risk" in q:
            st.info(f"Medium risk gas events: {len(medium_risk)}")

        elif "temperature issue" in q:
            st.info("Temperature risk detected." if len(high_temp) > 0 else "No temperature issues detected.")

        elif "high temperature" in q:
            st.info(f"High temperature events: {len(high_temp)}")

        elif "vibration causing" in q:
            if len(vibration_detected) > 0 and avg_gas < medium_threshold:
                st.info("Vibration detected but gas normal — likely external source.")
            else:
                st.info("No vibration-related leak detected.")

        elif "vibration event" in q:
            st.info(f"Total vibration events: {len(vibration_detected)}")

        elif "average temperature" in q:
            st.info(f"Average temperature: {round(avg_temp,2)}")

        elif "average vibration" in q:
            st.info(f"Average vibration: {round(avg_vib,2)}")

        elif "summary" in q or "health" in q:
            st.info(f"""
Executive Summary:
• Avg Gas: {round(avg_gas,2)}
• Max Gas: {max_gas}
• High Gas Events: {len(high_risk)}
• High Temp Events: {len(high_temp)}
• Valve Status: {"Closed" if valve_closed else "Open"}
""")

        elif "inspection" in q or "management" in q:
            if leak_detected:
                st.error("Immediate inspection recommended.")
            else:
                st.success("No immediate inspection required.")

        else:
            st.info("Please ask about gas, valve, safety, temperature, vibration, risk, inspection or summary.")

else:
    st.info("Upload a CSV file to begin monitoring.")