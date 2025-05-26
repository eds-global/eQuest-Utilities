import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw 
import re
import streamlit as st
import tempfile
from src import ps_e, bepu

warnings.filterwarnings("ignore")

def powerLighting(lvb_df):
    light = lvb_df['LIGHTS'].to_list()
    total_power = 0
    for i in range(0, len(light)):
        total_power = total_power + light[i]
    return total_power

# function to Calculate the total equipment consumption
def equipment(lvb_df):
    equip = lvb_df['EQUIP(WATT / SOFT)'].to_list()
    total_equip = 0
    for i in range(0, len(equip)):
        total_equip = total_equip + equip[i]
    return total_equip

# function to Calculate the total people
def people(lvb_df):
    peop = lvb_df['PEOPLE'].to_list()
    total_people = 0
    for i in range(0, len(peop)):
        total_people = total_people + peop[i]
    return total_people

# function to Calculate the total above_area 
def _total_above_area_Info(lvb_df):
    lvb_df['HEIGHT'] = pd.to_numeric(lvb_df['HEIGHT'])
    height = lvb_df['HEIGHT'].to_list()
    SA = []
    total_above_area = 0
    for i in range(0, len(height)):
        if height[i] > 6:
            SA.append(1)
            total_above_area = total_above_area + lvb_df['AREA'][i]
        else:
            SA.append(0)
    return total_above_area

import re

