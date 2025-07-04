import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw 
import re
import streamlit as st
import tempfile

warnings.filterwarnings("ignore")

def extract_after_FOR(row):
    try:
        idx = row.tolist().index('FOR')
        return ' '.join(str(x) for x in row[idx+1:] if pd.notna(x) and str(x).strip() != '')
    except ValueError:
        return ''

def replace_zeros_right(df):
    df_copy = df.copy()
    for i in df_copy.index:
        found = False
        for j, col in enumerate(df_copy.columns):
            val = df_copy.at[i, col]
            if isinstance(val, str) and val.startswith('0.00') and '*' in val:
                found = True
                df_copy.at[i, col] = '0.00'
            elif found:
                df_copy.at[i, col] = '0.00'
    return df_copy

def get_LVG_Report(name):
    with open(name) as f:
        flist = f.readlines()

        lvd_count = [] 
        for num, line in enumerate(flist, 0):
            if 'LV-G' in line:
                lvd_count.append(num)
            if 'LV-H' in line:
                numend = num
        numstart = lvd_count[0] 
        lvd_rpt = flist[numstart:numend]

        lvd_str = []
        space = []

        for idx, line in enumerate(lvd_rpt):
            if ('ON/OFF' in line or 'FRACTION' in line or 'TEMPERATURE' in line or 'MULTIPLIER' in line or 'ON/OFF/FLAG' in line or 'RESET-TEMP' in line or 'FRAC/DESIGN' in line or 'FOR DAYS' in line) and 'Schedule:' in line:
                lvd_str.append(line)
            if ('FOR DAYS' in line):
                lvd_str.append(line)
            if 'HOUR' in line:
                if idx + 2 < len(lvd_rpt):
                    lvd_str.append(lvd_rpt[idx + 2])

        result = []  
        for line in lvd_str:
            lvd_list = []
            splitter = line.split()
            space_name = " ".join(splitter[:-24])
            lvd_list=splitter[-24:]
            lvd_list.insert(0,space_name)
            result.append(lvd_list)

        df = pd.DataFrame(result)
        df['Schedule'] = ''
        df['Type of Schedule'] = ''
        df['Day Type'] = ''
        df = df[['Schedule', 'Type of Schedule', 'Day Type'] + [col for col in df.columns if col not in ['Schedule', 'Type of Schedule', 'Day Type']]]
        
        df = df.copy()
        current_schedule = None
        current_type = None
        for i in range(len(df)):
            row_values = df.iloc[i].astype(str).tolist()
            combined = " ".join(row_values)
            
            if "Schedule:" in combined:
                schedule_parts = combined.split("Schedule:")
                if len(schedule_parts) > 1:
                    schedule_split = schedule_parts[1].strip().split()
                    current_schedule = schedule_split[0]

                if "Type of Schedule:" in combined:
                    type_split = combined.split("Type of Schedule:")[-1].strip().split()
                    current_type = type_split[0]
                elif "Schedule:" in combined and "Type" in combined:
                    parts = combined.split()
                    if "Type" in parts and "of" in parts and "Schedule:" in parts:
                        try:
                            type_idx = parts.index("Schedule:") + 1
                            current_type = parts[type_idx]
                        except:
                            pass
            df.at[i, 'Schedule'] = current_schedule
            df.at[i, 'Type of Schedule'] = current_type  

        df = df[~df.apply(lambda row: row.astype(str).str.contains("Schedule:").any(), axis=1)]
        df.drop(df.columns[3], axis=1, inplace=True)
        df = replace_zeros_right(df)
        df['Day Type'] = df.apply(extract_after_FOR, axis=1)
        # Replace empty strings with NaN
        df['Day Type'] = df['Day Type'].replace('', pd.NA) 

        # Forward fill
        df['Day Type'] = df['Day Type'].fillna(method='ffill')
        df = df.replace('', pd.NA)  # Convert empty strings to NA
        df = df.dropna()

    return df

def generateSchedules(baseline, proposed):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(baseline.read())
        temp_file_path_baseline = temp_file.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(proposed.read())
        temp_file_path_proposed = temp_file.name

    lv_g_proposed = get_LVG_Report(temp_file_path_proposed)
    lv_g_baseline = get_LVG_Report(temp_file_path_baseline)
    st.markdown("<h6 style='color: red;'>🗂️ Baseline LV-G Report - Details of Schedules</h3>", unsafe_allow_html=True)
    st.write(lv_g_baseline)
    st.markdown("<h6 style='color: red;'>🗂️ Proposed LV-G Report - Details of Schedules</h3>", unsafe_allow_html=True)
    st.write(lv_g_proposed)