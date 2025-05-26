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

def get_END_USE(df, sim_files):
    end_use_map = {
        "Interior lighting": "LIGHTS",
        "Exterior lighting": "EXT USAGE",
        "Space heating": "SPACE_HEATING",
        "Space cooling": "SPACE_COOLING",
        "Pumps": "PUMPS & AUX",
        "Heat rejection": "HEAT_REJECT",
        "Fans - interior ventilation": "VENT FANS",
        "Service water heating": "DOMEST HOT WTR",
        "Receptacle equipment": ""
    }

    pse_dfs = []
    rotation_labels = [
        'Baseline 0° rotation',
        'Baseline 90° rotation',
        'Baseline 180° rotation',
        'Baseline 270° rotation',
    ]

    for i, sim_file in enumerate(sim_files):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
            temp_file.write(sim_file.read())
            temp_file_path = temp_file.name
            
        pse_df = get_PSE_report(temp_file_path)

        pse_df_int_light_kwh = pse_df['LIGHTS'][0]
        pse_df_int_light_kw = pse_df['LIGHTS'][1]
        pse_df_ext_light_kwh = pse_df['EXT USAGE'][0]
        pse_df_ext_light_kw = pse_df['EXT USAGE'][1]
        pse_df_heat_kwh = pse_df['SPACE_HEATING'][0]
        pse_df_heat_kw = pse_df['SPACE_HEATING'][1]
        pse_df_cool_kwh = pse_df['SPACE_COOLING'][0]
        pse_df_cool_kw = pse_df['SPACE_COOLING'][1]
        pse_df_pumps_kwh = pse_df['PUMPS & AUX'][0]
        pse_df_pumps_kw = pse_df['PUMPS & AUX'][1]
        pse_df_heat_reject_kwh = pse_df['HEAT_REJECT'][0]
        pse_df_heat_reject_kw = pse_df['HEAT_REJECT'][1]
        pse_df_fans_kwh = pse_df['VENT FANS'][0]
        pse_df_fans_kw = pse_df['VENT FANS'][1]
        pse_df_wtr_kwh = pse_df['DOMEST HOT WTR'][0]
        pse_df_wtr_kw = pse_df['DOMEST HOT WTR'][1]
        pse_df_equip_kwh = pse_df['MISC_EQUIP'][0]
        pse_df_equip_kw = pse_df['MISC_EQUIP'][1]

        col = rotation_labels[i]
        df[col][0] = float(pse_df_int_light_kwh)
        df[col][1] = float(pse_df_int_light_kw)
        df[col][2] = float(pse_df_ext_light_kwh)
        df[col][3] = float(pse_df_ext_light_kw)
        df[col][4] = float(pse_df_heat_kwh)
        df[col][5] = float(pse_df_heat_kw)
        df[col][6] = float(pse_df_cool_kwh)
        df[col][7] = float(pse_df_cool_kw)
        df[col][8] = float(pse_df_pumps_kwh)
        df[col][9] = float(pse_df_pumps_kw)
        df[col][10] = float(pse_df_heat_reject_kwh)
        df[col][11] = float(pse_df_heat_reject_kw)
        df[col][12] = float(pse_df_fans_kwh)
        df[col][13] = float(pse_df_fans_kw)
        df[col][16] = float(pse_df_wtr_kwh)
        df[col][17] = float(pse_df_wtr_kw)
        df[col][18] = float(pse_df_equip_kwh)
        df[col][19] = float(pse_df_equip_kw)

    cols = [
        'Baseline 0° rotation',
        'Baseline 90° rotation',
        'Baseline 180° rotation',
        'Baseline 270° rotation'
    ]
    df = df.iloc[:, :-4]
    # df = df.iloc[:, :-1]
    # df = df.drop(df.columns[1], axis=1)
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    total_0_degree = df['Baseline 0° rotation'].sum()
    total_90_degree = df['Baseline 90° rotation'].sum()
    total_180_degree = df['Baseline 180° rotation'].sum()
    total_270_degree = df['Baseline 270° rotation'].sum()
    df['Baseline 0° rotation'][49] = total_0_degree
    df['Baseline 90° rotation'][49] = total_90_degree
    df['Baseline 180° rotation'][49] = total_180_degree
    df['Baseline 270° rotation'][49] = total_270_degree
    df['Baseline 0° rotation'][50] = 0
    df['Baseline 90° rotation'][50] = 0
    df['Baseline 180° rotation'][50] = 0
    df['Baseline 270° rotation'][50] = 0
    df['Baseline 0° rotation'][51] = 0
    df['Baseline 90° rotation'][51] = 0
    df['Baseline 180° rotation'][51] = 0
    df['Baseline 270° rotation'][51] = 0
    df['Baseline Design Total (Average of 4 rotations)'] = df[cols].sum(axis=1) / 4

    st.success("Files processed and CSV updated successfully!")
    st.dataframe(df)

    st.download_button(
        label="Download Modified CSV",
        data=df.to_csv(index=False),
        file_name="modified_output.csv",
        mime="text/csv"
    ) 

