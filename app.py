import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.pagesizes import letter

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Smart Gas Leakage Monitoring System",
    layout="wide"
)

st.title("Smart Gas Leakage Detection & Prevention System")

# ----------------------------
# SIDEBAR THRESHOLDS
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
    vibration_detected = df[df["Vibration"] > 0]

    leak_detected = False
    reason = ""

    if len(high_risk) > 0:
        leak_detected = True
        reason = "Critical gas threshold exceeded."
    elif len(medium_risk) > 0 and len(high_temp) > 0:
        leak_detected = True
        reason = "Moderate gas with high temperature suggests possible leak."
    elif len(vibration_detected) > 0 and avg_gas < medium_threshold:
        leak_detected = False
        reason = "External vibration detected. Gas levels normal."
    else:
        reason = "System parameters within safe limits."

    valve_closed = leak_detected

    # ----------------------------
    # METRICS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Gas", round(avg_gas,2))
    col2.metric("Average Temp", round(avg_temp,2))
    col3.metric("Average Vibration", round(avg_vib,2))
    col4.metric("Max Gas", max_gas)

    # ----------------------------
    # ANIMATED VALVE INDICATOR
    # ----------------------------
    st.subheader("Valve Status")

    if valve_closed:
        st.markdown("### 🔴 VALVE CLOSED")
        st.markdown("⚠️ Leak prevention activated.")
    else:
        st.markdown("### 🟢 VALVE OPEN")
        st.markdown("System operating normally.")

    st.write("Reason:", reason)

    # ----------------------------
    # RISK HEATMAP
    # ----------------------------
    st.subheader("Risk Heatmap")

    risk_df = df.copy()
    risk_df["Risk Level"] = np.where(
        risk_df["Gas Readings"] > high_threshold, 2,
        np.where(risk_df["Gas Readings"] > medium_threshold, 1, 0)
    )

    st.dataframe(
        risk_df.style.background_gradient(
            subset=["Gas Readings"],
            cmap="Reds"
        )
    )

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
    # PDF REPORT GENERATION
    # ----------------------------
    st.subheader("Generate Professional PDF Report")

    if st.button("Generate PDF Report"):

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Smart Gas Leakage Monitoring Report", styles['Title']))
        elements.append(Spacer(1, 12))

        report_data = [
            ["Average Gas", round(avg_gas,2)],
            ["Max Gas", max_gas],
            ["High Risk Events", len(high_risk)],
            ["High Temperature Events", len(high_temp)],
            ["Valve Status", "Closed" if valve_closed else "Open"],
            ["Reason", reason]
        ]

        table = Table(report_data)
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)

        st.download_button(
            label="Download PDF Report",
            data=buffer,
            file_name="Gas_Monitoring_Report.pdf",
            mime="application/pdf"
        )

    # ----------------------------
    # SMART CHAT WITH SUGGESTIONS
    # ----------------------------
    st.subheader("Smart Safety Assistant")

    example_questions = [
        "Is the system safe?",
        "Why is the valve closed?",
        "Show high risk events",
        "What is average gas?",
        "Temperature issues?",
        "Is vibration causing leak?",
        "Give executive summary"
    ]

    selected_question = st.selectbox("Select a suggested question", example_questions)

    user_input = st.text_input("Or type your own question")

    if user_input:
        q = user_input.lower()
    else:
        q = selected_question.lower()

    if q:

        if "safe" in q:
            st.success("System is safe." if not leak_detected else "System is NOT safe.")
        elif "valve" in q:
            st.info(reason)
        elif "high risk" in q:
            st.info(f"{len(high_risk)} high gas events detected.")
        elif "average gas" in q:
            st.info(f"Average gas: {round(avg_gas,2)}")
        elif "temperature" in q:
            st.info(f"Average temperature: {round(avg_temp,2)}")
        elif "vibration" in q:
            st.info("Vibration detected. Gas normal → likely external.")
        elif "summary" in q:
            st.info(f"""
            Executive Summary:
            Gas Avg: {round(avg_gas,2)}
            Max Gas: {max_gas}
            High Risk Events: {len(high_risk)}
            Valve: {"Closed" if valve_closed else "Open"}
            """)
        else:
            st.info("Ask about gas, valve, safety, temperature, vibration or summary.")

else:
    st.info("Upload a CSV file to begin monitoring.")