import streamlit as st
import pandas as pd
import re
from io import BytesIO

def update_inp_file(uploaded_file):
    try:
        raw_text = uploaded_file.read().decode("utf-8")
        text = re.sub(r'\\[a-z]+\d*[\s]?|[\{\}]', '', raw_text)

        # Split the content into blocks per space
        space_entries = re.split(r"\n\s*([A-Z0-9\- &]+.*?)\s*\n1\. General Details:", text)
        results = []

        for i in range(1, len(space_entries), 2):
            space_name = space_entries[i].strip()
            block = space_entries[i + 1]

            # Extract basic fields
            floor_area = re.search(r"Floor Area\s+([\d.]+)", block)
            ceiling_height = re.search(r"Avg\. Ceiling Height\s+([\d.]+)", block)
            occupancy = re.search(r"Occupancy\s+([\d.]+)", block)

            # Extract wattage values from their sections
            overhead = re.search(r"2\.1\. Overhead Lighting:.*?Wattage\s+([\d.]+)", block, re.DOTALL)
            task = re.search(r"2\.2\. Task Lighting:.*?Wattage\s+([\d.]+)", block, re.DOTALL)
            equipment = re.search(r"2\.3\. Electrical Equipment:.*?Wattage\s+([\d.]+)", block, re.DOTALL)

            row = {
                "Space Name": space_name,
                "Floor Area": float(floor_area.group(1)) if floor_area else None,
                "Avg. Ceiling Height": float(ceiling_height.group(1)) if ceiling_height else None,
                "Occupancy": float(occupancy.group(1)) if occupancy else None,
                "Wattage (Overhead Lighting)": float(overhead.group(1)) if overhead else None,
                "Wattage (Task Lighting)": float(task.group(1)) if task else None,
                "Wattage (Electrical Equipment)": float(equipment.group(1)) if equipment else None,
            }

            results.append(row)

        df = pd.DataFrame(results)

        # Write to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Space Summary')
        output.seek(0)
        return output, "space_summary_named_wattage.xlsx"

    except Exception as e:
        st.error(f"An error occurred while processing the INP file: {e}")
        return None, None

def main(uploaded_file):
    # uploaded_file = st.file_uploader("Upload INP file", type=["inp", "txt"])
    if uploaded_file:
        file_content, updated_file_name = update_inp_file(uploaded_file)
        if file_content and updated_file_name:
            st.success("✅ Excel written successfully!")
            st.download_button(
                label="📥 Download Excel File",
                data=file_content,
                file_name=updated_file_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if __name__ == "__main__":
    main(uploaded_file)
