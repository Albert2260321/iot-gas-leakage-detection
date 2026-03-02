import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.graph_objects as go

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

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
    # HEATMAP (SAFE VERSION)
    # ----------------------------
    st.subheader("Gas Risk Heatmap")
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=[df["Gas Readings"].values],
        colorscale="Reds"
    ))
    fig_heatmap.update_layout(height=200)
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
    # CSV DOWNLOAD
    # ----------------------------
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="Download Sensor CSV Report",
        data=buffer,
        file_name="sensor_report.csv",
        mime="text/csv"
    )

    # ----------------------------
    # PROFESSIONAL PDF REPORT
    # ----------------------------
    def generate_pdf():
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Smart Gas Leakage Detection System Report", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Executive Summary", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        summary_text = f"""
        This report provides an operational analysis of the IoT-based Gas Leakage Detection 
        and Prevention System. The system monitors gas concentration, temperature, and vibration 
        to determine environmental safety.

        Current Risk Score: {risk_score}/100  
        Severity Level: {severity_label}  
        Valve Status: {"Closed" if risk_score >= 60 else "Open"}
        """
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("Sensor Metrics Summary", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        table_data = [
            ["Metric", "Value"],
            ["Average Gas Level", round(avg_gas,2)],
            ["Maximum Gas Level", max_gas],
            ["Average Temperature", round(avg_temp,2)],
            ["Average Vibration", round(avg_vib,2)],
            ["High Gas Events", len(high_risk)],
            ["High Temperature Events", len(high_temp)],
            ["Vibration Events", len(vibration_detected)],
        ]

        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN',(1,1),(-1,-1),'CENTER')
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("System Logic & Interpretation", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        theory_text = """
        The system evaluates safety using threshold-based monitoring and weighted risk scoring.
        Gas readings are categorized into risk levels. Temperature is evaluated alongside gas
        to detect combustion risk scenarios. Vibration analysis differentiates mechanical
        disturbance from genuine leak conditions.

        The consolidated risk score enables automated safety valve control and
        preventive action when required.
        """

        elements.append(Paragraph(theory_text, styles["Normal"]))
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer

    pdf_data = generate_pdf()

    st.download_button(
        label="Download Professional PDF Report",
        data=pdf_data,
        file_name="Gas_Leakage_System_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("Upload a CSV file to begin monitoring.")