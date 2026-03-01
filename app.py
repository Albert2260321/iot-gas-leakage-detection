import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Industrial Gas Safety System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# Custom Styling
# ----------------------
st.markdown("""
    <style>
        body {background-color: #0e1117;}
        .stMetric {background-color: #1c1f26; padding: 15px; border-radius: 10px;}
        .big-font {font-size:22px !important;}
    </style>
""", unsafe_allow_html=True)

st.title("Industrial IoT Gas Leakage Detection & Prevention")
st.markdown("Real-Time Monitoring | Automated Safety Response | AI Decision Support")

# ----------------------
# Sidebar Control Panel
# ----------------------
st.sidebar.header("System Control Panel")

threshold_low = st.sidebar.slider("Medium Risk Threshold", 200, 400, 250)
threshold_high = st.sidebar.slider("High Risk Threshold", 300, 600, 400)

uploaded_file = st.sidebar.file_uploader("Upload Sensor CSV", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    total_records = len(df)
    avg_gas = df["Gas Readings"].mean()
    max_gas = df["Gas Readings"].max()
    avg_temp = df["Temperature"].mean()
    avg_vibration = df["Vibration"].mean()

    # Risk Classification
    def classify_risk(value):
        if value > threshold_high:
            return "HIGH"
        elif value > threshold_low:
            return "MEDIUM"
        else:
            return "LOW"

    df["Risk Level"] = df["Gas Readings"].apply(classify_risk)
    high_risk_count = len(df[df["Risk Level"] == "HIGH"])

    shutoff_status = "ACTIVATED" if high_risk_count > 0 else "STANDBY"

    # ----------------------
    # Dashboard Layout
    # ----------------------
    st.subheader("System Performance Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", total_records)
    col2.metric("Average Gas", round(avg_gas, 2))
    col3.metric("Average Temp", round(avg_temp, 2))
    col4.metric("Average Vibration", round(avg_vibration, 2))

    st.divider()

    # Risk Display
    st.subheader("Safety Risk Analysis")

    if high_risk_count > 0:
        st.error(f"{high_risk_count} HIGH-RISK EVENTS DETECTED")
    else:
        st.success("System Stable — No Critical Leak Detected")

    # Valve Indicator
    st.markdown("### Valve Control System")
    if shutoff_status == "ACTIVATED":
        st.markdown("🟥 **EMERGENCY SHUTOFF ACTIVATED**")
    else:
        st.markdown("🟩 **VALVE IN STANDBY MODE**")

    st.divider()

    # Charts
    st.subheader("Live Sensor Trends")
    st.line_chart(df[["Gas Readings", "Temperature", "Vibration"]])

    st.divider()

    # ----------------------
    # AI Assistant
    # ----------------------
    st.subheader("AI Monitoring Assistant")

    user_query = st.text_input("Ask system status or statistics:")

    def ai_response(query):
        query = query.lower()

        if "average gas" in query:
            return f"Average gas concentration is {round(avg_gas,2)} units."

        elif "max gas" in query or "maximum gas" in query:
            return f"Maximum recorded gas concentration is {round(max_gas,2)} units."

        elif "risk" in query:
            return f"There are {high_risk_count} high-risk leakage events."

        elif "valve" in query:
            return f"Valve status is currently {shutoff_status}."

        elif "summary" in query:
            return f"{total_records} records analyzed. Max gas: {round(max_gas,2)}. Valve: {shutoff_status}."

        else:
            return "I can provide gas statistics, temperature stats, risk assessment, or system summary."

    if user_query:
        st.info(ai_response(user_query))

else:
    st.info("Upload sensor CSV from the sidebar to activate monitoring system.")