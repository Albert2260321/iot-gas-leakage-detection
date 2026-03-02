import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import google.generativeai as genai

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
    "Medium Risk Threshold (Gas Level)",
    min_value=100,
    max_value=1000,
    value=400
)

high_threshold = st.sidebar.slider(
    "High Risk Threshold (Gas Level)",
    min_value=200,
    max_value=1500,
    value=700
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

    # ----------------------------
    # RISK CLASSIFICATION
    # ----------------------------
    high_risk_count = len(df[df["Gas Readings"] > high_threshold])
    medium_risk_count = len(
        df[(df["Gas Readings"] > medium_threshold) &
           (df["Gas Readings"] <= high_threshold)]
    )

    valve_closed = high_risk_count > 0

    # ----------------------------
    # DASHBOARD METRICS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average Gas", round(avg_gas, 2))
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
    # RISK LEVEL
    # ----------------------------
    st.subheader("Risk Evaluation")

    if high_risk_count > 0:
        st.error("HIGH RISK - Immediate inspection required.")
    elif medium_risk_count > 0:
        st.warning("MEDIUM RISK - Increased monitoring recommended.")
    else:
        st.success("LOW RISK - System operating normally.")

    # ----------------------------
    # GRAPHS
    # ----------------------------
    st.subheader("Gas Trend")
    st.line_chart(df["Gas Readings"])

    st.subheader("Temperature Trend")
    st.line_chart(df["Temperature"])

    st.subheader("Vibration Trend (Enhanced Visibility)")
    st.line_chart(df["Vibration"] * 10)

    # ----------------------------
    # EXECUTIVE SUMMARY
    # ----------------------------
    st.subheader("Executive Safety Summary")

    summary = f"""
    Average Gas Level: {round(avg_gas,2)}
    Maximum Gas Level: {max_gas}
    High Risk Events: {high_risk_count}
    Medium Risk Events: {medium_risk_count}
    Valve Status: {"Closed" if valve_closed else "Open"}
    Medium Threshold: {medium_threshold}
    High Threshold: {high_threshold}
    """

    st.write(summary)

    # ----------------------------
    # REPORT DOWNLOAD
    # ----------------------------
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="Download Full Sensor Data",
        data=buffer,
        file_name="sensor_report.csv",
        mime="text/csv"
    )

    # ----------------------------
    # GEMINI AI SECTION (STABLE MODEL)
    # ----------------------------
    st.subheader("AI Industrial Safety Assistant")

    st.write("Example prompts:")
    st.write("- Is the system safe?")
    st.write("- What risks should management address?")
    st.write("- Suggest mitigation strategies.")
    st.write("- Provide executive safety summary.")

    user_input = st.text_input("Ask about system status...")

    if user_input:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

            # ✅ Using universally supported model
            model = genai.GenerativeModel("gemini-pro")

            context = f"""
            Gas Average: {avg_gas}
            Gas Maximum: {max_gas}
            High Risk Events: {high_risk_count}
            Medium Risk Events: {medium_risk_count}
            Valve Status: {"Closed" if valve_closed else "Open"}
            Medium Threshold: {medium_threshold}
            High Threshold: {high_threshold}
            """

            prompt = f"""
            You are an industrial IoT gas safety monitoring AI assistant.

            System Data:
            {context}

            User Question:
            {user_input}

            Provide a professional safety-focused response.
            """

            response = model.generate_content(prompt)

            st.info(response.text)

        except Exception as e:
            st.error("AI Error:")
            st.write(e)

else:
    st.info("Upload a CSV file to begin monitoring.")