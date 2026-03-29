import os
import streamlit as st
import shutil
from fpdf import FPDF
from EnergyReport.src_energy import read_energy
import PyPDF2
import tempfile
import re

# Function to process and convert SIM files to PDF
def main(deg_0, deg_90, file_180, file_270, proposed_file):
    try:
        docx_file = read_energy.extractReport(deg_0, deg_90, file_180, file_270, proposed_file)
        st.download_button(
            label="⬇️ Download Report",
            data=docx_file,
            file_name="Energy_Analysis_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except FileNotFoundError:
        st.error(f"Folder path {deg_0, deg_90, file_180, file_270, proposed_file} not found.")