import os
import pandas as pd
import streamlit as st
import tempfile
from zipfile import ZipFile
from INP_Parser.src_inp import hvac_system

def get_report_and_save(report_function, inp_path, file_suffix):
    try:
        report = report_function(inp_path)
        # Get the parent directory of the INP file
        parent_directory = os.path.dirname(inp_path)
        file_name = os.path.splitext(os.path.basename(inp_path))[0]
        file_path = os.path.join(parent_directory, f'{file_name}_{file_suffix}.csv')
        if os.path.isfile(file_path):
            os.remove(file_path)
        report.to_csv(file_path, index=False)
        return file_path
    except Exception as e:
        st.error(f"Error generating {file_suffix} report: {e}")
        return None

def main(uploaded_file):
    if uploaded_file is not None:
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                inp_path = os.path.join(temp_dir, uploaded_file.name)
                
                # Write the uploaded file to the temporary directory
                with open(inp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Generate reports
                sys_report_path = get_report_and_save(hvac_system.get_HVAC_System_report, inp_path, 'Sys_INP')
                zone_report_path = get_report_and_save(hvac_system.get_HVAC_Zone_report, inp_path, 'Zone_INP')
                
                if sys_report_path and zone_report_path:
                    st.success("INP Parsed Successfully!!")
                    
                    # Create a zip file containing both reports
                    zip_file_path = os.path.join(temp_dir, f"{os.path.splitext(uploaded_file.name)[0]}_reports.zip")
                    with ZipFile(zip_file_path, 'w') as zipf:
                        zipf.write(sys_report_path, os.path.basename(sys_report_path))
                        zipf.write(zone_report_path, os.path.basename(zone_report_path))
                    
                    # Provide a download link for the zip file
                    with open(zip_file_path, 'rb') as f:
                        st.download_button(
                            label="Download Reports",
                            data=f,
                            file_name=os.path.basename(zip_file_path),
                            mime='application/zip'
                        )

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    uploaded_file = st.file_uploader("Upload your INP file", type=["inp"])
    main(uploaded_file)
