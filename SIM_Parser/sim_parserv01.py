import os
import streamlit as st
import tempfile
from zipfile import ZipFile
import re
from SIM_Parser.src_sim import lv_b, ls_c, lv_d, pv_a, sv_a, beps, bepu, lvd_summary, sva_zone, ps_e, ps_f, ls_b, lv_h

def get_report_and_save(report_function, sim_path, file_suffix, title_container, status_container):
    import streamlit as st
    import os, tempfile

    # session key (safe per container)
    key = f"status_messages_{id(status_container)}"
    # init state
    if key not in st.session_state:
        st.session_state[key] = []
    try:
        report = report_function(sim_path)
        file_name = os.path.splitext(os.path.basename(sim_path))[0]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            report.to_csv(temp_file.name, index=False)
            temp_file_path = temp_file.name
        # add success badge
        st.session_state[key].append(f"<span style='color:green; font-weight:600; font-size:13px; margin-right:14px;'>✅ {file_suffix}</span>")
    except Exception:
        # add error badge
        st.session_state[key].append(f"<span style='color:red; font-weight:600; font-size:13px; margin-right:14px;'>❌ {file_suffix}</span>")
        temp_file_path = None
    # -------- UI Render --------
    title_container.markdown("<b style='color:black; font-weight:600; font-size:1200;'>SIM Reports:</b>",unsafe_allow_html=True)

    status_container.markdown(
        f"<div style='white-space:nowrap; overflow-x:auto; padding-top:4px;'>"
        f"{''.join(st.session_state[key])}</div>",
        unsafe_allow_html=True
    )

    return temp_file_path

def main(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        sim_path = temp_file_path
        sim_file_name = os.path.splitext(uploaded_file.name)[0]

        download_files = []

        report_functions = [
            (ls_c.get_LSC_report, 'LSC.csv', 'LS-C'),
            (ls_c.get_LSC_losses_report, 'LSC_LOSS.csv', 'LS-C LOSS'),
            (lv_d.get_LVD_report, 'LVD.csv', 'LV-D'),
            (lvd_summary.get_LVD_Summary_report, 'LVD_Summary.csv', 'LV-D Summary'),
            (pv_a.get_PVA_report, 'PVA.csv', 'PV-A'),
            (sv_a.get_SVA_report, 'SVA.csv', 'SV-A'),
            (sva_zone.get_SVA_Zone_report, 'SVA_Zone.csv', 'SV-A Zone'),
            (beps.get_BEPS_report, 'BEPS.csv', 'BEPS'),
            (bepu.get_BEPU_report, 'BEPU.csv', 'BEPU'),
            (lv_b.get_LVB_report, 'LVB.csv', 'LV-B'),
            (ps_e.get_PSE_report, 'PSE.csv', 'PS-E'),
            (ps_f.get_PSF_report, 'PSF.csv', 'PS-F'),
            (ls_b.get_LSB_report, 'LSB.csv', 'LS-B'),
            (lv_h.get_LVH_report, 'LVH.csv', 'LV-H')
        ]
        title_ui  = st.empty()
        status_ui = st.empty()
        for report_function, file_name, suffix in report_functions:
            file_path = get_report_and_save(report_function, sim_path, suffix, title_ui, status_ui)
            if file_path:
                download_files.append((file_name, file_path))

        if download_files:
            st.markdown(f"<br><span style='color:green;'></span>", unsafe_allow_html=True)

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
