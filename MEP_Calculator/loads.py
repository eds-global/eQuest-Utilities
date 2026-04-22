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

def get_PVA_Pumps(name):
    with open(name) as f:
        flist = f.readlines()

        sva_counts = [] 
        for num, line in enumerate(flist, 0):
            if 'PV-A' in line:
                sva_counts.append(num)
            if 'PS-A' in line:
                numend = num
        numstart = sva_counts[0] 
        sva_rpt = flist[numstart:numend]
        
        sva_str = []
        for line in sva_rpt:
            if('-SPEED' in line and '.' in line) or ('PRIMARY' in line and '*' not in line) or ('EVAPORATOR' in line) or 'CONDENSER' in line:
                sva_str.append(line)

        result = []  
        for line in sva_str:
            sva_list = []
            splitter = line.split()
            space_name = " ".join(splitter[:-7])
            sva_list=splitter[-7:]
            sva_list.insert(0,space_name)
            result.append(sva_list)

        df = pd.DataFrame(result)
        df = df.apply(right_align_row, axis=1, result_type='expand')
        rows = []
        for i in range(0, len(df), 2):
            main_row = df.iloc[i]
            extra_row = df.iloc[i+1]

            # Extract non-empty values from the next row
            extra_values = [str(v).strip() for v in extra_row if str(v).strip() != ""]

            # Build new column names for extra values
            extra_cols = [f"Extra_{j+1}" for j in range(len(extra_values))]

            # Combine values
            combined_values = extra_values + list(main_row)

            # Combine column names
            combined_cols = extra_cols + list(df.columns)

            rows.append(pd.Series(combined_values, index=combined_cols))

        result_df = pd.DataFrame(rows)

        # Ensure no duplicate columns
        result_df = result_df.loc[:, ~result_df.columns.duplicated()]
        new_cols = ['Pumps', 'Flow(GPM)', 'Head(ft)',
            'Head-Setpoint(ft)', 'Capacity Control', 'Power(kW)',
            'Mechanical Efficiency(Frac)', 'Motor Efficiency(FRAC)']
        # Rename last 8 columns
        result_df.rename(
            columns={old: new for old, new in zip(result_df.columns[-8:], new_cols)},
            inplace=True
        )
        
    return result_df

def get_PVA_Tower(name):
    with open(name) as f:
        flist = f.readlines()

        sva_counts = [] 
        for num, line in enumerate(flist, 0):
            if 'COOLING TOWERS *' in line:
                sva_counts.append(num)
            if 'PS-A' in line:
                numend = num
        numstart = sva_counts[0] 
        sva_rpt = flist[numstart:numend]
        
        sva_str = []
        for line in sva_rpt:
            if('.' in line and ':' not in line):
                sva_str.append(line)

        result = []  
        for line in sva_str:
            sva_list = []
            splitter = line.split()
            space_name = " ".join(splitter[:-6])
            sva_list=splitter[-6:]
            sva_list.insert(0,space_name)
            result.append(sva_list)

        df = pd.DataFrame(result)
        df.columns = [
            "Equipment type Attached to",
            "Capacity(MBTU/HR)",
            "Flow (GAL/MIN)",
            "Number OF Cells",
            "Fan Power per Cell(kW)",
            "Spray Power per Cell(kW)",
            "Auxilary(kW)"
        ]
        
    return df


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
            row_values = [str(v) for v in df.iloc[i]]
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