def get_Activity_Desc(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    start_marker = "Floors / Spaces / Walls / Windows / Doors"
    end_marker = "Electric & Fuel Meters"

    # Extract only the relevant portion
    try:
        start_idx = next(i for i, line in enumerate(lines) if start_marker in line)
        end_idx = next(i for i, line in enumerate(lines) if end_marker in line)
    except StopIteration:
        print("Markers not found.")
        return []

    section_lines = lines[start_idx:end_idx]

    activity_descs = []
    inside_space = False

    for line in section_lines:
        stripped = line.strip()

        # Detect start of a SPACE block
        if re.match(r'^".*"\s*=\s*SPACE', stripped):
            inside_space = True
        elif re.match(r'^".*"\s*=', stripped):  # Start of another block
            inside_space = False

        if inside_space and 'C-ACTIVITY-DESC' in stripped:
            # Extract text after '='
            match = re.search(r'C-ACTIVITY-DESC\s*=\s*\*?(.*?)\*?\s*$', stripped)
            if match:
                activity_descs.append(match.group(1).strip())

    return activity_descs

def get_LVB_Report(name):
    try:
        with open(name) as f:
            flist = f.readlines()

            lvb_count = [] 
            for num, line in enumerate(flist, 0):
                if 'LV-B' in line:
                    lvb_count.append(num)
                if 'LV-C' in line:
                    numend = num
            numstart = lvb_count[0] 
            lvb_rpt = flist[numstart:numend]
            
            lvb_str = []
            for line in lvb_rpt:
                line = re.sub(r'(\d)\.(\d+)\.', r'\1. \2.', line)
                # Check conditions and append lines containing relevant data to lvb_str list
                if (('NO-INFILT.' in line and 'INT' in line) or ('NO-INFILT.' in line and 'EXT' in line) or
                    ('AIR-CHANGE' in line and 'INT' in line) or ('AIR-CHANGE' in line and 'EXT' in line)):
                    lvb_str.append(line)       
            
            # result list to store filtered columns. after 10th column from last remaining values in 1 column.
            result = []  
            for line in lvb_str:
                lvb_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                # Join the first part of the splitter except the last 10 elements and store it as space_name
                space_name = " ".join(splitter[:-10])
                # Add space_name as the first element of lvb_list
                lvb_list=splitter[-10:]
                lvb_list.insert(0,space_name)
                # Append lvb_list to result
                result.append(lvb_list)
                
            # strore list to dataframe
            lvb_df = pd.DataFrame(result) 
            # Allot lvb_df columns from sim file
            lvb_df.columns = ['SPACE', 'SPACE*FLOOR', 'SPACE_TYPE', 'AZIMUTH', 
                                'LIGHTS', 'PEOPLE', 'EQUIP', 'INFILTRATION_METHOD', 'ACH',
                                'AREA(SQFT)', 'VOLUME(CUFT)']
            
            # convert below columns of lvb_df to numeric datatypes
            lvb_df['AREA(SQFT)'] = pd.to_numeric(lvb_df['AREA(SQFT)'])
            lvb_df['VOLUME(CUFT)'] = pd.to_numeric(lvb_df['VOLUME(CUFT)'])
            lvb_df['SPACE*FLOOR'] = pd.to_numeric(lvb_df['SPACE*FLOOR'])
            lvb_df['LIGHTS'] = pd.to_numeric(lvb_df['LIGHTS'])
            lvb_df['EQUIP'] = pd.to_numeric(lvb_df['EQUIP'])
            lvb_df['PEOPLE'] = pd.to_numeric(lvb_df['PEOPLE'])

            lvb_df['HEIGHT'] = lvb_df['VOLUME(CUFT)'] / lvb_df['AREA(SQFT)']
            # Set the index name of lvb_df to name
            lvb_df.index.name = name
            # Extract the filename from the path and store it in name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            name = name1.rsplit(".", 1)[0]
            lvb_df.insert(0, 'RUNNAME', name)
            return lvb_df

    except Exception as e:
        columns = ['RUNNAME', 'AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 
                                'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                            'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame(columns=columns)

def generateLighting(baseline, proposed, inp_file):
    # Write uploaded files to temporary files
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(baseline.read())
        temp_file_path_baseline = temp_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(proposed.read())
        temp_file_path_proposed = temp_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as temp_file:
        temp_file.write(inp_file.read())
        temp_file_path_inp = temp_file.name

    lv_b_proposed = get_LVB_Report(temp_file_path_proposed)
    lv_b_baseline = get_LVB_Report(temp_file_path_baseline)
    activity_desc_in_inp = get_Activity_Desc(temp_file_path_inp)

    mapping_df = pd.read_csv("database/eQUEST_database.csv")

    activity_desc = sorted(mapping_df["Code 2"].dropna().unique().tolist())

    if "rows" not in st.session_state:
        st.session_state.rows = []

    # Button to add a new row
    if st.button("➕ Add New Row"):
        st.session_state.rows.append({
            "Building ID": "",
            "Code 2": activity_desc[0],  # Default first option
            "Total Space Type Area (sqm)": "",
            "Maximum Allowance (W/sq m)": "",
            "Luminaire Mounting Height (m)": "",
            "Work-plane (m)": "",
            "Room Perimeter Length (m)": "",
            "Room Cavity Ratio": "",
            "Total Baseline LPD Allowance (W/sq m)": "",
            "Design LPD (W/sq m)": ""
        })

    # Table headers
    header = [
        "Building ID", "Table 9.6.1 Space Type", "Total Space Type Area (sqm)",
        "Maximum Allowance (W/sq m)", "Luminaire Mounting Height (m)",
        "Work-plane (m)", "Room Perimeter Length (m)", "Room Cavity Ratio",
        "Total Baseline LPD Allowance (W/sq m)", "Design LPD (W/sq m)"
    ]

    # Render table headers
    cols = st.columns(len(header))
    for i, col in enumerate(cols):
        col.markdown(f"**{header[i]}**")

    # Render each row
    for i, row in enumerate(st.session_state.rows):
        cols = st.columns(len(header))

        selected_space = cols[1].selectbox(
            f"space_type_{i}",
            activity_desc,
            index=activity_desc.index(row["Code 2"]) if row["Code 2"] in activity_desc else 0,
            key=f"dropdown_{i}"
        )

        db_row = mapping_df[mapping_df["Code 2"].str.strip().str.lower() == selected_space.strip().lower()]
        if not db_row.empty:
            db_row = db_row.iloc[0]
            st.session_state.rows[i].update({
                "Code 2": selected_space,
                "Maximum Allowance (W/sq m)": db_row.get("Maximum Allowance (W/sq m)", ""),
                "Luminaire Mounting Height (m)": db_row.get("Luminaire Mounting Height (m)", ""),
                "Work-plane (m)": db_row.get("Work-plane (m)", ""),
                "Room Perimeter Length (m)": db_row.get("Room Perimeter Length (m)", ""),
                "Room Cavity Ratio": db_row.get("Room Cavity Ratio", ""),
                "Total Baseline LPD Allowance (W/sq m)": db_row.get("Total Baseline LPD Allowance (W/sq m)", "")
            })

        # Render text inputs
        cols[0].text_input("Building ID", value=row["Building ID"], key=f"bldg_{i}")
        cols[2].text_input("Area", value=row["Total Space Type Area (sqm)"], key=f"area_{i}")
        cols[3].text_input("Max LPD", value=row["Maximum Allowance (W/sq m)"], key=f"max_lpd_{i}")
        cols[4].text_input("Mount Height", value=row["Luminaire Mounting Height (m)"], key=f"mount_{i}")
        cols[5].text_input("Work-plane", value=row["Work-plane (m)"], key=f"work_{i}")
        cols[6].text_input("Perimeter", value=row["Room Perimeter Length (m)"], key=f"perim_{i}")
        cols[7].text_input("Cavity Ratio", value=row["Room Cavity Ratio"], key=f"cavity_{i}")
        cols[8].text_input("Total LPD Allowance", value=row["Total Baseline LPD Allowance (W/sq m)"], key=f"allow_{i}")
        cols[9].text_input("Design LPD", value=row["Design LPD (W/sq m)"], key=f"design_{i}")