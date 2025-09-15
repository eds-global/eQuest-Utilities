import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw 
import re
import streamlit as st
import tempfile
import numpy as np

warnings.filterwarnings("ignore")

def get_SVA_Zone_Report(name):
    with open(name) as f:
        flist = f.readlines()

        sva_counts = [] 
        for num, line in enumerate(flist, 0):
            if 'SV-A' in line:
                sva_counts.append(num)
            if 'SS-D' in line:
                numend = num
        numstart = sva_counts[0] 
        sva_rpt = flist[numstart:numend]
        
        sva_str = []
        for line in sva_rpt:
            if (('zn' in line and '.' in line) or ('Zn' in line and '.' in line) or
                ('Zone' in line and '.' in line) or ('zone' in line and '.' in line)):
                sva_str.append(line)

        result = []  
        for line in sva_str:
            sva_list = []
            splitter = line.split()
            space_name = " ".join(splitter[:-11])
            sva_list=splitter[-11:]
            sva_list.insert(0,space_name)
            result.append(sva_list)

        sva_zone = pd.DataFrame(result)
        sva_zone.columns = ['ZONE_NAME', 'SUPPLY-FLOW(CFM)', 'EXHAUST-FLOW(CFM)',
                        'FAN(KW)', 'MINIMUM_FLOW(FRAC)', 'OUTISIDE-AIR-FLOW(CFM)',
                        'COOLING_CAPACITY(KBTU/HR)', 'SENSIBLE(FRAC)', 'EXTRACTION-RATE(KBTU/HR)',
                        'HEATING_CAPACITY(KBTU/HR)', 'ADDITION-RATE(KBTU/HR)', 'ZONE-MULT']
        sva_zone.index.name = name
        value_before_backslash = ''.join(reversed(name)).split("\\")[0]
        name1 = ''.join(reversed(value_before_backslash))
        name = name1.rsplit(".", 1)[0]
        # sva_zone.insert(0, 'RUNNAME', name)
        # Dropping rows where 'ZONE_NAME' column does not contain specified substrings
        sva_zone = sva_zone[sva_zone['ZONE_NAME'].str.contains(r'\bzn\b|\bZn\b|\bZone\b|\bzone\b|\b\b')]
        # Dropping rows where 'SUPPLY-FLOW(CFM)' column does not contain specified substrings
        sva_zone = sva_zone[sva_zone['SUPPLY-FLOW(CFM)'].str.contains(r'\b\b')]
        # Replace non-numeric values with NaN in 'SUPPLY-FLOW(CFM)'
        sva_zone['SUPPLY-FLOW(CFM)'] = pd.to_numeric(sva_zone['SUPPLY-FLOW(CFM)'], errors='coerce')
        # Adding 'SPACES' column based on 'SUPPLY-FLOW(CFM)' condition
        sva_zone['SPACES'] = np.where(sva_zone['SUPPLY-FLOW(CFM)'] == 0, 'UnConditioned', 'Conditioned')
        
    return sva_zone

