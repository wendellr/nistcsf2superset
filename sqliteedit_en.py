import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Function to connect to the SQLite database
def connect_to_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Function to load data from the table
def load_table_data(conn, table_name):
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql_query(query, conn)

# Function to update fields in the table
def update_record(conn, record_id, status, maturity_level, target_maturity_level, reviewer, justificative, recommendation):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = """
    UPDATE nist_csf2_en
    SET Status = ?, 
        Maturity_Level = ?, 
        Target_Maturity_Level = ?, 
        Reviewer = ?, 
        Justificative = ?, 
        Recommendation = ?, 
        Creation_Date = ?
    WHERE ID = ?;
    """
    conn.execute(query, (status, maturity_level, target_maturity_level, reviewer, justificative, recommendation, current_date, record_id))
    conn.commit()

# Connect to the database
db_path = 'DEMO_NIST_CSF_2_0.db'
conn = connect_to_db(db_path)

# Streamlit configuration
st.title("NIST CSF Table Editor")

# Load table data
data = load_table_data(conn, 'nist_csf2_en')

# Add search filters
st.sidebar.title("Search Filters")

# Filter by Function
function_filter = st.sidebar.text_input("Search by Function")
if function_filter:
    data = data[data['Function'].str.contains(function_filter, case=False, na=False)]

# Filter by Category
category_filter = st.sidebar.text_input("Search by Category")
if category_filter:
    data = data[data['Category'].str.contains(category_filter, case=False, na=False)]

# Filter by Subcategory
subcategory_filter = st.sidebar.text_input("Search by Subcategory")
if subcategory_filter:
    data = data[data['Subcategory'].str.contains(subcategory_filter, case=False, na=False)]

# Display filtered records
st.subheader("Filtered Records")
if data.empty:
    st.write("No records found.")
else:
    st.dataframe(data[['ID', 'Function', 'Category', 'Subcategory', 'Status']])

# Select a record to edit
selected_row = st.selectbox("Select the ID of the record to edit", data['ID'] if not data.empty else [])

if selected_row:
    # Filter data for the selected row
    record = data[data['ID'] == selected_row].iloc[0]
    
    # Fields for editing
    status = st.text_input("Status", value=record['Status'] if record['Status'] else "")
    maturity_level = st.number_input("Maturity Level", value=record['Maturity_Level'] if record['Maturity_Level'] else 0, step=1)
    target_maturity_level = st.number_input("Target Maturity Level", value=record['Target_Maturity_Level'] if record['Target_Maturity_Level'] else 0, step=1)
    reviewer = st.text_input("Reviewer", value=record['Reviewer'] if record['Reviewer'] else "")
    justificative = st.text_area("Justificative", value=record['Justificative'] if record['Justificative'] else "")
    recommendation = st.text_area("Recommendation", value=record['Recommendation'] if record['Recommendation'] else "")
    
    # Button to save changes
    if st.button("Save Changes"):
        update_record(conn, selected_row, status, maturity_level, target_maturity_level, reviewer, justificative, recommendation)
        st.success("Record updated successfully!")
        # Refresh data in the interface
        data = load_table_data(conn, 'nist_csf2_en')
        st.dataframe(data)