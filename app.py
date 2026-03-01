import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from datetime import datetime
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
# FILE UPLOAD
# ----------------------------
uploaded_file = st.file_uploader("Upload IoT Sensor CSV File", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # Ensure correct columns
    df.columns = df.columns.str.strip()

    # ----------------------------
    # BASIC METRICS
    # ----------------------------
    avg_gas = df["Gas Readings"].mean()
    avg_temp = df["Temperature"].mean()
    avg_vib = df["Vibration"].mean()

    max_gas = df["Gas Readings"].max()

    # Risk thresholds
    high_risk_count = len(df[df["Gas Readings"] > 700])
    medium_risk_count = len(df[(df["Gas Readings"] > 400) & (df["Gas Readings"] <= 700)])

    valve_closed = high_risk_count > 0

    # ----------------------------
    # DASHBOARD CARDS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average Gas Level", round(avg_gas, 2))
    col2.metric("Average Temperature", round(avg_temp, 2))
    col3.metric("Average Vibration", round(avg_vib, 2))
    col4.metric("High Risk Events", high_risk_count)

    # ----------------------------
    # VALVE STATUS
    # ----------------------------
    st.subheader("Automatic Safety Valve Status")

    if valve_closed:
        st.error("VALVE CLOSED - HIGH GAS DETECTED")
    else:
        st.success("VALVE OPEN - SYSTEM SAFE")

    # ----------------------------
    # RISK CLASSIFICATION
    # ----------------------------
    st.subheader("Risk Classification")

    if high_risk_count > 0:
        st.error("HIGH RISK: Immediate inspection required.")
    elif medium_risk_count > 0:
        st.warning("MEDIUM RISK: Monitor system closely.")
    else:
        st.success("LOW RISK: System operating normally.")

    # ----------------------------
    # GRAPHS
    # ----------------------------
    st.subheader("Sensor Trends")

    st.line_chart(df["Gas Readings"])

    st.subheader("Temperature Trends")
    st.line_chart(df["Temperature"])

    st.subheader("Vibration Trends (Enhanced Visibility)")
    st.line_chart(df["Vibration"] * 10)  # multiplied for clarity

    # ----------------------------
    # EXECUTIVE SUMMARY
    # ----------------------------
    st.subheader("Executive Safety Summary")

    summary_text = f"""
    The monitoring system recorded an average gas concentration of {round(avg_gas,2)} units.
    A total of {high_risk_count} high-risk events were detected.
    The maximum gas reading reached {max_gas} units.
    Valve status is currently {"CLOSED due to high gas detection." if valve_closed else "OPEN and operating normally."}
    """

    st.write(summary_text)

    # ----------------------------
    # DOWNLOAD REPORT
    # ----------------------------
    st.subheader("Download Incident Report")

    report_df = pd.DataFrame({
        "Metric": ["Average Gas", "Average Temp", "Average Vibration", "High Risk Events", "Valve Status"],
        "Value": [
            round(avg_gas,2),
            round(avg_temp,2),
            round(avg_vib,2),
            high_risk_count,
            "Closed" if valve_closed else "Open"
        ]
    })

    buffer = BytesIO()
    report_df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="Download Report as CSV",
        data=buffer,
        file_name="gas_safety_report.csv",
        mime="text/csv"
    )

    # ----------------------------
    # GEMINI AI SECTION
    # ----------------------------
    st.subheader("AI Safety Assistant")

    st.write("Example prompts:")
    st.write("- Is the system safe?")
    st.write("- Provide executive safety summary.")
    st.write("- What risks should management address?")
    st.write("- Suggest preventive measures.")

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")

        user_input = st.text_input("Ask anything about the system status...")

        if user_input:

            data_summary = f"""
            Average Gas: {avg_gas}
            Average Temperature: {avg_temp}
            Average Vibration: {avg_vib}
            High Risk Events: {high_risk_count}
            Maximum Gas Level: {max_gas}
            Valve Status: {"Closed" if valve_closed else "Open"}
            """

            prompt = f"""
            You are an industrial IoT gas safety monitoring assistant.

            System data:
            {data_summary}

            User question:
            {user_input}

            Provide a professional, concise, safety-focused answer.
            """

            response = model.generate_content(prompt)
            st.info(response.text)

    except Exception as e:
        st.warning("AI Assistant not configured properly. Please check API key.")