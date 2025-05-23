import os
import streamlit as st
import tempfile
from zipfile import ZipFile
from SIM_Parser.src_sim import lv_b, ls_c, lv_d, pv_a, sv_a, beps, bepu, lvd_summary, sva_zone, ps_e, ps_f

def get_report_and_save(report_function, sim_path, file_suffix):
    try:
        report = report_function(sim_path)
        file_name = os.path.splitext(os.path.basename(sim_path))[0]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            report.to_csv(temp_file.name, index=False)
            temp_file_path = temp_file.name
        st.success(f"{file_suffix} Report Generated!")
        return temp_file_path
    except Exception as e:
        st.success(f" {file_suffix} does not exist!")
        return None

def main(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        sim_path = temp_file_path
        sim_file_name = os.path.splitext(uploaded_file.name)[0]

        download_files = []

        report_functions = [
            (ls_c.get_LSC_report, 'LSC.csv', 'lsc'),
            (lv_d.get_LVD_report, 'LVD.csv', 'lvd'),
            (lvd_summary.get_LVD_Summary_report, 'LVD_Summary.csv', 'lvd_Summary'),
            (pv_a.get_PVA_report, 'PVA.csv', 'pva'),
            (sv_a.get_SVA_report, 'SVA.csv', 'sva'),
            (sva_zone.get_SVA_Zone_report, 'SVA_Zone.csv', 'sva_Zone'),
            (beps.get_BEPS_report, 'BEPS.csv', 'beps'),
            (bepu.get_BEPU_report, 'BEPU.csv', 'bepu'),
            (lv_b.get_LVB_report, 'LVB.csv', 'lvb'),
            (ps_e.get_PSE_report, 'PSE.csv', 'pse'),
            (ps_f.get_PSF_report, 'PSF.csv', 'psf')
        ]

        for report_function, file_name, suffix in report_functions:
            file_path = get_report_and_save(report_function, sim_path, suffix)
            if file_path:
                download_files.append((file_name, file_path))

        if download_files:
            st.success("SIM Parsed Successfully!!")

            # Create a zip file containing all generated reports
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
                zip_folder_name = f"{sim_file_name}_SIM_reports"
                with ZipFile(temp_zip.name, 'w') as zipf:
                    for file_name, file_path in download_files:
                        zipf.write(file_path, file_name)

                # Provide download link for the zip file
                with open(temp_zip.name, 'rb') as f:
                    st.download_button(
                        label="Download All Reports",
                        data=f,
                        file_name=f"{zip_folder_name}.zip",
                        mime='application/zip'
                    )
        else:
            st.error("No reports were generated. Please check the SIM file and try again.")
    else:
        st.error("Please upload a SIM file.")

if __name__ == "__main__":
    uploaded_file = st.file_uploader("Upload your SIM file", type=["sim"])
    main(uploaded_file)
