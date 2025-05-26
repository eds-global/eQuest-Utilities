import os
import streamlit as st
import shutil
from fpdf import FPDF
from SIM2PDF.src_pdf import readSim
import PyPDF2
import tempfile

# Function to process and convert SIM files to PDF
def main(reports, input_sim_files):
    try:
        readSim.extractReport(input_sim_files, reports)
    except FileNotFoundError:
        st.error(f"Folder path {input_sim_files} not found.")