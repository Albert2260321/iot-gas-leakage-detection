import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Industrial Gas Safety System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Custom Industrial Styling
# ----------------------------
st.markdown("""
    <style>
        body {background-color: #0e1117;}
        .stMetric {background-color: #1c1f26; padding: 15px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("Industrial IoT Gas Leakage Detection & Prevention System")
st.markdown("Real-Time Monitoring | Automated Valve Control | AI Decision Support")

# ----------------------------
# Sidebar Control Panel
# ----------------------------
st.sidebar.header("System Control Panel")

threshold_low = st.sidebar.slider("Medium Risk Threshold", 200, 400, 250)
threshold_high = st.sidebar.slider("High Risk Threshold", 300, 600, 400)

uploaded_file = st.sidebar.file_uploader("Upload Sensor CSV", type=["csv"])

if uploaded_file is not None:

    # ----------------------------
    # Load & Clean Data
    # ----------------------------
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # Force numeric conversion
    df["Gas Readings"] = pd.to_numeric(df["Gas Readings"], errors="coerce")
    df["Temperature"] = pd.to_numeric(df["Temperature"], errors="coerce")
    df["Vibration"] = pd.to_numeric(df["Vibration"], errors="coerce")

    total_records = len(df)
    avg_gas = df["Gas Readings"].mean()
    max_gas = df["Gas Readings"].max()
    avg_temp = df["Temperature"].mean()
    max_temp = df["Temperature"].max()
    avg_vibration = df["Vibration"].mean()

    # ----------------------------
    # Risk Classification
    # ----------------------------
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

    # ----------------------------
    # Dashboard Metrics
    # ----------------------------
    st.subheader("System Performance Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", total_records)
    col2.metric("Average Gas", round(avg_gas, 2))
    col3.metric("Average Temperature", round(avg_temp, 2))
    col4.metric("Average Vibration", round(avg_vibration, 2))

    st.divider()

    # ----------------------------
    # Risk Display
    # ----------------------------
    st.subheader("Safety Risk Analysis")

    if high_risk_count > 0:
        st.error(f"{high_risk_count} HIGH-RISK EVENTS DETECTED")
    else:
        st.success("System Stable — No Critical Leak Detected")

    st.markdown("### Valve Control System")

    if shutoff_status == "ACTIVATED":
        st.markdown("🟥 **EMERGENCY SHUTOFF ACTIVATED**")
    else:
        st.markdown("🟩 **VALVE IN STANDBY MODE**")

    st.divider()

    # ----------------------------
    # Sensor Visualizations
    # ----------------------------
    st.subheader("Gas Level Trend")
    st.line_chart(df["Gas Readings"])

    st.subheader("Temperature Trend")
    st.line_chart(df["Temperature"])

    st.subheader("Vibration Activity (Binary Detection)")
    st.bar_chart(df["Vibration"])

    vibration_events = df["Vibration"].sum()
    st.write(f"Total Vibration Trigger Events: {int(vibration_events)}")

    st.divider()

    # ----------------------------
    # AI Monitoring Assistant
    # ----------------------------
    st.subheader("AI Monitoring Assistant")

    st.markdown("### Example Questions:")
    st.markdown("""
    - What is average gas level?
    - What is maximum gas reading?
    - How many high risk events?
    - What is valve status?
    - Give system summary
    """)

    user_query = st.text_input("Enter your question:")

    def ai_response(query):
        query = query.lower()

        if "average gas" in query:
            return f"Average gas concentration is {round(avg_gas,2)} units."

        elif "maximum gas" in query or "max gas" in query:
            return f"Maximum recorded gas concentration is {round(max_gas,2)} units."

        elif "average temperature" in query:
            return f"Average temperature is {round(avg_temp,2)} degrees."

        elif "maximum temperature" in query:
            return f"Maximum recorded temperature is {round(max_temp,2)} degrees."

        elif "high risk" in query or "leak" in query:
            return f"There are {high_risk_count} high-risk leakage events detected."

        elif "valve" in query:
            return f"Valve status is currently {shutoff_status}."

        elif "summary" in query:
            return f"The system analyzed {total_records} records. Maximum gas: {round(max_gas,2)}. High-risk events: {high_risk_count}. Valve status: {shutoff_status}."

        else:
            return "Please ask about gas levels, temperature, risks, valve status, or system summary."

    if user_query:
        st.info(ai_response(user_query))

    st.divider()

    # ----------------------------
    # Footer
    # ----------------------------
    st.caption(f"Monitoring Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.info("Upload sensor CSV from the sidebar to activate monitoring system.")