import streamlit as st
from generate_plot import generate_plot  # This imports the function from generate_plot.py

st.set_page_config(page_title="Battery V3 Viewer", layout="wide")
st.title("Battery Data Visualizer (V3)")

uploaded_files = st.file_uploader("Upload an Excel file", accept_multiple_files=True)

if uploaded_files:
    uploaded_file = uploaded_files[0]  # only take first file for now
    file_name = uploaded_file.name
    if not (file_name.endswith(".xls") or file_name.endswith(".xlsx")):
        st.error("❌ Please upload a file with .xls or .xlsx extension.")
    else:
        try:
            fig = generate_plot(
                uploaded_file,
                custom_label="Uploaded Battery",
                x_column='Test_Time(s)',
                left_y_columns=['Current(A)'],
                right_y_columns=['Voltage(V)'],
                color_pair=('blue', 'red'),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating plot: {e}")
