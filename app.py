
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(layout="wide", page_title="Futuristic Police Dashboard")

# Basic access control
allowed_emails = ["manoj.spoffice.kri@gmail.com"]
if "user_authenticated" not in st.session_state:
    user_email = st.text_input("Enter your email to access the dashboard")
    if st.button("Login"):
        if user_email.strip().lower() in allowed_emails:
            st.session_state.user_authenticated = True
            st.success("Login successful!")
        else:
            st.error("Access denied.")
    st.stop()

st.markdown("<h1 style='color:#FF00FF;'>🚨 Police Dashboard</h1>", unsafe_allow_html=True)

station_df = pd.read_csv("station_data.csv")
employee_df = pd.read_csv("employee_data.csv")

# Sidebar filters
st.sidebar.header("🔍 Search Filters")
pc_input = st.sidebar.text_input("Search by PC Number")
station_filter = st.sidebar.selectbox("Station", ["All"] + sorted(station_df["Station"].unique()))

# Filter data
filtered_emp = employee_df.copy()
if pc_input:
    filtered_emp = filtered_emp[filtered_emp["PC Number"].str.contains(pc_input.strip(), case=False)]
if station_filter != "All":
    filtered_emp = filtered_emp[filtered_emp["Station"] == station_filter]

# Metrics view
st.subheader("📊 Key Metrics")
if station_filter != "All":
    stats = station_df[station_df["Station"] == station_filter]
else:
    stats = station_df[["Sanctioned Quota", "Actual Strength", "Vacancies"]].sum().to_frame().T

col1, col2, col3 = st.columns(3)
col1.metric("Sanctioned", int(stats["Sanctioned Quota"].values[0]))
col2.metric("Actual", int(stats["Actual Strength"].values[0]))
col3.metric("Vacancies", int(stats["Vacancies"].values[0]))

# Data display
st.subheader("👮 Filtered Employee Records")
st.dataframe(filtered_emp, use_container_width=True)

# PDF Generation
def generate_pdf(df, summary, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"{title} Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    for col in summary.columns:
        pdf.cell(60, 10, f"{col}: {summary[col].values[0]}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    for col in df.columns:
        pdf.cell(38, 10, col, border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 11)
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(38, 10, str(item), border=1)
        pdf.ln()
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

if not filtered_emp.empty and station_filter != "All":
    if st.button("📄 Download Station PDF Report"):
        summary_row = stats if isinstance(stats, pd.DataFrame) else pd.DataFrame(stats)
        pdf_data = generate_pdf(filtered_emp, summary_row, station_filter)
        st.download_button("📥 Download Report", data=pdf_data, file_name=f"{station_filter}_Report.pdf", mime="application/pdf")

# Add/Edit employee form
st.subheader("➕ Manage Employee")
with st.form("emp_form"):
    pc = st.text_input("PC Number")
    name = st.text_input("Name")
    station = st.selectbox("Assign Station", sorted(station_df["Station"].unique()))
    date = st.text_input("Joining Date")
    attachment = st.text_input("Attachment")
    submitted = st.form_submit_button("Save Record")
    if submitted:
        employee_df = employee_df[employee_df["PC Number"] != pc]
        new_row = pd.DataFrame([[pc, name, station, date, attachment]], columns=employee_df.columns)
        employee_df = pd.concat([employee_df, new_row], ignore_index=True)
        employee_df.to_csv("employee_data.csv", index=False)
        st.success("Record saved!")

st.markdown("---")
st.caption("Futuristic dashboard powered by Streamlit ✨")
