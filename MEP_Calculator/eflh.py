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

def generateSchedules(baseline, proposed, holiday, monday, tuesday, wednesday, thursday, friday, saturday, sunday):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(baseline.read())
        temp_file_path_baseline = temp_file.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(proposed.read())
        temp_file_path_proposed = temp_file.name
    
    lv_g_proposed = get_LVG_Report(temp_file_path_proposed)
    lv_g_baseline = get_LVG_Report(temp_file_path_baseline)

    subset_b = lv_g_baseline.iloc[:, :24]
    numeric_subset_b = subset_b.apply(pd.to_numeric, errors='coerce')
    subset_p = lv_g_baseline.iloc[:, :24]
    numeric_subset_p = subset_p.apply(pd.to_numeric, errors='coerce')
    lv_g_baseline['Hours / Day'] = numeric_subset_b.sum(axis=1)
    lv_g_proposed['Hours / Day'] = numeric_subset_p.sum(axis=1)

    holiday = holiday
    weekday = monday + tuesday + wednesday + thursday + friday
    weekend = saturday + sunday

    def get_multiplier(day_type):
        day_type = str(day_type).upper()
        if 'HOL' in day_type:
            return holiday
        elif 'SAT' in day_type:
            return weekend
        elif 'CDD' in day_type:
            return weekday
        else:
            return weekday

    lv_g_baseline['Hours / Year'] = lv_g_baseline.apply(lambda row: row['Hours / Day'] * get_multiplier(row['Day Type']), axis=1)
    lv_g_proposed['Hours / Year'] = lv_g_proposed.apply(lambda row: row['Hours / Day'] * get_multiplier(row['Day Type']), axis=1)

    numeric_cols = lv_g_baseline.columns.difference(['Schedule'])
    result_baseline = pd.DataFrame(columns=lv_g_baseline.columns)
    numeric_cols_p = lv_g_proposed.columns.difference(['Schedule'])
    result_proposed = pd.DataFrame(columns=lv_g_proposed.columns)

    cols = lv_g_baseline.columns.tolist()
    second_last_col = cols[-2]
    last_col = cols[-1]
    cols_p = lv_g_proposed.columns.tolist()
    second_last_col_p = cols_p[-2]
    last_col_p = cols_p[-1]

    for name, group in lv_g_baseline.groupby('Schedule'):
        result_baseline = pd.concat([result_baseline, group], ignore_index=True)
        total_values = group[numeric_cols].sum()
        total_row = pd.Series("", index=lv_g_baseline.columns)
        total_row['Schedule'] = 'Total hours of operation'
        total_row[second_last_col] = total_values[second_last_col]
        total_row[last_col] = total_values[last_col]
        result_baseline = pd.concat([result_baseline, pd.DataFrame([total_row])], ignore_index=True)
    
    for name, group in lv_g_proposed.groupby('Schedule'):
        result_proposed = pd.concat([result_proposed, group], ignore_index=True)
        total_values = group[numeric_cols_p].sum()
        total_row_p = pd.Series("", index=lv_g_proposed.columns)
        total_row_p['Schedule'] = 'Total hours of operation'
        total_row_p[second_last_col] = total_values[second_last_col_p]
        total_row_p[last_col_p] = total_values[last_col_p]
        result_proposed = pd.concat([result_proposed, pd.DataFrame([total_row_p])], ignore_index=True)
    total_days = sum([holiday, monday, tuesday, wednesday, thursday, friday, saturday, sunday])
    data = {
        "Days per Year": [
            holiday,
            monday,
            tuesday,
            wednesday,
            thursday,
            friday,
            saturday,
            sunday,
            total_days
        ]
    }
    index = ["Holiday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Total (must equal 365 days/year)"]
    days_ = pd.DataFrame(data, index=index)
    st.markdown("<h6 style='color: red;'>🔰 Yearly Schedule Allocation</h3>", unsafe_allow_html=True)
    st.write(days_)
    st.markdown("<h6 style='color: red;'>🗂️ Baseline LV-G Report - Details of Schedules</h3>", unsafe_allow_html=True)
    st.write(result_baseline)
    st.markdown("<h6 style='color: red;'>🗂️ Proposed LV-G Report - Details of Schedules</h3>", unsafe_allow_html=True)
    st.write(result_proposed)