def get_SVA_Report(name):
    with open(name) as f:
        flist = f.readlines()

        sva_count = [] 
        for num, line in enumerate(flist, 0):
            if 'SV-A' in line:
                sva_count.append(num)
            if 'SS-D' in line:
                numend = num
        numstart = sva_count[0] 
        sva_rpt = flist[numstart:numend]
        
        sva_str = []
        for line in sva_rpt:
            if (('SUM' in line and '.' in line) or ('PTAC' in line and '.' in line and 'WEATHER' not in line) or
                ('VAVS' in line and '.' in line) or ('PIU' in line and '.' in line) or 
                ('FC' in line and 'zn' not in line and 'Zn' not in line and '.' in line) or 
                ('UVT' in line and '.' in line) or
                ('PSZ' in line and '.' in line) or ('PMZS' in line and '.' in line)):
                sva_str.append(line)

        result = []  
        for line in sva_str:
            sva_list = []
            splitter = line.split()
            space_name = " ".join(splitter[:-10])
            sva_list=splitter[-10:]
            sva_list.insert(0,space_name)
            result.append(sva_list)

        sva_df = pd.DataFrame(result)
        sva_df.columns = ['SYSTEM_TYPE', 'ALTITUDE_FACTOR', 'FLOOR_AREA(SQFT)',
                        'MAX_PEOPLE', 'OUTSIDE_AIR_RATIO', 'COOLING_CAPACITY(KBTU/HR)',
                        'SENSIBLE(SHR)', 'HEATING_CAPACITY(KBTU/HR)', 'COOLING_EIR(BTU/BTU)', 'HEATING_EIR(BTU/BTU)', 'HEAT_PUMP(SUPP_HEAT)(KBTU/HR)']
        sva_df['FLOOR_AREA(SQFT)'] = pd.to_numeric(sva_df['FLOOR_AREA(SQFT)'])
        sva_df.index.name = name
        value_before_backslash = ''.join(reversed(name)).split("\\")[0]
        name1 = ''.join(reversed(value_before_backslash))
        name = name1.rsplit(".", 1)[0]
        # sva_df.insert(0, 'RUNNAME', name)
        
    return sva_df

def get_LVB_Report(name):
    with open(name) as f:
        # Read all lines from the file and store them in a list named flist
        flist = f.readlines()

        # Initialize an empty list to store line numbers where 'LV-B' occurs
        lvb_count = [] 
        # Iterate through each line in flist along with its line number
        for num, line in enumerate(flist, 0):
            # If 'LV-B' is in the line, append its line number to lvb_count list
            if 'LV-B' in line:
                lvb_count.append(num)
            # If 'LV-C' is in the line, store its line number as numend
            if 'LV-C' in line:
                numend = num
        numstart = lvb_count[0] 
        
        # Slice flist from the start of 'LV-B' to the line before 'LV-C' and store it in lvb_rpt
        lvb_rpt = flist[numstart:numend]
        
        lvb_str = []
        # Iterate through each line in lvb_rpt
        for line in lvb_rpt:
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
                             'LIGHTS(WATT / SOFT)', 'PEOPLE', 'EQUIP(WATT / SOFT)', 'INFILTRATION_METHOD', 'ACH',
                             'AREA(SQFT)', 'VOLUME(CUFT)']
        
        # convert below columns of lvb_df to numeric datatypes
        lvb_df['AREA(SQFT)'] = pd.to_numeric(lvb_df['AREA(SQFT)'])
        lvb_df['VOLUME(CUFT)'] = pd.to_numeric(lvb_df['VOLUME(CUFT)'])
        lvb_df['SPACE*FLOOR'] = pd.to_numeric(lvb_df['SPACE*FLOOR'])
        lvb_df['LIGHTS(WATT / SOFT)'] = pd.to_numeric(lvb_df['LIGHTS(WATT / SOFT)'])
        lvb_df['EQUIP(WATT / SOFT)'] = pd.to_numeric(lvb_df['EQUIP(WATT / SOFT)'])
        lvb_df['PEOPLE'] = pd.to_numeric(lvb_df['PEOPLE'])

        lvb_df['HEIGHT'] = lvb_df['VOLUME(CUFT)'] / lvb_df['AREA(SQFT)']
        # Set the index name of lvb_df to name
        lvb_df.index.name = name
        # Extract the filename from the path and store it in name
        value_before_backslash = ''.join(reversed(name)).split("\\")[0]
        name1 = ''.join(reversed(value_before_backslash))
        name = name1.rsplit(".", 1)[0]
        # Insert a new column named 'RUNNAME' containing the filename
        # lvb_df.insert(0, 'RUNNAME', name)
        
        return lvb_df