def get_PSE_report(name):
    try:
        with open(name) as f:
            flist = f.readlines()
    
            pse_count = [] 
            for num, line in enumerate(flist, 0):
                if 'PS-E' in line:
                    pse_count.append(num)
                if 'PS-F' in line:
                    numend = num
            numstart = pse_count[0] 
            pse_rpt = flist[numstart:numend]
            
            pse_str = []
            pse_type = []
            # Iterate through each line in lvb_rpt
            for line in pse_rpt:
                line = re.sub(r'(\d)\.(\d+)\.', r'\1. \2.', line)
                # Check conditions and append lines containing relevant data to lvb_str list
                if (('.' in line and 'KW' in line) or ('JAN' in line or 'FEB' in line or 'MAR' in line
                      or 'JUN' in line or 'APR' in line or 'MAY' in line or 'JUN' in line or 'JUL' in line or 'AUG' in line or
                      'SEP' in line or 'OCT' in line or 'NOV' in line or 'DEC' in line) or
                    ('.' in line and 'MAX KW' in line)):
                    pse_str.append(line)
                elif ("PS-E" in line and "WEATHER" in line):
                    pse_type.append(line)
            
            # result list to store filtered columns. after 10th column from last remaining values in 1 column.
            result = []  
            for line in pse_str:
                lvb_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                # Join the first part of the splitter except the last 10 elements and store it as space_name
                space_name = " ".join(splitter[:-13])
                # Add space_name as the first element of lvb_list
                lvb_list=splitter[-13:]
                lvb_list.insert(0,space_name)
                # Append lvb_list to result
                result.append(lvb_list)
                
            # strore list to dataframe
            pse_df = pd.DataFrame(result) 
            # # Allot lvb_df columns from sim file
            pse_df.columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_HEATING', 
                                 'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                                 'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']
            
            pse_df.index.name = name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            name = name1.rsplit(".", 1)[0]
            # pse_df.insert(0, 'RUNNAME', name)
            # print(pse_df) 
    
            # Find the index of the first occurrence of "JAN" followed by "FEB"
            start_index = None
            for i in range(len(pse_df) - 1):
                if pse_df['LIGHTS'][i] == 'JAN' and pse_df['LIGHTS'][i+1] == 'FEB':
                    start_index = i
                    break
    
            # If "JAN" followed by "FEB" found, delete rows from "JAN" to the end
            if start_index is not None:
                pse_df = pse_df.iloc[0:start_index]
    
            ########################################################################
    
            for i in range(len(pse_df)):
                if i < len(pse_df) - 1 and ((pse_df['UNIT'][i] == 'MAX KW' and pse_df['LIGHTS'][i+1] == 'KWH') or (pse_df['UNIT'][i] == 'MAX KW' and pse_df['UNIT'][i+1] == 'KWH')):
                    new_row = {'UNIT': '', 'LIGHTS': 'TOTAL'}  # New row to be inserted
                    pse_df = pd.concat([pse_df.iloc[:i+1], pd.DataFrame([new_row]), pse_df.iloc[i+1:]]).reset_index(drop=True)
    
            # This will tell how many meters we have in KW and KWH case(in CSV)
            countMeters = 0
            for i in range(len(pse_df)):
                if pse_df['LIGHTS'][i] == 'JAN':
                    countMeters += 1
    
            values = []
            for item in pse_type:
                start_index = item.find("for") + len("for")
                end_index = item.find("WEATHER")
                value = item[start_index:end_index].strip()
                values.append(value)
            values1 = list(dict.fromkeys(values))
    
            values2 = []
            for i in range(countMeters):
                values2.append(values1[i])
            
            # Iterate over DataFrame indices
            j = 0
            for i in range(len(pse_df)):
                if pse_df['LIGHTS'].iloc[i] == 'JAN':
                    new_row = {'UNIT': values2[j]}
                    pse_df = pd.concat([pse_df.iloc[:i], pd.DataFrame([new_row]), pse_df.iloc[i:]]).reset_index(drop=True)
                    j += 1
                    if(j == countMeters):
                        break
    
            # Reset index after concatenation
            pse_df.reset_index(drop=True, inplace=True)
            pse_df = pse_df.tail(2).reset_index(drop=True)
            # st.write(pse_df)
    
        return pse_df
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame(columns=columns)