def get_END_USE_Proposed(df, zero, ninty, oneeighty, twoseventy, proposed):
    sim_files = []
    sim_files.append(zero)
    sim_files.append(ninty)
    sim_files.append(oneeighty)
    sim_files.append(twoseventy)
    sim_files.append(proposed)

    end_use_map = {
        "Interior lighting": "LIGHTS",
        "Exterior lighting": "EXT USAGE",
        "Space heating": "SPACE_HEATING",
        "Space cooling": "SPACE_COOLING",
        "Pumps": "PUMPS & AUX",
        "Heat rejection": "HEAT_REJECT",
        "Fans - interior ventilation": "VENT FANS",
        "Service water heating": "DOMEST HOT WTR",
        "Receptacle equipment": ""
    }

    pse_dfs = []
    rotation_labels = [
        'Baseline 0° rotation',
        'Baseline 90° rotation',
        'Baseline 180° rotation',
        'Baseline 270° rotation',
        'Proposed'
    ]

    for i, sim_file in enumerate(sim_files):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
            temp_file.write(sim_file.read())
            temp_file_path = temp_file.name
            
        pse_df = get_PSE_report(temp_file_path)
        bepu_df = bepu.get_BEPU_report(temp_file_path)
        # st.write(pse_df)
        pse_df_int_light_kwh = pse_df['LIGHTS'][0]
        pse_df_int_light_kw = pse_df['LIGHTS'][1]
        pse_df_ext_light_kwh = pse_df['EXT USAGE'][0]
        pse_df_ext_light_kw = pse_df['EXT USAGE'][1]
        pse_df_heat_kwh = pse_df['SPACE_HEATING'][0]
        pse_df_heat_kw = pse_df['SPACE_HEATING'][1]
        pse_df_cool_kwh = pse_df['SPACE_COOLING'][0]
        pse_df_cool_kw = pse_df['SPACE_COOLING'][1]
        pse_df_pumps_kwh = pse_df['PUMPS & AUX'][0]
        pse_df_pumps_kw = pse_df['PUMPS & AUX'][1]
        pse_df_heat_reject_kwh = pse_df['HEAT_REJECT'][0]
        pse_df_heat_reject_kw = pse_df['HEAT_REJECT'][1]
        pse_df_fans_kwh = pse_df['VENT FANS'][0]
        pse_df_fans_kw = pse_df['VENT FANS'][1]
        pse_df_wtr_kwh = pse_df['DOMEST HOT WTR'][0]
        pse_df_wtr_kw = pse_df['DOMEST HOT WTR'][1]
        pse_df_equip_kwh = pse_df['MISC_EQUIP'][0]
        pse_df_equip_kw = pse_df['MISC_EQUIP'][1]

        col = rotation_labels[i]
        df[col][0] = float(pse_df_int_light_kwh)
        df[col][1] = float(pse_df_int_light_kw)
        df[col][2] = float(pse_df_ext_light_kwh)
        df[col][3] = float(pse_df_ext_light_kw)
        df[col][4] = float(pse_df_heat_kwh)
        df[col][5] = float(pse_df_heat_kw)
        df[col][6] = float(pse_df_cool_kwh)
        df[col][7] = float(pse_df_cool_kw)
        df[col][8] = float(pse_df_pumps_kwh)
        df[col][9] = float(pse_df_pumps_kw)
        df[col][10] = float(pse_df_heat_reject_kwh)
        df[col][11] = float(pse_df_heat_reject_kw)
        df[col][12] = float(pse_df_fans_kwh)
        df[col][13] = float(pse_df_fans_kw)
        df[col][16] = float(pse_df_wtr_kwh)
        df[col][17] = float(pse_df_wtr_kw)
        df[col][18] = float(pse_df_equip_kwh)
        df[col][19] = float(pse_df_equip_kw)

    cols = [
        'Baseline 0° rotation',
        'Baseline 90° rotation',
        'Baseline 180° rotation',
        'Baseline 270° rotation',
        'Proposed'
    ]
    # df = df.iloc[:, :-4]
    df = df.iloc[:, :-2]
    # df = df.iloc[:, :-3]
    df = df.drop(df.columns[1], axis=1)
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    third_col_name = df.columns[3]
    total_0_degree = df.loc[df[third_col_name] == 'Consumption (kWh)', 'Baseline 0° rotation'].sum()
    total_90_degree = df.loc[df[third_col_name] == 'Consumption (kWh)', 'Baseline 90° rotation'].sum()
    total_180_degree = df.loc[df[third_col_name] == 'Consumption (kWh)', 'Baseline 180° rotation'].sum()
    total_270_degree = df.loc[df[third_col_name] == 'Consumption (kWh)', 'Baseline 270° rotation'].sum()
    df['Baseline 0° rotation'][49] = total_0_degree
    df['Baseline 90° rotation'][49] = total_90_degree
    df['Baseline 180° rotation'][49] = total_180_degree
    df['Baseline 270° rotation'][49] = total_270_degree
    total_0_degree_therm = 0
    total_90_degree_therm = 0
    total_180_degree_therm = 0
    total_270_degree_therm = 0
    df['Baseline 0° rotation'][50] = total_0_degree_therm
    df['Baseline 90° rotation'][50] = total_90_degree_therm
    df['Baseline 180° rotation'][50] = total_180_degree_therm
    df['Baseline 270° rotation'][50] = total_270_degree_therm
    total_0_degree_mwh = 0
    total_90_degree_mwh = 0
    total_180_degree_mwh = 0
    total_270_degree_mwh = 0
    df['Baseline 0° rotation'][51] = total_0_degree_mwh
    df['Baseline 90° rotation'][51] = total_90_degree_mwh
    df['Baseline 180° rotation'][51] = total_180_degree_mwh
    df['Baseline 270° rotation'][51] = total_270_degree_mwh

    with st.expander("**🔴 Baseline Energy Summary by End Use**"):
        df = df.head(-2)
        df = df[df.iloc[:, 3].notna() & (df.iloc[:, 3] != "")]
        df_ = df
        df = df.iloc[:, :-2]
        df = df.iloc[:-4]
        st.dataframe(df)

    with st.expander("**🔴 Proposed Energy Summary by End Use**"):
        df_ = df_.iloc[:-4]
        cols_to_drop = df_.columns[-6:-1]
        df_proposed = df_.drop(columns=cols_to_drop)
        third_col_name = df_.columns[3]
        total_proposed = df_.loc[df_[third_col_name] == 'Consumption (kWh)', 'Proposed'].sum()
        st.write(df_proposed)
    
    with st.expander("**🔴 Baseline Building Annual Energy Cost by Energy Type**"):
        columns = pd.MultiIndex.from_product([
            ['Energy Type', 'Unit'],
            ['Baseline 0° rotation', 'Baseline 90° rotation', 'Baseline 180° rotation', 'Baseline 270° rotation', 'Baseline Design Total']
        ], names=['', ''])
        
        avg = (total_0_degree + total_90_degree + total_180_degree + total_270_degree)*0.085
        avg_therm = (total_0_degree_therm + total_90_degree_therm + total_180_degree_therm + total_270_degree_therm)*0.085
        avg_mwh = (total_0_degree_mwh + total_90_degree_mwh + total_180_degree_mwh + total_270_degree_mwh)*0.085
        baseline_0_sum = round((total_0_degree + total_0_degree_therm + total_0_degree_mwh)*0.085,2)
        baseline_90_sum = round((total_90_degree + total_90_degree_therm + total_90_degree_mwh)*0.085,2)
        baseline_180_sum = round((total_180_degree + total_180_degree_therm + total_180_degree_mwh)*0.085,2)
        baseline_270_sum = round((total_270_degree + total_270_degree_therm + total_270_degree_mwh)*0.085,2)
        avg_cost = round((baseline_0_sum + baseline_90_sum + baseline_180_sum + baseline_270_sum)/4,2)

        data = [
            ['Electricity', 'kWh', round(total_0_degree*0.085,2), round(total_90_degree*0.085,2), total_180_degree*0.085, total_270_degree*0.085, avg/4],
            ['Natural Gas', 'therm', round(total_0_degree_therm*0.085,2), round(total_90_degree_therm*0.085,2), total_180_degree_therm*0.085, total_270_degree_therm*0.085, avg_therm/4],
            ['District Cooling', 'MWh', round(total_0_degree_mwh*0.085,2), round(total_90_degree_mwh*0.085,2), total_180_degree_mwh*0.085, total_270_degree_mwh*0.085, avg_mwh/4],
            ['Baseline annual energy cost', '', baseline_0_sum, baseline_90_sum, baseline_180_sum, baseline_270_sum, avg_cost]
        ]

        # Create the DataFrame
        df2 = pd.DataFrame(data, columns=[
            'Energy Type', 'Unit',
            'Baseline 0° rotation', 'Baseline 90° rotation',
            'Baseline 180° rotation', 'Baseline 270° rotation',
            'Baseline Design Total'
        ])
        st.write(df2)

    with st.expander("**🔴 Performance rating Energy consumption and cost by fuel type**"):
        columns = pd.MultiIndex.from_tuples([
            ("Energy Type", ""),
            ("Site Energy Units", ""),
            ("Baseline", "Site Energy Use\n(Units shown per energy type)"),
            ("Baseline", "Source Energy Use\n(Btu x 10^6)"),
            ("Baseline", "Cost"),
            ("Proposed", "Site Energy Use\n(Units shown per energy type)"),
            ("Proposed", "Source Energy Use\n(Btu x 10^6)"),
            ("Proposed", "Cost"),
            ("Percent Savings", "Site Energy Use"),
            ("Percent Savings", "Cost")
        ])

        # Data rows
        data = [
            ["Electricity", "kWh", avg_cost, 0.0, avg_cost*0.085, total_proposed, 0.0, total_proposed*0.085, (1-total_proposed*0.085/avg_cost)*100, round((1-total_proposed*0.085/avg_cost)*100,2)],
            ["Natural Gas", "therm", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
            ["District Cooling", "MWh", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
            ["Energy model subtotal (Btu x 10^6)", "", 0.0, 0.0, "$", 0.0, 0.0, "$", 15, ""]
        ]

        df3 = pd.DataFrame(data, columns=columns)
        st.write(df3)

    with st.expander("**🔴 Virtual rate(average energy cost per unit energy)**"):
        # columns = pd.MultiIndex.from_tuples([
        #     ("Energy Type", ""),
        #     ("Unit Rate", ""),
        #     ("Baseline", ""),
        #     ("Proposed", ""),
        #     ("Percent Variance", "")
        # ])

        # # Define the data
        # data = [
        #     ["Electricity", "$ / kWh", "", "", ""],
        #     ["Natural Gas", "$ / therm", "", "", ""],
        #     ["District Cooling", "$ / MWh", "", "", ""]
        # ]

        # # Create the DataFrame
        # df4 = pd.DataFrame(data, columns=columns)
        # st.write(df4)
        st.info("This table updates automatically based on your earlier inputs.")

    
    with st.expander("**🔴Exceptional Calculation Methods**"):
        # columns = pd.MultiIndex.from_tuples([
        #     ("", "Energy Type"),
        #     ("", "Site Energy Units"),
        #     ("Baseline Energy Consumption\nwith Exceptional Calculation Methods", "Site Energy Use\n(Units shown per energy type)"),
        #     ("Baseline Energy Consumption\nwith Exceptional Calculation Methods", "Source Energy Use\n(Btu x 10^6)"),
        #     ("Baseline Energy Consumption\nwith Exceptional Calculation Methods", "Cost"),
        #     ("Proposed Energy Consumption\nwith Exceptional Calculation Methods", "Site Energy Use\n(Units shown per energy type)"),
        #     ("Proposed Energy Consumption\nwith Exceptional Calculation Methods", "Source Energy Use\n(Btu x 10^6)"),
        #     ("Proposed Energy Consumption\nwith Exceptional Calculation Methods", "Cost"),
        #     ("Percent Savings", "Site Energy Use"),
        #     ("Percent Savings", "Cost")
        # ])

        # data = [
        #     ["Electricity", "kWh", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
        #     ["Natural Gas", "therm", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
        #     ["District Cooling", "MWh", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
        #     ["Energy model subtotal (Btu x 10^6)", "", 0.0, 0.0, "$", 0.0, 0.0, "$", 15, ""]
        # ]

        # df5 = pd.DataFrame(data, columns=columns)
        # st.write(df5)
        st.info("This table updates automatically based on your earlier inputs.")
    
    with st.expander("**🔴Renewable Energy Production**"):
        # columns = pd.MultiIndex.from_tuples([
        #     ("", "Energy Type"),
        #     ("", "Site Energy Units"),
        #     ("On-Site Renewable Savings", "Site Energy Use Savings"),
        #     ("On-Site Renewable Savings", "Source Energy Use Savings\n(Btu x 10^6)"),
        #     ("On-Site Renewable Savings", "Cost Savings"),
        #     ("Proposed with On-Site Renewable Energy", "Site Energy Use (Units shown per energy type)"),
        #     ("Proposed with On-Site Renewable Energy", "Source Energy Use (Btu x 10^6)"),
        #     ("Proposed with On-Site Renewable Energy", "Cost"),
        #     ("Percent Cost Savings", "Site Energy Use"),
        #     ("Percent Cost Savings", "Cost")
        # ])

        # # Define the data
        # data = [
        #     ["Electricity", "kWh", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
        #     ["Natural Gas", "therm", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
        #     ["District Cooling", "MWh", 0.0, 0.0, "$", 0.0, 0.0, "$", 5, ""],
        #     ["Energy model subtotal (Btu x 10^6)", "", 0.0, 0.0, "$", 0.0, 0.0, "$", 15, ""]
        # ]
        # df6 = pd.DataFrame(data, columns=columns)
        # st.write(df6)
        st.info("This table updates automatically based on your earlier inputs.")

    with st.expander("**🔴Total Energy Usage**"):
        # columns = pd.MultiIndex.from_tuples([
        #     ("", "Energy Type"),
        #     ("", "Site Energy Units"),
        #     ("Baseline", "Site Energy Use (Units shown per energy type)"),
        #     ("Baseline", "Source Energy Use (Btu x 10^6)"),
        #     ("Baseline", "Cost"),
        #     ("Proposed", "Site Energy Use (Units shown per energy type)"),
        #     ("Proposed", "Source Energy Use (Btu x 10^6)"),
        #     ("Proposed", "Cost"),
        #     ("Percent Savings", "Site Energy Use"),
        #     ("Percent Savings", "Cost")
        # ])

        # df7 = pd.DataFrame(data, columns=columns)
        # st.write(df7)
        st.info("This table updates automatically based on your earlier inputs.")

    with st.expander("**🔴Unmet Loads**"):
        columns = ["Unmet Loads", "Baseline", "Proposed"]

        line1 = bepu_df['BEPU-SOURCE'][15]
        line2 = bepu_df['BEPU-SOURCE'][16]

        value1 = int(line1.split('=')[-1].strip())
        value2 = int(line2.split('=')[-1].strip())

        total_unmet = value1 + value2
        compliance = "No" if total_unmet > 300 else "Yes"

        data = [
            ["Number of hours heating loads not met", value2, value2],
            ["Number of hours cooling loads not met", value1, value1],
            ["Totals", total_unmet, total_unmet],
            ["Compliance", compliance, compliance]
        ]

        df_unmet = pd.DataFrame(data, columns=columns)
        st.write(df_unmet)