def getProcessLoads(database, proposed, baseline):
    # --- Load SIM file temporarily ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(proposed.read())
        temp_file_path_proposed = temp_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(baseline.read())
        temp_file_path_baseline = temp_file.name

    # Extract baseline load data
    lv_d_proposed = get_LVB_Report(temp_file_path_proposed)
    lv_d_baseline = get_LVB_Report(temp_file_path_baseline)
    sv_a_baseline = get_SVA_Report(temp_file_path_baseline)
    sv_a_zone_df = get_SVA_Zone_Report(temp_file_path_baseline)

    # Keep necessary columns only
    lv_d_baseline = lv_d_baseline[['SPACE', 'AREA(SQFT)', 'EQUIP(WATT / SOFT)', 'LIGHTS(WATT / SOFT)']]
    lv_d_proposed = lv_d_proposed[['SPACE', 'AREA(SQFT)', 'EQUIP(WATT / SOFT)', 'LIGHTS(WATT / SOFT)']]

    ############################ STEP 1 ############################
    merged_df = lv_d_baseline.merge(
        lv_d_proposed,
        on='SPACE',
        suffixes=('_baseline', '_proposed'),
        how='outer'
    )

    # 3. Check matching
    merged_df['Mark'] = merged_df.apply(
        lambda row: "Yes" if (
            row['AREA(SQFT)_baseline'] == row['AREA(SQFT)_proposed'] and
            row['EQUIP(WATT / SOFT)_baseline'] == row['EQUIP(WATT / SOFT)_proposed']
        ) else "No",
        axis=1
    )

    # Create Code 3
    database['Code 3'] = database['Code'].astype(str).str[:2].str.capitalize() + \
                            database['Space type'].astype(str).str[:2].str.capitalize()

    lv_b_baseline = lv_d_baseline.dropna(subset=['SPACE'])
    filtered_data = database[['Building_Type', 'Code 3']].dropna()

    summary_rows = []
    for btype in filtered_data['Building_Type'].unique():
        btype_filtered = filtered_data[filtered_data['Building_Type'] == btype]
        matched_rows = []

        for _, row in lv_b_baseline.iterrows():
            space_val = str(row['SPACE'])
            for _, code_row in btype_filtered.iterrows():
                code_3 = str(code_row['Code 3'])
                if code_3 in space_val:
                    matched_rows.append({
                        'AREA(SQFT)': row['AREA(SQFT)'],
                        'EQUIP(WATT / SOFT)': row['EQUIP(WATT / SOFT)'],
                        'LIGHTS(WATT / SOFT)': row['LIGHTS(WATT / SOFT)']
                    })
                    break

        if matched_rows:
            matched_df = pd.DataFrame(matched_rows)
            total_area = matched_df['AREA(SQFT)'].sum()
            weighted_equip = (matched_df['AREA(SQFT)'] * matched_df['EQUIP(WATT / SOFT)']).sum() / total_area
            weighted_light = (matched_df['AREA(SQFT)'] * matched_df['LIGHTS(WATT / SOFT)']).sum() / total_area
            summary_rows.append({
                'Building Type': btype,
                'AREA(SQFT)': total_area,
            })

    if (merged_df['Mark'] == 'Yes').all():
        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)

            # Add TOTAL row
            grand_total_area = summary_df['AREA(SQFT)'].sum()
            total_row = pd.DataFrame([{
                'Building Type': 'TOTAL',
                'AREA(SQFT)': grand_total_area,
            }])
            summary_df = pd.concat([summary_df, total_row], ignore_index=True)
        else:
            st.warning("No matches found for any building type.")

        #############################################################
        # --- Prepare matched and unmatched spaces ---
        database['Code 3'] = (
            database['Code'].astype(str).str[:2].str.capitalize() +
            database['Space type'].astype(str).str[:2].str.capitalize()
        )

        lv_b_proposed = lv_d_proposed.dropna(subset=['SPACE'])
        filtered_data = database[['Building_Type', 'Code 3']].dropna()

        matched_spaces, unmatched_spaces = [], []
        for _, row in lv_b_proposed.iterrows():
            space_val = str(row['SPACE'])
            matched_type = None
            for _, code_row in filtered_data.iterrows():
                if str(code_row['Code 3']) in space_val:
                    matched_type = code_row['Building_Type']
                    break
            if matched_type:
                matched_spaces.append({
                    'SPACE': space_val,
                    'Building Type': matched_type,
                    'AREA(SQFT)': row['AREA(SQFT)'],
                    'EQUIP(WATT / SOFT)': row['EQUIP(WATT / SOFT)'],
                    'LIGHTS(WATT / SOFT)': row['LIGHTS(WATT / SOFT)']
                })
            else:
                unmatched_spaces.append({
                    'SPACE': space_val,
                    'AREA(SQFT)': row['AREA(SQFT)'],
                    'EQUIP(WATT / SOFT)': row['EQUIP(WATT / SOFT)'],
                    'LIGHTS(WATT / SOFT)': row['LIGHTS(WATT / SOFT)']
                })

        matched_df = pd.DataFrame(matched_spaces) if matched_spaces else pd.DataFrame(
            columns=['SPACE', 'Building Type', 'AREA(SQFT)', 'EQUIP(WATT / SOFT)', 'LIGHTS(WATT / SOFT)'])

        st.markdown("###### ⚠️ Map Unmatched Spaces")
        if unmatched_spaces:
            with st.form("mapping_form"):
                col1, col2 = st.columns([2.8, 1.2])
                with col1:
                    unmatched_df = pd.DataFrame(unmatched_spaces).reset_index(drop=True)

                    if "mapped_spaces" not in st.session_state:
                        st.session_state.mapped_spaces = set()
                    if "mapped_df" not in st.session_state:
                        st.session_state.mapped_df = pd.DataFrame(
                            columns=["SPACE", "AREA(SQFT)", "EQUIP(WATT / SOFT)", "LIGHTS(WATT / SOFT)", "Building Type"]
                        )
                        
                    selected_spaces = []
                    cols = st.columns(4)
                    for i, row in unmatched_df.iterrows():
                        col = cols[i % 4]
                        is_disabled = row['SPACE'] in st.session_state.mapped_spaces
                        # 
                        checked = col.checkbox(
                            f"{row['SPACE']}",
                            key=f"check_{i}",
                            disabled=is_disabled
                        )
                        if checked and not is_disabled:
                            selected_spaces.append(row['SPACE'])

                    building_types_list = database['Building_Type'].dropna().unique()

                with col2:
                    selected_btype = st.selectbox(
                        "Building Type",
                        options=sorted(building_types_list, key=str.lower),
                        label_visibility="collapsed"
                    )
                    submit = st.form_submit_button("✅ Map Selected")
                    if submit:
                        for space in selected_spaces:
                            st.session_state.mapped_spaces.add(space)
                            row_data = unmatched_df[unmatched_df['SPACE'] == space].copy()
                            row_data["Building Type"] = selected_btype
                            st.session_state.mapped_df = pd.concat(
                                [st.session_state.mapped_df, row_data], ignore_index=True
                            )
                        st.success(f"Mapped {len(selected_spaces)} spaces to '{selected_btype}'")

                        # for space in selected_spaces:
                        #     st.session_state.mapped_spaces.add(space)
                        #     row_data = unmatched_df[unmatched_df['SPACE'] == space].copy()
                        #     row_data["Building Type"] = selected_btype
                        #     st.session_state.mapped_df = pd.concat(
                        #         [st.session_state.mapped_df, row_data], ignore_index=True
                        #     )
                        # st.success(f"Mapped {len(selected_spaces)} spaces to '{selected_btype}'")

        # --- Build final_df always (even if no new mapping) ---
        if not st.session_state.mapped_df.empty:
            final_df = pd.concat([matched_df, st.session_state.mapped_df], ignore_index=True)
        else:
            final_df = matched_df.copy()

        # --- Build summary_df ---
        summary_rows = []
        mark = 'Yes'
        for btype in final_df['Building Type'].unique():
            temp_df = final_df[final_df['Building Type'] == btype]
            area = temp_df['AREA(SQFT)'].sum()
            weighted_equip = (temp_df['AREA(SQFT)'] * temp_df['EQUIP(WATT / SOFT)']).sum() / area
            weighted_light = (temp_df['AREA(SQFT)'] * temp_df['LIGHTS(WATT / SOFT)']).sum() / area

            baseline_spaces = lv_d_baseline[lv_d_baseline['SPACE'].isin(temp_df['SPACE'])]
            if not baseline_spaces.empty:
                baseline_light = (
                    (baseline_spaces['AREA(SQFT)'] * baseline_spaces['LIGHTS(WATT / SOFT)']).sum()
                    / baseline_spaces['AREA(SQFT)'].sum()
                )
            else:
                baseline_light = None

            summary_rows.append({
                'Building Type': btype,
                'AREA(SQFT)': area,
                'EQUIP(WATT / SOFT)': round(weighted_equip, 2),
                'LIGHTS(WATT / SOFT)': round(weighted_light, 2),
                'LIGHTS(WATT / SOFT) (Baseline)': round(baseline_light, 2) if baseline_light is not None else None,
                'Baseline Modeled Identically': mark
            })

        summary_df = pd.DataFrame(summary_rows)
        total_area = summary_df['AREA(SQFT)'].sum()
        total_equip = (summary_df['AREA(SQFT)'] * summary_df['EQUIP(WATT / SOFT)']).sum() / total_area
        total_light = (summary_df['AREA(SQFT)'] * summary_df['LIGHTS(WATT / SOFT)']).sum() / total_area
        total_light_baseline = (summary_df['AREA(SQFT)'] * summary_df['LIGHTS(WATT / SOFT) (Baseline)']).sum() / total_area
        total_row = pd.DataFrame([{
            'Building Type': 'TOTAL',
            'AREA(SQFT)': total_area,
            'EQUIP(WATT / SOFT)': round(total_equip, 2),
            'LIGHTS(WATT / SOFT)': round(total_light, 2),
            'LIGHTS(WATT / SOFT) (Baseline)': round(total_light_baseline, 2)
        }])
        summary_df = pd.concat([summary_df, total_row], ignore_index=True)

        # --- Display table with delete buttons ---
        st.markdown("###### 📝 Mapped Spaces: Review & Edit")

        table_data = summary_df.to_dict('records')

        # Table Header
        header_cols = st.columns([1, 0.5, 0.5, 0.5])
        for col, header in zip(header_cols, ["Building Type", "AREA (SQFT)", "EQUIP (WATT / SQFT)", "Action"]):
            col.markdown(f"**{header}**")

        # Table Rows
        for i, row in enumerate(table_data):
            row_cols = st.columns([1, 0.5, 0.5, 0.5])
            row_cols[0].write(row['Building Type'])
            row_cols[1].write(f"{row['AREA(SQFT)']:.2f}")
            row_cols[2].write(f"{row['EQUIP(WATT / SOFT)']:.2f}")

            if row['Building Type'] != "TOTAL":
                # ✅ Only allow delete if this building type exists in mapped_df
                if row['Building Type'] in st.session_state.mapped_df['Building Type'].tolist():
                    if row_cols[3].button("🗑️ Delete", key=f"del_{i}"):
                        st.session_state.mapped_df = st.session_state.mapped_df[
                            st.session_state.mapped_df['Building Type'] != row['Building Type']
                        ]
                        removed_spaces = final_df[final_df['Building Type'] == row['Building Type']]['SPACE'].tolist()
                        for space in removed_spaces:
                            st.session_state.mapped_spaces.discard(space)
                        st.rerun()
                else:
                    # 🔒 Show info instead of blank (for auto-matched)
                    row_cols[3].markdown("🔒 Auto-matched", unsafe_allow_html=True)
            else:
                row_cols[3].write("")

        # --- Show matched spaces detail ---
        with st.expander("✅ See List of Matched Spaces"):   # CHANGE title
            if not final_df.empty:
                st.markdown("##### 📋 Current Matched Spaces (Auto + Manual)")
                st.dataframe(final_df)
            else:
                st.info("No matched spaces found yet.")

        return summary_df, sv_a_baseline, sv_a_zone_df

    else:
        st.error("Baseline didn't Modeled Identically")