import os
import streamlit as st
import tempfile
from zipfile import ZipFile
from SIM_Parser.src_sim import lv_b, ls_c, lv_d, pv_a, sv_a, beps, bepu, lvd_summary, sva_zone, ps_e, ps_f

def get_report_and_save(report_function, name1, sim_path, file_suffix):
    report = report_function(sim_path)
    file_name = os.path.splitext(os.path.basename(sim_path))[0]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        report.to_csv(temp_file.name, index=False)
        temp_file_path = temp_file.name
    st.success(f"{file_suffix} Report Generated!")
    return temp_file_path

def main(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        sim_path = temp_file_path
        sim_file_name = os.path.splitext(uploaded_file.name)[0]

        download_files = []

        download_files.append(("LSC.csv", get_report_and_save(ls_c.get_LSC_report, None, sim_path, 'lsc')))
        download_files.append(("LVD.csv", get_report_and_save(lv_d.get_LVD_report, None, sim_path, 'lvd')))
        download_files.append(("LVD_Summary.csv", get_report_and_save(lvd_summary.get_LVD_Summary_report, None, sim_path, 'lvd_Summary')))
        download_files.append(("PVA.csv", get_report_and_save(pv_a.get_PVA_report, None, sim_path, 'pva')))
        download_files.append(("SVA.csv", get_report_and_save(sv_a.get_SVA_report, None, sim_path, 'sva')))
        download_files.append(("SVA_Zone.csv", get_report_and_save(sva_zone.get_SVA_Zone_report, None, sim_path, 'sva_Zone')))
        download_files.append(("BEPS.csv", get_report_and_save(beps.get_BEPS_report, None, sim_path, 'beps')))
        download_files.append(("BEPU.csv", get_report_and_save(bepu.get_BEPU_report, None, sim_path, 'bepu')))
        download_files.append(("LVB.csv", get_report_and_save(lv_b.get_LVB_report, None, sim_path, 'lvb')))
        download_files.append(("PSE.csv", get_report_and_save(ps_e.get_PSE_report, None, sim_path, 'pse')))
        download_files.append(("PSF.csv", get_report_and_save(ps_f.get_PSF_report, None, sim_path, 'psf')))

        st.success("SIM Parsed Successfully!!")

        # Create a zip file containing all generated reports
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            zip_folder_name = f"{sim_file_name}_SIM_reports"
            with ZipFile(temp_zip, 'w') as zipf:
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
        st.error("Please upload a SIM file.")

if __name__ == "__main__":
    uploaded_file = st.file_uploader("Upload your SIM file", type=["sim"])
    main(uploaded_file)
