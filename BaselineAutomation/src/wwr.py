import pandas as pd
import os
import re
import streamlit as st

def UpdateWWR(sim_file, amenity_data):
    with open(sim_file, 'r', encoding='utf-8', errors='replace') as file:
        sim_data = file.readlines()

    lvd_count = [] 
    for num, line in enumerate(sim_data, 0):
        if 'LV-D' in line:
            lvd_count.append(num)
        if 'LV-E' in line:
            numend = num
    numstart = lvd_count[0] 
    lvd_rpt = sim_data[numstart:numend]
    
    lvd_str = []
    for line in lvd_rpt:
        if ('ALL WALLS' in line):
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
    lvd_summ.columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 
                        'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
    lvd_summ['WINDOW(AREA)(SQFT)'] = pd.to_numeric(lvd_summ['WINDOW(AREA)(SQFT)'])
    lvd_summ['WINDOW+WALL(AREA)(SQFT)'] = pd.to_numeric(lvd_summ['WINDOW+WALL(AREA)(SQFT)'])

    pc_wwr = (lvd_summ['WINDOW(AREA)(SQFT)'] / lvd_summ['WINDOW+WALL(AREA)(SQFT)'])
    for value in pc_wwr:
        if value > 0.4:
            height_factor = 0.4 / value

            ## Paste all_win_value in range "Floors / Spaces / Walls / Windows / Doors" and "Electric & Fuel Meters" ##
            start_marker1 = "Floors / Spaces / Walls / Windows / Doors"
            end_marker1 = "Electric & Fuel Meters"

            # Finding start and end indices
            start_index1 = None
            end_index1 = None

            for i, line in enumerate(amenity_data):
                if start_marker1 in line:
                    start_index1 = i
                if end_marker1 in line:
                    end_index1 = i
                    break

            if start_index1 is not None and end_index1 is not None:
                inside_window = False
                for line_index in range(start_index1 + 3, end_index1 - 4):
                    line = amenity_data[line_index]
                    if "WINDOW" in line:
                        inside_window = True
                    elif inside_window:
                        if ".." in line:
                            inside_window = False
                        elif "HEIGHT" in line:
                            height_str = re.search(r'HEIGHT\s*=\s*(\S+)', line)
                            if height_str:
                                existing_height = float(height_str.group(1))
                                new_height = existing_height * height_factor
                                amenity_data[line_index] = re.sub(r'(HEIGHT\s*=\s*\S+)', 'HEIGHT           = {}'.format(round(new_height, 2)), line)
        else:
            st.success("WWR is <= 0.4")
    
    return amenity_data
