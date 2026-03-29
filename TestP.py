import streamlit as st
import zipfile
import io
import os

st.title("Energy Report Generator")

# ✅ Your fixed template path
TEMPLATE_PATH = r"D:\EDS\S2302_eQuest_Automation\S2302.2 eQuest Utilities\git\MEPC\EnergyReport\Energy_Analysis_Report_Tempelate.docx"

project_name = st.text_input("Project Name")

ORIGINAL_NAME = "MFAR Red Sanders"

if st.button("Generate Report"):

    if not os.path.exists(TEMPLATE_PATH):
        st.error("Template file not found!")
    else:
        with open(TEMPLATE_PATH, "rb") as f:
            input_bytes = f.read()

        zip_in = zipfile.ZipFile(io.BytesIO(input_bytes))

        output_buffer = io.BytesIO()
        zip_out = zipfile.ZipFile(output_buffer, "w")

        for item in zip_in.infolist():
            data = zip_in.read(item.filename)

            if item.filename.endswith(".xml"):
                try:
                    text = data.decode("utf-8")

                    # ✅ Replace only if different
                    if project_name.strip().lower() != ORIGINAL_NAME.lower():
                        text = text.replace("MFAR Red Sanders", project_name)
                        text = text.replace("Bangalore", "")

                    data = text.encode("utf-8")
                except:
                    pass

            zip_out.writestr(item, data)

        zip_out.close()
        output_buffer.seek(0)

        st.success("Report Generated Successfully!")

        st.download_button(
            label="Download Report",
            data=output_buffer,
            file_name="Energy_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )