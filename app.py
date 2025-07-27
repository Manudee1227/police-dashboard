
import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.set_page_config(layout="wide", page_title="Minimal Police Dashboard")

# Load data
station_df = pd.read_csv("station_data.csv")
employee_df = pd.read_csv("employee_data.csv")

# Sidebar: Filters and Search
st.sidebar.header("Filter Options")
pc_search = st.sidebar.text_input("Search by PC Number")
subdivision = st.sidebar.selectbox("Sub-Division", ["All"] + sorted(station_df["Sub-Division"].unique()))
circle = st.sidebar.selectbox("Circle", ["All"] + sorted(station_df["Circle"].unique()))
station = st.sidebar.selectbox("Station", ["All"] + sorted(station_df["Station"].unique()))

# Apply filters
filtered_emp = employee_df.copy()
filtered_stats = station_df.copy()

if pc_search:
    filtered_emp = filtered_emp[filtered_emp["PC Number"].str.contains(pc_search.strip(), case=False)]
else:
    if subdivision != "All":
        filtered_emp = filtered_emp[filtered_emp["Station"].isin(
            station_df[station_df["Sub-Division"] == subdivision]["Station"])]
        filtered_stats = filtered_stats[filtered_stats["Sub-Division"] == subdivision]
    if circle != "All":
        filtered_emp = filtered_emp[filtered_emp["Station"].isin(
            station_df[station_df["Circle"] == circle]["Station"])]
        filtered_stats = filtered_stats[filtered_stats["Circle"] == circle]
    if station != "All":
        filtered_emp = filtered_emp[filtered_emp["Station"] == station]
        filtered_stats = filtered_stats[filtered_stats["Station"] == station]

# Display employee data
st.title("Police Staff Directory")
st.dataframe(filtered_emp, use_container_width=True)

# Display quota summary
st.subheader("Quota Summary")
st.dataframe(filtered_stats[["Station", "Sanctioned Quota", "Actual Strength", "Vacancies"]], use_container_width=True)

# Add/Edit/Delete form
st.subheader("Modify Employee Data")
with st.form("edit_form"):
    pc = st.text_input("PC Number")
    name = st.text_input("Name")
    post_station = st.selectbox("Post Station", sorted(station_df["Station"].unique()))
    date = st.text_input("Date (DD.MM.YY)")
    attachment = st.text_input("Attachment")
    action = st.radio("Action", ["Add/Update", "Delete"])
    go = st.form_submit_button("Apply")
    if go:
        if action == "Add/Update":
            employee_df = employee_df[employee_df["PC Number"] != pc]
            new_row = pd.DataFrame([[pc, name, post_station, date, attachment]], columns=employee_df.columns)
            employee_df = pd.concat([employee_df, new_row], ignore_index=True)
            employee_df.to_csv("employee_data.csv", index=False)
            st.success("Employee record saved.")
        elif action == "Delete":
            employee_df = employee_df[employee_df["PC Number"] != pc]
            employee_df.to_csv("employee_data.csv", index=False)
            st.warning("Employee record deleted.")

# PDF Export
def generate_pdf(data, stats, title="Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"{title}", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)

    for idx, row in stats.iterrows():
        for col in ["Station", "Sanctioned Quota", "Actual Strength", "Vacancies"]:
            pdf.cell(0, 8, f"{col}: {row[col]}", ln=True)
        pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    for col in data.columns:
        pdf.cell(38, 8, col, border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 11)
    for _, row in data.iterrows():
        for item in row:
            pdf.cell(38, 8, str(item), border=1)
        pdf.ln()

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

if not filtered_emp.empty and st.button("📄 Download PDF Report"):
    pdf_bytes = generate_pdf(filtered_emp, filtered_stats, title="Filtered Report")
    st.download_button("Download PDF", data=pdf_bytes, file_name="filtered_report.pdf", mime="application/pdf")

st.caption("Minimal Dashboard • Streamlit & Python")
