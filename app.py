
import streamlit as st
import pandas as pd

# --- AUTHENTICATION SECTION ---
allowed_emails = st.secrets["auth"]["allowed_emails"]
if "user_authenticated" not in st.session_state:
    user_email = st.text_input("Enter your email to access the dashboard")
    if st.button("Login"):
        if user_email.strip().lower() in allowed_emails:
            st.session_state.user_authenticated = True
            st.success("Login successful!")
        else:
            st.error("Access denied. Please use an authorized email.")
    st.stop()

st.set_page_config(layout="wide")
st.title("🚔 Police Department Staff Dashboard")

# Load data
station_df = pd.read_csv("station_data.csv")
employee_df = pd.read_csv("employee_data.csv")

# Sidebar Filters
st.sidebar.header("🔍 Search Options")
pc_number = st.sidebar.text_input("Search by PC Number")
station_filter = st.sidebar.selectbox("Filter by Station", options=["All"] + sorted(station_df["Station"].unique().tolist()))
circle_filter = st.sidebar.selectbox("Filter by Circle", options=["All"] + sorted(station_df["Circle"].unique().tolist()))
subdivision_filter = st.sidebar.selectbox("Filter by Sub-Division", options=["All"] + sorted(station_df["Sub-Division"].unique().tolist()))

# Filter Data
filtered_employees = employee_df.copy()
if pc_number:
    filtered_employees = filtered_employees[filtered_employees["PC Number"].str.contains(pc_number.upper(), na=False)]
if station_filter != "All":
    filtered_employees = filtered_employees[filtered_employees["Station"] == station_filter]

# Export Option
st.download_button(
    label="📥 Download Filtered Employee Data as CSV",
    data=filtered_employees.to_csv(index=False).encode("utf-8"),
    file_name="filtered_employee_data.csv",
    mime="text/csv"
)

# Show Employee Table
st.subheader("📋 Employee Records")
st.dataframe(filtered_employees, use_container_width=True)

# Station Summary
st.subheader("📊 Station Quota Summary")
filtered_stations = station_df.copy()
if station_filter != "All":
    filtered_stations = filtered_stations[filtered_stations["Station"] == station_filter]
elif circle_filter != "All":
    filtered_stations = filtered_stations[filtered_stations["Circle"] == circle_filter]
elif subdivision_filter != "All":
    filtered_stations = filtered_stations[filtered_stations["Sub-Division"] == subdivision_filter]
st.dataframe(filtered_stations, use_container_width=True)

# Aggregated View
st.subheader("📍 Sub-Division Aggregated View")
if st.checkbox("Show Aggregated Data by Sub-Division"):
    agg_df = station_df.groupby("Sub-Division")[["Sanctioned Quota", "Actual Strength", "Vacancies"]].sum().reset_index()
    st.dataframe(agg_df, use_container_width=True)

# Add / Edit Employee Entry
st.subheader("➕ Add / Edit Employee")
with st.form("add_employee"):
    pc = st.text_input("PC Number")
    name = st.text_input("Name")
    station = st.selectbox("Station", options=sorted(station_df["Station"].unique()))
    date = st.text_input("Date (DD.MM.YY)")
    attachment = st.text_input("Attachment")
    submitted = st.form_submit_button("Add / Update Employee")
    if submitted:
        new_row = pd.DataFrame([[pc, name, station, date, attachment]],
                               columns=["PC Number", "Name", "Station", "Date", "Attachments"])
        employee_df = employee_df[employee_df["PC Number"] != pc]
        employee_df = pd.concat([employee_df, new_row], ignore_index=True)
        employee_df.to_csv("employee_data.csv", index=False)
        st.success(f"Employee '{pc}' added/updated successfully!")

# Functional Wings Placeholder
st.subheader("🦾 Functional Wings (Coming Soon)")
st.info("This section will support tracking of functional wing quotas and staffing. Please upload your functional data to extend.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit")
