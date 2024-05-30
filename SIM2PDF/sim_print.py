import os
import streamlit as st
import shutil
from fpdf import FPDF
from SIM2PDF.src_pdf import readSim
import PyPDF2

def main(input_sim_files, reports):
    if os.path.isdir(input_sim_files):
        st.success(input_sim_files)
        readSim.extractReport(input_sim_files, reports)
        st.success("PDFs Generated Successfully!")
    else:
        st.error("Invalid directory path.")
