import os
import streamlit as st
import shutil
from fpdf import FPDF
from SIM2PDF.src_pdf import readSim
import PyPDF2

def main(input_sim_files, reports):
        if os.path.isdir(input_sim_files):
            readSim.extractReport(input_sim_files, reports)
            st.success("PDFs Generated Successfully!")
        else:
            st.error("Invalid directory path.")

# import os
# import shutil
# from fpdf import FPDF
# from SIM2PDF.src_pdf import readSim
# import PyPDF2

# def main(input_sim_files, reports):
#     try:
#         # Normalize the path
#         normalized_path = os.path.normpath(input_sim_files)
#         print("Normalized directory path:", normalized_path)  # Debugging output

#         # Print the current working directory for additional context
#         print("Current working directory:", os.getcwd())

#         if os.path.exists(normalized_path):
#             print("Directory path exists.")
#             if os.path.isdir(normalized_path):
#                 print("Directory path is valid.")
#                 readSim.extractReport(normalized_path, reports)
#                 print("PDFs Generated Successfully!")
#                 return "PDFs Generated Successfully!"
#             else:
#                 error_message = "Path exists but is not a directory."
#                 print(error_message)
#                 return error_message
#         else:
#             error_message = "Path does not exist."
#             print(error_message)
#             return error_message
#     except Exception as e:
#         error_message = f"Error: {e}"
#         print(error_message)
#         return error_message