def get_PVA_Primary_Report(name):
    try:
        with open(name) as f:
            flist = f.readlines()

        pva_count = [] 
        numend = None
        for num, line in enumerate(flist, 0):
            if 'PRIMARY EQUIPMENT' in line:
                pva_count.append(num)
            if 'COOLING TOWERS' in line:
                numend = num
        
        if not pva_count or numend is None:
            # Return an empty DataFrame if PV-A or PS-A are not found
            columns = ['RUNNAME', 'HEATING_CAPACITY(MBTU/HR)', 'COOLING_CAPACITY(MBTU/HR)', 'LOOP_FLOW(GAL/MIN)',
                       'TOTAL_HEAD(FT)', 'SUPPLY_UA PRODUCT(BTU/HR-F)', 'SUPPLY_LOSS_DT(F)',
                       'RETURN_UA PRODUCT(BTU/HR-F)', 'RETURN_LOSS_DT(F)', 'LOOP_VOLUME(GAL)', 'FLUID_HEAT(CAPACITY)(BTU/LB-F)']
            return pd.DataFrame(columns=columns)
        
        numstart = pva_count[0]
        pva_rpt = flist[numstart:numend]

        pva_str = []
        for line in pva_rpt:
            numeric_values = ''.join([char for char in line if char.isdigit() or char == '.'])
            if numeric_values and any(letter in line for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') and '/' not in line:
                pva_str.append(line)

        result = []  
        for line in pva_str:
            pva_list = []
            splitter = line.split()
            space_name = " ".join(splitter[:-5])
            pva_list=splitter[-5:]
            pva_list.insert(0,space_name)
            result.append(pva_list)

        # result = []  
        # for line in sva_str:
        #     sva_list = []
        #     splitter = line.split()
        #     space_name = " ".join(splitter[:-11])
        #     sva_list=splitter[-11:]
            # sva_list.insert(0,space_name)
            # result.append(sva_list)

        pva_df = pd.DataFrame(result) 
        pva_df = pva_df.replace(["", " "], np.nan)
        # 2. Select last 5 columns
        last5 = pva_df.columns[-5:]
        # Convert last 5 columns to numeric (non-numeric becomes NaN)
        pva_df[last5] = pva_df[last5].apply(pd.to_numeric, errors='coerce')

        # Keep rows where all last 5 columns are valid numbers (not NaN)
        pva_df = pva_df[pva_df[last5].notna().all(axis=1)]
        pva_df.columns = ['Equipment & Attached To', 'Rated Capacity(MBTU/HR)', 'Flow(GAL/MIN)',
                          'Rated EIR(FRAC)', 'Rated HIR(FRAC)', 'Auxiliary(kW)']
        pva_df.index.name = name
        value_before_backslash = ''.join(reversed(name)).split("\\")[0]
        name1 = ''.join(reversed(value_before_backslash))
        name = name1.rsplit(".", 1)[0]
        # pva_df.insert(0, 'RUNNAME', name)

        return pva_df
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['HEATING_CAPACITY(MBTU/HR)', 'COOLING_CAPACITY(MBTU/HR)', 'LOOP_FLOW(GAL/MIN)',
                   'TOTAL_HEAD(FT)', 'SUPPLY_UA PRODUCT(BTU/HR-F)', 'SUPPLY_LOSS_DT(F)',
                   'RETURN_UA PRODUCT(BTU/HR-F)', 'RETURN_LOSS_DT(F)', 'LOOP_VOLUME(GAL)', 'FLUID_HEAT(CAPACITY)(BTU/LB-F)']
        return pd.DataFrame(columns=columns)

def get_PVA_loop_Report(name):
    try:
        with open(name) as f:
            flist = f.readlines()

        pva_count = [] 
        numend = None
        for num, line in enumerate(flist, 0):
            if 'PV-A' in line:
                pva_count.append(num)
            if 'PS-A' in line:
                numend = num
        
        if not pva_count or numend is None:
            # Return an empty DataFrame if PV-A or PS-A are not found
            columns = ['RUNNAME', 'HEATING_CAPACITY(MBTU/HR)', 'COOLING_CAPACITY(MBTU/HR)', 'LOOP_FLOW(GAL/MIN)',
                       'TOTAL_HEAD(FT)', 'SUPPLY_UA PRODUCT(BTU/HR-F)', 'SUPPLY_LOSS_DT(F)',
                       'RETURN_UA PRODUCT(BTU/HR-F)', 'RETURN_LOSS_DT(F)', 'LOOP_VOLUME(GAL)', 'FLUID_HEAT(CAPACITY)(BTU/LB-F)']
            return pd.DataFrame(columns=columns)
        
        numstart = pva_count[0]
        pva_rpt = flist[numstart:numend]

        pva_str = []
        for line in pva_rpt:
            numeric_values = ''.join([char for char in line if char.isdigit() or char == '.'])
            if numeric_values and not any(letter in line for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
                pva_str.append(line)

        result = []  
        for line in pva_str:
            pva_list = line.split()[-10:]
            result.append(pva_list)

        pva_df = pd.DataFrame(result) 
        pva_df.columns = ['HEATING_CAPACITY(MBTU/HR)', 'COOLING_CAPACITY(MBTU/HR)', 'LOOP_FLOW(GAL/MIN)',
                          'TOTAL_HEAD(FT)', 'SUPPLY_UA PRODUCT(BTU/HR-F)', 'SUPPLY_LOSS_DT(F)',
                          'RETURN_UA PRODUCT(BTU/HR-F)', 'RETURN_LOSS_DT(F)', 'LOOP_VOLUME(GAL)', 'FLUID_HEAT(CAPACITY)(BTU/LB-F)']
        pva_df.index.name = name
        value_before_backslash = ''.join(reversed(name)).split("\\")[0]
        name1 = ''.join(reversed(value_before_backslash))
        name = name1.rsplit(".", 1)[0]
        pva_df.insert(0, 'RUNNAME', name)

        return pva_df
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['HEATING_CAPACITY(MBTU/HR)', 'COOLING_CAPACITY(MBTU/HR)', 'LOOP_FLOW(GAL/MIN)',
                   'TOTAL_HEAD(FT)', 'SUPPLY_UA PRODUCT(BTU/HR-F)', 'SUPPLY_LOSS_DT(F)',
                   'RETURN_UA PRODUCT(BTU/HR-F)', 'RETURN_LOSS_DT(F)', 'LOOP_VOLUME(GAL)', 'FLUID_HEAT(CAPACITY)(BTU/LB-F)']
        return pd.DataFrame(columns=columns)

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

def get_LVD_report(name):
    try:
        # Open the file named 'name' and read its contents
        with open(name) as f:
            # Read all lines from the file and store them in a list named flist
            flist = f.readlines()
            
            # Initialize an empty list to store line numbers where 'LV-D' occurs
            lvd_count = [] 
            # Iterate through each line in flist along with its line number
            for num, line in enumerate(flist, 0):
                # If 'LV-D' is in the line, append its line number to lvd_count list
                if 'LV-D' in line:
                    lvd_count.append(num)
                # If 'LV-E' is in the line, store its line number as numend
                if 'LV-E' in line:
                    numend = num
            # Store the line number of the first occurrence of 'LV-B'
            numstart = lvd_count[0] 
             # Slice flist from the start of 'LV-D' to the line before 'LV-E' and store it in lvd_rpt
            lvd_rpt = flist[numstart:numend]
            
            # create two lists lvd_str and space to store lines between LV-D and LV-E 
            lvd_str = []
            space = [] # space list to store space type
            # iterate in each line of lvd_rpt
            for line in lvd_rpt:
                # condition for each line to get the specific rows
                if ('NORTH' in line  or 'SOUTH' in line or 'NORTH-EAST' in line or 'EAST' in line
                    or 'NORTH-WEST' in line  or 'SOUTH-WEST' in line or 'SOUTH-EAST' in line or 'WEST' in line
                    or "ROOF" in line or 'UNDERGRND' in line or 'FLOOR' in line):
                    lvd_str.append(line)
                # condition to store line which contains 'in space'
                elif ('in space:' in line):
                    space.append(line)
            
            # result list to store filtered columns. after 7th column from last remaining values in 1 column. 
            result = []  
            for line in lvd_str:
                lvd_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                 # Join the first part of the splitter except the last 7 elements and store it as space_name
                space_name = " ".join(splitter[:-7])
                # Add space_name as the first element of lvd_list
                lvd_list=splitter[-7:]
                lvd_list.insert(0,space_name)
                # Append lvd_list to result
                result.append(lvd_list)
            
            # stores result list to dataframe as lvd_df
            lvd_df = pd.DataFrame(result) 
            # Allot lvd_df columns from sim file
            lvd_df.columns = ['SURFACE', 'U-VALUE_Window(BTU/HR-SQFT-F)', 'AREA_Window(SQFT)', 'U-VALUE_Wall(BTU/HR-SQFT-F)',
                                'AREA_Wall(SQFT)', 'U-VALUE_Wall_Wind(BTU/HR-SQFT-F)', 'AREA_Wall_Wind(SQFT)', 'AZIMUTH']
            # drop that rows in lvd_df if AZIMUTH column in numeric values.
            lvd_df = lvd_df[~pd.to_numeric(lvd_df['AZIMUTH'], errors='coerce').notna()]
            Azi = lvd_df['AZIMUTH'].to_list()
            # list to add new column in lvd_df dataframe
            Grade_Express = []
            for azimuth in Azi:
                if azimuth == 'UNDERGRND':
                    Grade_Express.append('BG')
                else:
                    Grade_Express.append('AG')
            # adding new column in lvd_df report as- Grade-Expression
            lvd_df['Grade-Expression'] = Grade_Express
            
            # while len of space list is less, append azimuth
            while len(space) < len(Azi):
                space.append(Azi)
            # while len of space list is more, append space
            while len(Azi) < len(space):
                Azi.append(space)
            # put it into space_df dataframe
            space_df = pd.DataFrame({'AZIMUTH_': Azi, 'SPACE': space})
            # adding new column as space in lvd_df
            lvd_df = pd.concat([lvd_df, space_df], axis=1)
            # replace new line of last column as ''
            lvd_df[lvd_df.columns[-1]] = lvd_df[lvd_df.columns[-1]].str.replace('\n', '')
    
            # Set the index name of lvb_df to name
            lvd_df.index.name = name
            # Extract the filename from the path and store it in name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            # take the value before '.'
            name = name1.rsplit(".", 1)[0]
            # Insert a new column named 'RUNNAME' containing the filename
            lvd_df.insert(0, 'RUNNAME', name) 
            lvd_df = lvd_df.drop(columns=[lvd_df.columns[-2]])
            indices_to_delete = lvd_df[~lvd_df.iloc[:, -2].isin(['BG', 'AG'])].index
            lvd_df = lvd_df.drop(indices_to_delete)
            last_col = lvd_df.pop(lvd_df.columns[-1])
            lvd_df.insert(2, last_col.name, last_col)
            # in each row of 'SPACE' column ignore 'in space: ' string.
            lvd_df['SPACE'] = lvd_df['SPACE'].str.replace('in space: ','')
            
        return lvd_df
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['SURFACE', 'U-VALUE_Window(BTU/HR-SQFT-F)', 'AREA_Window(SQFT)', 'U-VALUE_Wall(BTU/HR-SQFT-F)',
                    'AREA_Wall(SQFT)', 'U-VALUE_Wall_Wind(BTU/HR-SQFT-F)', 'AREA_Wall_Wind(SQFT)', 'AZIMUTH']
        return pd.DataFrame(columns=columns)

def get_last_nonempty_value(row):
    for v in reversed(row.values):
        if v is None:
            continue
        s = str(v).strip()
        if s == "" or s.lower() == "nan":
            continue
        return s
    return None

def right_align_row(row):
    row_values = list(row)
    # Identify blanks
    blanks = [v for v in row_values if pd.isna(v) or v.strip() == ""]
    non_blanks = [v for v in row_values if not (pd.isna(v) or v.strip() == "")]
    return blanks + non_blanks

# Function to merge strings into 3rd last column
def merge_strings(row):
    parts = []
    for c in cols_to_check:
        val = str(row[c]).strip()
        if val.isalpha():  # only A–Z, a–z
            parts.append(val)
    if parts:
        # Merge with existing 3rd-last column
        row[col_3_last] = " ".join(parts + [str(row[col_3_last]).strip()])
        # blank out original columns
        for c in cols_to_check:
            if str(row[c]).strip().isalpha():
                row[c] = ""
    return row

def get_LVC_Exterior_Surfaces(name):
    import pandas as pd
    import re

    with open(name) as f:
        flist = f.readlines()

    # -------------------------------
    # FIND SECTION
    # -------------------------------
    lvb_count = []
    numend = None

    for num, line in enumerate(flist):
        if 'LV-C' in line:
            lvb_count.append(num)
        if 'LV-D' in line:
            numend = num

    if not lvb_count or numend is None:
        return pd.DataFrame(columns=["Surface", "Multiplier", "Area(ft²)", "Construction",
                                     "U-Value((BTU/HR-SQFT-F)", "Surface Type"])

    numstart = lvb_count[0]
    lvb_rpt = flist[numstart:numend]

    # -------------------------------
    # FILTER LINES
    # -------------------------------
    lvb_str = []
    for line in lvb_rpt:
        if ('.' in line and ('QUICK' in line or 'DELAYED' in line) and 'ADIABATIC' not in line):
            lvb_str.append(line)

    # -------------------------------
    # BUILD DATA
    # -------------------------------
    result = []
    for line in lvb_str:
        splitter = line.split()
        if len(splitter) < 7:
            continue

        space_name = " ".join(splitter[:-7])
        values = splitter[-7:]
        values.insert(0, space_name)
        result.append(values)

    if not result:
        return pd.DataFrame(columns=["Surface", "Multiplier", "Area(ft²)", "Construction",
                                     "U-Value((BTU/HR-SQFT-F)", "Surface Type"])

    df = pd.DataFrame(result)

    # -------------------------------
    # ALIGN
    # -------------------------------
    def right_align_row(row):
        row_values = list(row)
        blanks = [v for v in row_values if pd.isna(v) or str(v).strip() == ""]
        non_blanks = [v for v in row_values if not (pd.isna(v) or str(v).strip() == "")]
        return blanks + non_blanks

    df_aligned = df.apply(right_align_row, axis=1, result_type='expand')

    # -------------------------------
    # SAFE MERGE (THIS WAS CRASHING)
    # -------------------------------
    df_aligned2 = df_aligned.copy()

    cols_to_merge = df_aligned2.columns[:-5]  # ALWAYS DEFINE FIRST

    valid_cols = [col for col in cols_to_merge if col in df_aligned2.columns]

    if valid_cols:
        df_aligned2['Surface'] = (
            df_aligned2[valid_cols]
            .fillna('')
            .astype(str)
            .agg(lambda x: ' '.join(x), axis=1)
        )
    else:
        df_aligned2['Surface'] = ''

    # -------------------------------
    # FINAL CLEAN
    # -------------------------------
    df_aligned2 = df_aligned2.drop(df_aligned2.columns[:3], axis=1, errors='ignore')

    df_aligned2.columns = [
        "Multiplier", "Area(ft²)", "Construction",
        "U-Value((BTU/HR-SQFT-F)", "Surface Type", "Surface"
    ]

    df_aligned2["Surface"] = df_aligned2["Surface"].str.strip()

    # Move Surface first
    surface_col = df_aligned2.pop("Surface")
    df_aligned2.insert(0, "Surface", surface_col)

    return df_aligned2

def get_LVB_Report(name):
    # st.write(name)
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

# this function is to get lvd report summary report based on orientations and U value, Area 
# of walls and windows.
def get_LVD_Summary_report(name):
    try:
        with open(name) as f:
            flist = f.readlines()
    
            lvd_count = [] 
            for num, line in enumerate(flist, 0):
                if 'LV-D' in line:
                    lvd_count.append(num)
                if 'LV-E' in line:
                    numend = num
            numstart = lvd_count[0] 
            lvd_rpt = flist[numstart:numend]
            
            lvd_str = []
            for line in lvd_rpt:
                if ('NORTH' in line  or 'SOUTH' in line or 'NORTH-EAST' in line or 'EAST' in line
                    or 'NORTH-WEST' in line  or 'SOUTH-WEST' in line or 'SOUTH-EAST' in line or 'WEST' in line
                    or "ROOF" in line or 'UNDERGRND' in line or 'ALL WALLS' in line or 'BUILDING' in line or 
                    'WALLS+ROOFS' in line):
                    lvd_str.append(line)
                    
            result = []  
            for line in lvd_str:
                lvd_list = []
                splitter = line.split()
                space_name = " ".join(splitter[:-6])
                lvd_list=splitter[-6:]
                lvd_list.insert(0,space_name)
                result.append(lvd_list)
            
            # converting result to dataframe.
            lvd_summ = pd.DataFrame(result) 
            # allot with column names
            lvd_summ.columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
            lvd_summ = lvd_summ[pd.to_numeric(lvd_summ['WINDOW+WALL(AREA)(SQFT)'], errors='coerce').notna()]
            
            lvd_summ.index.name = name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            # get the value before '.' in 1st column
            name = name1.rsplit(".", 1)[0]
            # insert into 1st column as RUNNAME
            # lvd_summ.insert(0, 'RUNNAME', name)
            
        return lvd_summ
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame(columns=columns)

def getProcessLoads(database, proposed, baseline, sim90, sim180, sim270):
    import tempfile
    import pandas as pd
    import streamlit as st

    # =====================================================
    # SAVE TEMP FILES
    # =====================================================
    def save_temp(uploaded_file):
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
            temp_file.write(uploaded_file.getvalue())  # ✅ correct way
            temp_file.flush()
            return temp_file.name

    temp_file_path_proposed = save_temp(proposed)
    temp_file_path_baseline = save_temp(baseline)
    temp_file_path_sim90 = save_temp(sim90)
    temp_file_path_sim180 = save_temp(sim180)
    temp_file_path_sim270 = save_temp(sim270)

    # =====================================================
    # EXTRACT REPORTS
    # =====================================================
    lvc_exterior = get_LVC_Exterior_Surfaces(temp_file_path_baseline)
    pv_a_pumps = get_PVA_Pumps(temp_file_path_baseline)
    pv_a_pumps_p = get_PVA_Pumps(temp_file_path_proposed)
    pv_a_tower = get_PVA_Tower(temp_file_path_baseline)
    pv_a_tower_p = get_PVA_Tower(temp_file_path_proposed)

    lv_d_proposed = get_LVB_Report(temp_file_path_proposed)
    lv_d_baseline = get_LVB_Report(temp_file_path_baseline)
    lvd_base = get_LVD_report(temp_file_path_baseline)

    sv_a_baseline = get_SVA_Report(temp_file_path_baseline)
    sv_a_proposed = get_SVA_Report(temp_file_path_proposed)
    sv_a_zone_df = get_SVA_Zone_Report(temp_file_path_baseline)

    pv_a_loop = get_PVA_loop_Report(temp_file_path_baseline)
    pv_a_loop_p = get_PVA_loop_Report(temp_file_path_proposed)

    pv_a_primary = get_PVA_Primary_Report(temp_file_path_baseline)
    pv_a_primary_p = get_PVA_Primary_Report(temp_file_path_proposed)

    ps_e_baseline = get_PSE_report(temp_file_path_baseline)
    ps_e_proposed = get_PSE_report(temp_file_path_proposed)
    pse_90 = get_PSE_report(temp_file_path_sim90)
    pse_180 = get_PSE_report(temp_file_path_sim180)
    pse_270 = get_PSE_report(temp_file_path_sim270)

    lvd_summary_p = get_LVD_Summary_report(temp_file_path_proposed)
    lvd_summary_b = get_LVD_Summary_report(temp_file_path_baseline)

    lv_g_baseline = get_LVG_Report(temp_file_path_baseline)
    lv_g_proposed = get_LVG_Report(temp_file_path_proposed)

    # =====================================================
    # CLEAN REQUIRED COLUMNS
    # =====================================================
    keep_cols = ['SPACE', 'AREA(SQFT)', 'EQUIP(WATT / SOFT)', 'LIGHTS(WATT / SOFT)']
    lv_d_baseline = lv_d_baseline[keep_cols].copy()
    lv_d_proposed = lv_d_proposed[keep_cols].copy()

    # =====================================================
    # IDENTICAL CHECK
    # =====================================================
    merged_df = lv_d_baseline.merge(
        lv_d_proposed,
        on='SPACE',
        suffixes=('_baseline', '_proposed'),
        how='outer'
    )

    merged_df['Mark'] = merged_df.apply(
        lambda row: "Yes" if (
            row['AREA(SQFT)_baseline'] == row['AREA(SQFT)_proposed'] and
            row['EQUIP(WATT / SOFT)_baseline'] == row['EQUIP(WATT / SOFT)_proposed']
        ) else "No",
        axis=1
    )

    baseline_identical = (merged_df['Mark'] == 'Yes').all()

    # =====================================================
    # MASTER SPACE MAP
    # =====================================================
    space_to_btype = {
        "Mechan": "Electrical/mechanical",
        "Corrid": "Corridor/transition",
        "Archiv": "Storage",
        "Multip": "Conference/meeting/multipurpose",
        "Restro": "Restrooms",
        "Stairw": "Stairway",
        "Elevat": "Lobby - elevator",
        "Sales-": "Sales area",
        "Enclos": "Office - enclosed",
        "Break/": "Lounge/recreation",
        "Locker": "Locker room",
        "Lounge": "Lounge/recreation",
        "Dining": "Dining area",
        "Food": "Food preparation",
        "Lobby": "Lobby",
        "Workshop": "Workshop",
        "Family": "Dining area family dining",
        "Kitche": "Dining area family dining",
        "Readin": "Reading Area"
    }

    def map_space(space):
        try:
            room_code = str(space).split("_")[1]
            return space_to_btype.get(room_code)
        except:
            return None

    # =====================================================
    # AUTO MATCH PROPOSED
    # =====================================================
    final_df = lv_d_proposed.copy()
    final_df["Building Type"] = final_df["SPACE"].apply(map_space)

    matched_df = final_df.dropna(subset=["Building Type"]).copy()
    unmatched_df = final_df[final_df["Building Type"].isna()].copy()

    # =====================================================
    # SESSION STATE
    # =====================================================
    if "mapped_spaces" not in st.session_state:
        st.session_state.mapped_spaces = set()

    if "mapped_df" not in st.session_state:
        st.session_state.mapped_df = pd.DataFrame(
            columns=["SPACE", "AREA(SQFT)", "EQUIP(WATT / SOFT)", "LIGHTS(WATT / SOFT)", "Building Type"]
        )

    # =====================================================
    # MANUAL UI
    # =====================================================
    st.markdown("###### ⚠️ Map Unmatched Spaces")

    if not unmatched_df.empty:
        with st.form("mapping_form"):
            col1, col2 = st.columns([2.8, 1.2])

            with col1:
                selected_spaces = []
                cols = st.columns(4)

                for i, row in unmatched_df.iterrows():
                    col = cols[i % 4]
                    disabled = row["SPACE"] in st.session_state.mapped_spaces

                    checked = col.checkbox(
                        row["SPACE"],
                        key=f"space_{i}",
                        disabled=disabled
                    )

                    if checked and not disabled:
                        selected_spaces.append(row["SPACE"])

            with col2:
                selected_btype = st.selectbox(
                    "Building Type",
                    sorted(database["Building_Type"].dropna().unique())
                )

                submitted = st.form_submit_button("✅ Map Selected")

                if submitted:
                    for space in selected_spaces:
                        row_data = unmatched_df[unmatched_df["SPACE"] == space].copy()
                        row_data["Building Type"] = selected_btype

                        st.session_state.mapped_spaces.add(space)
                        st.session_state.mapped_df = pd.concat(
                            [st.session_state.mapped_df, row_data],
                            ignore_index=True
                        )

                    st.success(f"{len(selected_spaces)} spaces mapped")

    # =====================================================
    # FINAL MERGE
    # =====================================================
    final_df = pd.concat(
        [matched_df, st.session_state.mapped_df],
        ignore_index=True
    ).drop_duplicates(subset=["SPACE"])

    # =====================================================
    # SUMMARY
    # =====================================================
    summary_rows = []

    for btype in final_df["Building Type"].dropna().unique():
        temp_df = final_df[final_df["Building Type"] == btype]

        area = temp_df["AREA(SQFT)"].sum()

        equip = (
            temp_df["AREA(SQFT)"] * temp_df["EQUIP(WATT / SOFT)"]
        ).sum() / area

        light = (
            temp_df["AREA(SQFT)"] * temp_df["LIGHTS(WATT / SOFT)"]
        ).sum() / area

        baseline_spaces = lv_d_baseline[
            lv_d_baseline["SPACE"].isin(temp_df["SPACE"])
        ]

        baseline_light = None
        if not baseline_spaces.empty:
            baseline_light = (
                baseline_spaces["AREA(SQFT)"] *
                baseline_spaces["LIGHTS(WATT / SOFT)"]
            ).sum() / baseline_spaces["AREA(SQFT)"].sum()

        summary_rows.append({
            "Building Type": btype,
            "AREA(SQFT)": area,
            "EQUIP(WATT / SOFT)": round(equip, 2),
            "LIGHTS(WATT / SOFT)": round(light, 2),
            "LIGHTS(WATT / SOFT) (Baseline)": round(baseline_light, 2) if baseline_light else None,
            "Baseline Modeled Identically": "Yes" if baseline_identical else "No"
        })

    summary_df = pd.DataFrame(summary_rows)

    # TOTAL ROW
    if not summary_df.empty:
        total_area = summary_df["AREA(SQFT)"].sum()

        total_row = pd.DataFrame([{
            "Building Type": "TOTAL",
            "AREA(SQFT)": total_area,
            "EQUIP(WATT / SOFT)": round(
                (summary_df["AREA(SQFT)"] * summary_df["EQUIP(WATT / SOFT)"]).sum() / total_area, 2
            ),
            "LIGHTS(WATT / SOFT)": round(
                (summary_df["AREA(SQFT)"] * summary_df["LIGHTS(WATT / SOFT)"]).sum() / total_area, 2
            )
        }])

        summary_df = pd.concat([summary_df, total_row], ignore_index=True)

    # =====================================================
    # DISPLAY
    # =====================================================
    st.markdown("###### 📝 Process Load Summary")
    st.dataframe(summary_df)

    with st.expander("✅ See List of Matched Spaces"):
        st.dataframe(final_df)

    return (
        summary_df, sv_a_baseline, sv_a_zone_df, sv_a_proposed,
        pv_a_loop, pv_a_primary, ps_e_baseline,
        lvd_summary_p, lvd_summary_b,
        lv_g_baseline, lv_g_proposed,
        ps_e_proposed, pse_90, pse_180, pse_270,
        lvd_base, pv_a_pumps, pv_a_loop_p,
        pv_a_pumps_p, pv_a_primary_p,
        pv_a_tower, pv_a_tower_p
    )