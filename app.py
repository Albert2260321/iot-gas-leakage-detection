import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.set_page_config(page_title="Smart Gas Leakage Monitoring System", layout="wide")

st.title("Smart Gas Leakage Detection & Prevention System")
st.markdown("### IoT-Based Real-Time Industrial Safety Monitoring")

st.divider()

uploaded_file = st.file_uploader("Upload Gas Sensor CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    st.subheader("Sensor Data Overview")
    st.dataframe(df, use_container_width=True)

    # ---- Metrics ----
    st.divider()
    st.subheader("System Metrics")

    total_records = len(df)
    avg_gas = df["Gas Readings"].mean()
    max_gas = df["Gas Readings"].max()
    avg_temp = df["Temperature"].mean()
    avg_vibration = df["Vibration"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", total_records)
    col2.metric("Avg Gas Level", round(avg_gas, 2))
    col3.metric("Avg Temperature", round(avg_temp, 2))
    col4.metric("Avg Vibration", round(avg_vibration, 2))

    # ---- Risk Classification ----
    st.divider()
    st.subheader("Leakage Risk Assessment")

    THRESHOLD_LOW = 250
    THRESHOLD_HIGH = 400

    def classify_risk(value):
        if value > THRESHOLD_HIGH:
            return "HIGH"
        elif value > THRESHOLD_LOW:
            return "MEDIUM"
        else:
            return "LOW"

    df["Risk Level"] = df["Gas Readings"].apply(classify_risk)

    high_risk_count = len(df[df["Risk Level"] == "HIGH"])

    if high_risk_count > 0:
        st.error(f"{high_risk_count} High-Risk Gas Events Detected")
        shutoff_status = "ACTIVATED"
    else:
        st.success("System Operating Normally")
        shutoff_status = "STANDBY"

    st.write(f"**Safety Valve Status:** {shutoff_status}")

    # ---- Charts ----
    st.divider()
    st.subheader("Sensor Trends")

    st.line_chart(df["Gas Readings"])
    st.line_chart(df["Temperature"])
    st.line_chart(df["Vibration"])

    # ---- Professional Summary ----
    st.divider()
    st.subheader("Operational Summary")

    summary_text = f"""
    The system analyzed {total_records} sensor records.
    Maximum gas concentration recorded was {round(max_gas,2)} units.
    Current valve status: {shutoff_status}.
    Continuous monitoring ensures proactive industrial safety.
    """

    st.info(summary_text)

    # ---- PDF Download ----
    st.divider()
    st.subheader("Download Incident Report")

    if st.button("Generate Incident Report PDF"):
        file_path = "Incident_Report.pdf"
        doc = SimpleDocTemplate(file_path)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Smart Gas Leakage Detection System - Incident Report", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(f"Generated On: {datetime.now()}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(summary_text, styles["Normal"]))

        doc.build(elements)

        with open(file_path, "rb") as f:
            st.download_button(
                label="Download Report",
                data=f,
                file_name="Smart_Gas_Leakage_Report.pdf",
                mime="application/pdf"
            )

else:
    st.info("Upload a CSV file to start monitoring.")