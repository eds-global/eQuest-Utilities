import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
import re

# Function to extract room data from a single block of text
def extract_room_data(text):
    room_data = {}

    # Room Name (more general: line ending with ROOM or starting with L- / number)
    room_match = re.search(r"^(.*?)(?:\s*ROOM|$)", text.strip(), re.MULTILINE)
    room_data['Room Name'] = room_match.group(1).strip() if room_match else ""

    # Floor Area
    floor_match = re.search(r"Floor Area\s*([\d\.]+)\s*m²", text)
    room_data['Floor Area (m²)'] = float(floor_match.group(1)) if floor_match else 0.0

    # Ceiling Height
    ceiling_match = re.search(r"Avg\. Ceiling Height\s*([\d\.]+)\s*m", text)
    room_data['Ceiling Height (m)'] = float(ceiling_match.group(1)) if ceiling_match else 0.0

    # Building Weight
    weight_match = re.search(r"Building Weight\s*([\d\.]+)\s*kg/m²", text)
    room_data['Building Weight (kg/m²)'] = float(weight_match.group(1)) if weight_match else 0.0

    # OA Requirements
    oa1_match = re.search(r"OA Requirement 1\s*([\d\.]+)\s*L/s/person", text)
    room_data['OA Req. 1 (L/s/person)'] = float(oa1_match.group(1)) if oa1_match else 0.0

    oa2_match = re.search(r"OA Requirement 2\s*([\d\.]+)\s*L/\(s·m²\)", text)
    room_data['OA Req. 2 (L/s·m²)'] = float(oa2_match.group(1)) if oa2_match else 0.0

    # Occupancy (fixed regex)
    occ_match = re.search(r'Occupancy[:\s]*([\d\.,]+)', text, re.IGNORECASE)
    room_data['Occupancy'] = float(occ_match.group(1).replace(',', '')) if occ_match else 0.0

    # Sensible & Latent
    sens_match = re.search(r"Sensible\s*([\d\.]+)\s*W/person", text)
    room_data['Sensible (W/person)'] = float(sens_match.group(1)) if sens_match else 0.0

    latent_match = re.search(r"Latent\s*([\d\.]+)\s*W/person", text)
    room_data['Latent (W/person)'] = float(latent_match.group(1)) if latent_match else 0.0

    # Lighting
    light_match = re.search(r"Overhead Lighting:\s*.*?Wattage\s*([\d\.]+)\s*W/m²", text, re.DOTALL)
    room_data['Lighting'] = float(light_match.group(1)) if light_match else 0.0
    room_data['Light-Unit'] = "W/m²" if light_match else ""

    # Task Lighting
    task_match = re.search(r"Task Lighting:\s*.*?Wattage\s*([\d\.]+)\s*W/m²", text, re.DOTALL)
    room_data['Task Lighting'] = float(task_match.group(1)) if task_match else 0.0
    room_data['Task-Light-Unit'] = "W/m²" if task_match else ""

    # Electrical Equipment
    equip_match = re.search(r"Electrical Equipment:\s*Wattage\s*([\d\.]+)\s*Watts", text, re.DOTALL)
    room_data['Electrical Equip.'] = float(equip_match.group(1)) if equip_match else 0.0
    room_data['Electrical-Equip-Unit'] = "Watts" if equip_match else ""

    return room_data


# Streamlit app
st.title("PDF Room Data Extractor (Pages 161–296)")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = ""
    # Extract text from pages 161 to 296 (0-based indexing)
    for page_num in range(160, 296):
        if page_num < len(reader.pages):
            full_text += reader.pages[page_num].extract_text() + "\n"

    # Split into room blocks (each block starts with "L-" or "Room")
    blocks = re.split(r'\n(?=L-\d+)', full_text)
    room_list = []
    for block in blocks:
        if "Floor Area" in block:  # filter only valid room sections
            room_list.append(extract_room_data(block))

    df = pd.DataFrame(room_list)

    st.subheader(f"Extracted Room Data — {len(df)} rooms found")
    st.dataframe(df, use_container_width=True)

    # Optional: allow download as Excel
    excel_file = "room_data.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file, "rb") as f:
        st.download_button("Download as Excel", f, file_name=excel_file)
