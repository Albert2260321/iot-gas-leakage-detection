import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.graph_objects as go

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Smart Gas Leakage Monitoring System",
    layout="wide"
)

st.title("Smart Gas Leakage Detection & Prevention System")

# ----------------------------
# SIDEBAR - THRESHOLDS
# ----------------------------
st.sidebar.header("Risk Threshold Configuration")

medium_threshold = st.sidebar.slider("Medium Gas Threshold", 100, 1000, 400)
high_threshold = st.sidebar.slider("High Gas Threshold", 200, 1500, 700)
temp_threshold = st.sidebar.slider("High Temperature Threshold", 30, 150, 80)

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
    # RISK SCORE CALCULATION
    # ----------------------------
    gas_score = min((avg_gas / high_threshold) * 50, 50)
    temp_score = min((avg_temp / temp_threshold) * 30, 30)
    vibration_score = min((avg_vib * 20), 20)

    risk_score = round(gas_score + temp_score + vibration_score)

    # ----------------------------
    # SEVERITY CLASSIFICATION
    # ----------------------------
    if risk_score < 30:
        severity_color = "green"
        severity_label = "LOW RISK"
    elif risk_score < 60:
        severity_color = "orange"
        severity_label = "MEDIUM RISK"
    else:
        severity_color = "red"
        severity_label = "HIGH RISK"

    # ----------------------------
    # METRICS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average Gas", round(avg_gas, 2))
    col2.metric("Average Temperature", round(avg_temp, 2))
    col3.metric("Average Vibration", round(avg_vib, 2))
    col4.metric("Max Gas", max_gas)

    # ----------------------------
    # SEVERITY DISPLAY
    # ----------------------------
    st.subheader("Risk Severity Level")
    st.markdown(
        f"<h2 style='color:{severity_color};'>{severity_label}</h2>",
        unsafe_allow_html=True
    )

    # ----------------------------
    # RISK GAUGE
    # ----------------------------
    st.subheader("Overall Risk Score (0–100)")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': severity_color},
            'steps': [
                {'range': [0, 30], 'color': "green"},
                {'range': [30, 60], 'color': "orange"},
                {'range': [60, 100], 'color': "red"},
            ],
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # VALVE STATUS
    # ----------------------------
    st.subheader("Automatic Safety Valve Status")

    if risk_score >= 60:
        st.error("🔴 VALVE CLOSED — Leak Prevention Activated")
    else:
        st.success("🟢 VALVE OPEN — System Operating Normally")

    # ----------------------------
    # PLOTLY HEATMAP (FIXED)
    # ----------------------------
    st.subheader("Gas Risk Heatmap")

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=[df["Gas Readings"].values],
        colorscale="Reds"
    ))

    fig_heatmap.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # ----------------------------
    # TRENDS
    # ----------------------------
    st.subheader("Gas Trend")
    st.line_chart(df["Gas Readings"])

    st.subheader("Temperature Trend")
    st.line_chart(df["Temperature"])

    st.subheader("Vibration Trend (Amplified)")
    st.line_chart(df["Vibration"] * 10)

    # ----------------------------
    # DOWNLOAD REPORT
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
    # SMART ASSISTANT
    # ----------------------------
    st.subheader("Smart Safety Assistant")

    questions = [
        "Is the system safe?",
        "What is the risk score?",
        "What is the risk severity?",
        "Explain valve status",
        "Should inspection be done?",
        "What is the average gas level?",
        "What is the maximum gas level?",
        "How many high gas events occurred?",
        "How many high temperature events occurred?",
        "How many vibration events occurred?",
        "Give executive summary",
        "Overall system health status"
    ]

    selected = st.selectbox("Select a question:", ["-- Select --"] + questions)
    user_input = st.text_input("Or type your own question:")

    if user_input:
        q = user_input.lower()
    elif selected != "-- Select --":
        q = selected.lower()
    else:
        q = None

    if q:
        if "safe" in q:
            st.success("System is safe." if risk_score < 60 else "System is NOT safe.")
        elif "risk score" in q:
            st.info(f"Overall risk score is {risk_score}/100.")
        elif "severity" in q:
            st.info(f"Current severity level: {severity_label}.")
        elif "valve" in q:
            st.info("Valve is Closed." if risk_score >= 60 else "Valve is Open.")
        elif "inspection" in q:
            st.warning("Inspection recommended." if risk_score >= 60 else "Inspection not required.")
        elif "average gas" in q:
            st.info(f"Average gas level: {round(avg_gas,2)}")
        elif "maximum gas" in q:
            st.info(f"Maximum gas level recorded: {max_gas}")
        elif "high gas" in q:
            st.info(f"High gas events: {len(high_risk)}")
        elif "temperature" in q:
            st.info(f"High temperature events: {len(high_temp)}")
        elif "vibration" in q:
            st.info(f"Vibration events: {len(vibration_detected)}")
        elif "summary" in q or "health" in q:
            st.info(f"""
Executive Summary:
• Risk Score: {risk_score}
• Severity: {severity_label}
• Avg Gas: {round(avg_gas,2)}
• High Gas Events: {len(high_risk)}
• High Temp Events: {len(high_temp)}
""")
        else:
            st.info("Please ask about risk, safety, valve, inspection, gas, temperature or summary.")

else:
    st.info("Upload a CSV file to begin monitoring.")