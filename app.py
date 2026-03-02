import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.graph_objects as go

# ----------------------------
# PROFESSIONAL DARK THEME
# ----------------------------
st.set_page_config(
    page_title="Smart Gas Leakage Monitoring System",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.metric-box {
    padding: 10px;
    border-radius: 10px;
    background-color: #1C1F26;
}
</style>
""", unsafe_allow_html=True)

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

    high_risk = df[df["Gas Readings"] > high_threshold]
    medium_risk = df[(df["Gas Readings"] > medium_threshold) &
                     (df["Gas Readings"] <= high_threshold)]
    high_temp = df[df["Temperature"] > temp_threshold]

    # ----------------------------
    # RISK SCORE CALCULATION (0–100)
    # ----------------------------
    gas_score = min((avg_gas / high_threshold) * 50, 50)
    temp_score = min((avg_temp / temp_threshold) * 30, 30)
    vibration_score = min((avg_vib * 20), 20)

    risk_score = round(gas_score + temp_score + vibration_score)

    # ----------------------------
    # RISK SEVERITY COLOR
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

    col1.metric("Average Gas", round(avg_gas,2))
    col2.metric("Average Temp", round(avg_temp,2))
    col3.metric("Average Vibration", round(avg_vib,2))
    col4.metric("Max Gas", max_gas)

    # ----------------------------
    # RISK SEVERITY SCALE
    # ----------------------------
    st.subheader("Risk Severity Level")

    st.markdown(f"""
    <h2 style='color:{severity_color};'>{severity_label}</h2>
    """, unsafe_allow_html=True)

    # ----------------------------
    # RISK SCORE GAUGE
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
    st.subheader("Valve Status")

    if risk_score >= 60:
        st.error("🔴 VALVE CLOSED — Automatic Leak Prevention Activated")
    else:
        st.success("🟢 VALVE OPEN — System Stable")

    # ----------------------------
    # HEATMAP TABLE
    # ----------------------------
    st.subheader("Gas Risk Heatmap")

    st.dataframe(
        df.style.background_gradient(
            subset=["Gas Readings"],
            cmap="Reds"
        )
    )

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
    # SMART CHAT
    # ----------------------------
    st.subheader("Smart Safety Assistant")

    questions = [
        "Is the system safe?",
        "What is the risk score?",
        "What is the risk severity?",
        "Should inspection be done?",
        "Explain valve status",
        "Give executive summary"
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
        elif "inspection" in q:
            if risk_score >= 60:
                st.error("Immediate inspection recommended.")
            else:
                st.success("No immediate inspection required.")
        elif "valve" in q:
            st.info("Valve is Closed." if risk_score >= 60 else "Valve is Open.")
        elif "summary" in q:
            st.info(f"""
Executive Summary:
• Risk Score: {risk_score}
• Severity: {severity_label}
• Avg Gas: {round(avg_gas,2)}
• High Gas Events: {len(high_risk)}
• High Temp Events: {len(high_temp)}
""")
        else:
            st.info("Ask about risk, safety, valve, inspection or summary.")

else:
    st.info("Upload a CSV file to begin monitoring.")