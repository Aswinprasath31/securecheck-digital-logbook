import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

# Database connection
def create_connection():
    try:
        connection = pymysql.connect(
            host="localhost",  # ⚠️ Replace with remote host for Streamlit Cloud
            user="root",
            password="Rose143",
            database="securecheck",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Fetch data from database
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()

# Streamlit UI
st.set_page_config(page_title="SecureCheck Police Dashboard", layout="wide")
st.title("🚨 SecureCheck: Police Check Post Digital Ledger")
st.markdown("Real-time monitoring and insights for law enforcement 🚓")

# Load Data
query = "SELECT * FROM police_logs"
data = fetch_data(query)

if data.empty:
    st.warning("⚠️ Using fallback Excel file (no database connection).")
    try:
        data = pd.read_excel("traffic_stops.xlsx")
    except Exception as e:
        st.error(f"No data available: {e}")
        st.stop()

# Show full table
st.header("📋 Police Logs Overview")
st.dataframe(data, use_container_width=True)

# Quick Metrics
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Police Stops", data.shape[0])

with col2:
    if "stop_outcome" in data.columns:
        arrests = data[data["stop_outcome"].str.contains("arrest", case=False, na=False)].shape[0]
        st.metric("Total Arrests", arrests)
    else:
        st.metric("Total Arrests", "N/A")

with col3:
    if "stop_outcome" in data.columns:
        warnings = data[data["stop_outcome"].str.contains("warning", case=False, na=False)].shape[0]
        st.metric("Total Warnings", warnings)
    else:
        st.metric("Total Warnings", "N/A")

with col4:
    if "drugs_related_stop" in data.columns:
        drug_related = data[data["drugs_related_stop"] == 1].shape[0]
        st.metric("Drug Related Stops", drug_related)
    else:
        st.metric("Drug Related Stops", "N/A")

# Charts
st.header("📈 Visual Insights")
tab1, tab2 = st.tabs(["Stops by Violation", "Driver Gender Distribution"])

with tab1:
    if "violation" in data.columns:
        violation_data = data["violation"].value_counts().reset_index()
        violation_data.columns = ["Violation", "Count"]
        fig = px.bar(violation_data, x="Violation", y="Count",
                     title="Stops by Violation Type", color="Violation")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Violation chart.")

with tab2:
    if "driver_gender" in data.columns:
        gender_data = data["driver_gender"].value_counts().reset_index()
        gender_data.columns = ["Gender", "Count"]
        fig = px.pie(gender_data, names="Gender", values="Count",
                     title="Driver Gender Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Driver Gender chart.")
