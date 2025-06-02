import streamlit as st
import tempfile
import pandas as pd
from q.src import psf
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def get_lvd_Psummary(name):
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
            
            
        return lvd_summ
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame(columns=columns)

def get_lvd_Bsummary(name):
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
            
        return lvd_summ
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame(columns=columns)

def getTwoSimFiles(input_simp_path, input_simb_path):
    if input_simp_path is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(input_simp_path.getbuffer())
            sim_p_path = temp_file.name
    else:
        st.error("Error: No input for simulation P file.")
        return
    
    if input_simb_path is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(input_simb_path.getbuffer())
            sim_b_path = temp_file.name
    else:
        st.error("Error: No input for simulation B file.")
        return
        
    sim_p_path = sim_p_path.replace('\n', '\r\n')
    sim_b_path = sim_b_path.replace('\n', '\r\n')

    lvd_summary_p = get_lvd_Psummary(sim_p_path)
    lvd_summary_b = get_lvd_Bsummary(sim_b_path)
    # st.write(lvd_summary_p)
    # st.write(lvd_summary_b)

    # if st.button("Based on Metering"):
    #     prop_data = psf.get_PSF_report_Prop(sim_p_path)
    #     base_data = psf.get_PSF_report_Base(sim_b_path)
    #     if prop_data is None or base_data is None:
    #         st.error("Error: Failed to retrieve simulation data.")
    #         return
        
    #     # Handle trailing columns in LIGHTS and MISC_EQUIP
    #     if prop_data['LIGHTS'].iloc[-3] != 'TOTAL':
    #         new_row = pd.DataFrame({'LIGHTS': ['TOTAL'], 'OTHER_COLUMN': [None]})
    #         prop_data = pd.concat([prop_data.iloc[:-2], new_row, prop_data.iloc[-2:]]).reset_index(drop=True)
        
    #     if base_data['LIGHTS'].iloc[-3] != 'TOTAL':
    #         new_row = pd.DataFrame({'LIGHTS': ['TOTAL'], 'OTHER_COLUMN': [None]})
    #         base_data = pd.concat([base_data.iloc[:-2], new_row, base_data.iloc[-2:]]).reset_index(drop=True)
        
    #     prop_data['MISC_EQUIP'] = prop_data['MISC_EQUIP'].astype(str)
    #     base_data['MISC_EQUIP'] = base_data['MISC_EQUIP'].astype(str)

    #     def correct_multiple_dots(entry):
    #         parts = entry.split('.')
    #         if len(parts) > 2:
    #             return '.'.join(parts[1:])
    #         return entry

    #     prop_data['MISC_EQUIP'] = prop_data['MISC_EQUIP'].apply(correct_multiple_dots)
    #     base_data['MISC_EQUIP'] = base_data['MISC_EQUIP'].apply(correct_multiple_dots)

    #     for index, metering_name in prop_data.iloc[:, 0].items():
    #         if str(metering_name).strip() not in ['KWH', 'KW', 'NaN', 'nan', '', 'MAX KW', 'MAX KWH']:
    #             st.markdown(f"""<h6 style="color:red;">🟢 {metering_name}</h6>""", unsafe_allow_html=True)
    #             st.markdown("""<h7 style="color:green;"><b>Output PS-F</b></h7>""", unsafe_allow_html=True)

    #             elfh_propKWH, elfh_propKW = None, None
    #             elfh_baseKWH, elfh_baseKW = None, None
    #             equip_propKW, equip_propKWH = None, None
    #             equip_baseKW, equip_baseKWH = None, None
    #             fans_propKW, fans_propKWH = None, None
    #             fans_baseKW, fans_baseKWH = None, None
    #             cool_propKW, cool_propKWH = None, None
    #             cool_baseKW, cool_baseKWH = None, None
    #             heat_propKW, heat_propKWH = None, None
    #             heat_baseKW, heat_baseKWH = None, None
    #             ext_propKW, ext_propKWH = None, None
    #             ext_baseKW, ext_baseKWH = None, None
    #             domest_propKW, domest_propKWH = None, None
    #             domest_baseKW, domest_baseKWH = None, None
    #             pumps_propKW, pumps_propKWH = None, None
    #             pumps_baseKW, pumps_baseKWH = None, None
    #             refringe_propKW, refringe_propKWH = None, None
    #             refringe_baseKW, refringe_baseKWH = None, None
    #             ht_pump_propKW, ht_pump_propKWH = None, None
    #             ht_pump_baseKW, ht_pump_baseKWH = None, None
    #             total_propKW, total_propKWH = None, None
    #             total_baseKW, total_baseKWH = None, None

    #             for sub_index in range(index, len(prop_data)):
    #                 if prop_data['LIGHTS'].iloc[sub_index] == "TOTAL":
    #                     elfh_propKWH = prop_data['LIGHTS'].iloc[sub_index + 1]
    #                     elfh_propKW = prop_data['LIGHTS'].iloc[sub_index + 2]
    #                     elfh_baseKWH = base_data['LIGHTS'].iloc[sub_index + 1]
    #                     elfh_baseKW = base_data['LIGHTS'].iloc[sub_index + 2] if base_data is not None else None

    #                     equip_propKW = prop_data['MISC_EQUIP'].iloc[sub_index + 2]
    #                     equip_propKWH = prop_data['MISC_EQUIP'].iloc[sub_index + 1]
    #                     equip_baseKW = base_data['MISC_EQUIP'].iloc[sub_index + 2]
    #                     equip_baseKWH = base_data['MISC_EQUIP'].iloc[sub_index + 1] if base_data is not None else None

    #                     fans_propKW = prop_data['VENT FANS'].iloc[sub_index + 2]
    #                     fans_propKWH = prop_data['VENT FANS'].iloc[sub_index + 1]
    #                     fans_baseKW = base_data['VENT FANS'].iloc[sub_index + 2]
    #                     fans_baseKWH = base_data['VENT FANS'].iloc[sub_index + 1] if base_data is not None else None

    #                     cool_propKW = prop_data['SPACE_COOLING'].iloc[sub_index + 2]
    #                     cool_propKWH = prop_data['SPACE_COOLING'].iloc[sub_index + 1]
    #                     cool_baseKW = base_data['SPACE_COOLING'].iloc[sub_index + 2]
    #                     cool_baseKWH = base_data['SPACE_COOLING'].iloc[sub_index + 1] if base_data is not None else None

    #                     heat_propKW = prop_data['HEAT_REJECT'].iloc[sub_index + 2]
    #                     heat_propKWH = prop_data['HEAT_REJECT'].iloc[sub_index + 1]
    #                     heat_baseKW = base_data['HEAT_REJECT'].iloc[sub_index + 2]
    #                     heat_baseKWH = base_data['HEAT_REJECT'].iloc[sub_index + 1] if base_data is not None else None

    #                     ext_propKW = prop_data['EXT USAGE'].iloc[sub_index + 2]
    #                     ext_propKWH = prop_data['EXT USAGE'].iloc[sub_index + 1]
    #                     ext_baseKW = base_data['EXT USAGE'].iloc[sub_index + 2]
    #                     ext_baseKWH = base_data['EXT USAGE'].iloc[sub_index + 1] if base_data is not None else None

    #                     domest_propKW = prop_data['DOMEST HOT WTR'].iloc[sub_index + 2]
    #                     domest_propKWH = prop_data['DOMEST HOT WTR'].iloc[sub_index + 1]
    #                     domest_baseKW = base_data['DOMEST HOT WTR'].iloc[sub_index + 2]
    #                     domest_baseKWH = base_data['DOMEST HOT WTR'].iloc[sub_index + 1] if base_data is not None else None

    #                     pumps_propKW = prop_data['PUMPS & AUX'].iloc[sub_index + 2]
    #                     pumps_propKWH = prop_data['PUMPS & AUX'].iloc[sub_index + 1]
    #                     pumps_baseKW = base_data['PUMPS & AUX'].iloc[sub_index + 2]
    #                     pumps_baseKWH = base_data['PUMPS & AUX'].iloc[sub_index + 1] if base_data is not None else None

    #                     refringe_propKW = prop_data['REFRIG DISPLAY'].iloc[sub_index + 2]
    #                     refringe_propKWH = prop_data['REFRIG DISPLAY'].iloc[sub_index + 1]
    #                     refringe_baseKW = base_data['REFRIG DISPLAY'].iloc[sub_index + 2]
    #                     refringe_baseKWH = base_data['REFRIG DISPLAY'].iloc[sub_index + 1] if base_data is not None else None

    #                     ht_pump_propKW = prop_data['HT PUMP SUPPLEM'].iloc[sub_index + 2]
    #                     ht_pump_propKWH = prop_data['HT PUMP SUPPLEM'].iloc[sub_index + 1]
    #                     ht_pump_baseKW = base_data['HT PUMP SUPPLEM'].iloc[sub_index + 2]
    #                     ht_pump_baseKWH = base_data['HT PUMP SUPPLEM'].iloc[sub_index + 1] if base_data is not None else None

    #                     total_propKW = prop_data['TOTAL'].iloc[sub_index + 2]
    #                     total_propKWH = prop_data['TOTAL'].iloc[sub_index + 1]
    #                     total_baseKW = base_data['TOTAL'].iloc[sub_index + 2]
    #                     total_baseKWH = base_data['TOTAL'].iloc[sub_index + 1] if base_data is not None else None

    #                     if elfh_propKWH in ['NaN', 'nan', '', 'KWH']:
    #                         elfh_propKWH = prop_data['TASK_LIGHTS'].iloc[sub_index + 1]
    #                         equip_propKWH = prop_data['MISC_EQUIP'].iloc[sub_index + 1]
    #                         fans_propKWH = prop_data['VENT FANS'].iloc[sub_index + 1]
    #                         cool_propKWH = prop_data['SPACE_COOLING'].iloc[sub_index + 1]
    #                         heat_propKWH = prop_data['HEAT_REJECT'].iloc[sub_index + 1]
    #                         ext_propKWH = prop_data['EXT USAGE'].iloc[sub_index + 1]
    #                         domest_propKWH = prop_data['DOMEST HOT WTR'].iloc[sub_index + 1]
    #                         pumps_propKWH = prop_data['PUMPS & AUX'].iloc[sub_index + 1]
    #                         refringe_propKWH = prop_data['REFRIG DISPLAY'].iloc[sub_index + 1]
    #                         ht_pump_propKWH = prop_data['HT PUMP SUPPLEM'].iloc[sub_index + 1]
    #                         total_propKWH = prop_data['TOTAL'].iloc[sub_index + 1]

    #                     if elfh_baseKWH in ['NaN', 'nan', '', 'KWH']:
    #                         elfh_baseKWH = base_data['TASK_LIGHTS'].iloc[sub_index + 1] if base_data is not None else None
    #                         equip_baseKWH = base_data['MISC_EQUIP'].iloc[sub_index + 1] if base_data is not None else None
    #                         fans_baseKWH = base_data['VENT FANS'].iloc[sub_index + 1] if base_data is not None else None
    #                         cool_baseKWH = base_data['SPACE_COOLING'].iloc[sub_index + 1] if base_data is not None else None
    #                         heat_baseKWH = base_data['HEAT_REJECT'].iloc[sub_index + 1] if base_data is not None else None
    #                         ext_baseKWH = base_data['EXT USAGE'].iloc[sub_index + 1] if base_data is not None else None
    #                         domest_baseKWH = base_data['DOMEST HOT WTR'].iloc[sub_index + 1] if base_data is not None else None
    #                         pumps_baseKWH = base_data['PUMPS & AUX'].iloc[sub_index + 1] if base_data is not None else None
    #                         refringe_baseKWH = base_data['REFRIG DISPLAY'].iloc[sub_index + 1] if base_data is not None else None
    #                         ht_pump_baseKWH = base_data['HT PUMP SUPPLEM'].iloc[sub_index + 1] if base_data is not None else None
    #                         total_baseKWH = base_data['TOTAL'].iloc[sub_index + 1] if base_data is not None else None

    #                     # Convert to numeric and round to 1 decimal place
    #                     elfh_propKW = pd.to_numeric(elfh_propKW, errors='coerce').round(1)
    #                     elfh_propKWH = pd.to_numeric(elfh_propKWH, errors='coerce').round(1)
    #                     elfh_baseKW = pd.to_numeric(elfh_baseKW, errors='coerce').round(1)
    #                     elfh_baseKWH = pd.to_numeric(elfh_baseKWH, errors='coerce').round(1)
    #                     equip_propKW = pd.to_numeric(equip_propKW, errors='coerce').round(1)
    #                     equip_propKWH = pd.to_numeric(equip_propKWH, errors='coerce').round(1)
    #                     equip_baseKW = pd.to_numeric(equip_baseKW, errors='coerce').round(1)
    #                     equip_baseKWH = pd.to_numeric(equip_baseKWH, errors='coerce').round(1)
    #                     fans_propKW = pd.to_numeric(fans_propKW, errors='coerce').round(1)
    #                     fans_propKWH = pd.to_numeric(fans_propKWH, errors='coerce').round(1)
    #                     fans_baseKW = pd.to_numeric(fans_baseKW, errors='coerce').round(1)
    #                     fans_baseKWH = pd.to_numeric(fans_baseKWH, errors='coerce').round(1)
    #                     cool_propKW = pd.to_numeric(cool_propKW, errors='coerce').round(1)
    #                     cool_propKWH = pd.to_numeric(cool_propKWH, errors='coerce').round(1)
    #                     cool_baseKW = pd.to_numeric(cool_baseKW, errors='coerce').round(1)
    #                     cool_baseKWH = pd.to_numeric(cool_baseKWH, errors='coerce').round(1)
    #                     heat_propKW = pd.to_numeric(heat_propKW, errors='coerce').round(1)
    #                     heat_propKWH = pd.to_numeric(heat_propKWH, errors='coerce').round(1)
    #                     heat_baseKW = pd.to_numeric(heat_baseKW, errors='coerce').round(1)
    #                     heat_baseKWH = pd.to_numeric(heat_baseKWH, errors='coerce').round(1)
    #                     ext_propKW = pd.to_numeric(ext_propKW, errors='coerce').round(1)
    #                     ext_propKWH = pd.to_numeric(ext_propKWH, errors='coerce').round(1)
    #                     ext_baseKW = pd.to_numeric(ext_baseKW, errors='coerce').round(1)
    #                     ext_baseKWH = pd.to_numeric(ext_baseKWH, errors='coerce').round(1)
    #                     domest_propKW = pd.to_numeric(domest_propKW, errors='coerce').round(1)
    #                     domest_propKWH = pd.to_numeric(domest_propKWH, errors='coerce').round(1)
    #                     domest_baseKW = pd.to_numeric(domest_baseKW, errors='coerce').round(1)
    #                     domest_baseKWH = pd.to_numeric(domest_baseKWH, errors='coerce').round(1)
    #                     pumps_propKW = pd.to_numeric(pumps_propKW, errors='coerce').round(1)
    #                     pumps_propKWH = pd.to_numeric(pumps_propKWH, errors='coerce').round(1)
    #                     pumps_baseKW = pd.to_numeric(pumps_baseKW, errors='coerce').round(1)
    #                     pumps_baseKWH = pd.to_numeric(pumps_baseKWH, errors='coerce').round(1)
    #                     refringe_propKW = pd.to_numeric(refringe_propKW, errors='coerce').round(1)
    #                     refringe_propKWH = pd.to_numeric(refringe_propKWH, errors='coerce').round(1)
    #                     refringe_baseKW = pd.to_numeric(refringe_baseKW, errors='coerce').round(1)
    #                     refringe_baseKWH = pd.to_numeric(refringe_baseKWH, errors='coerce').round(1)
    #                     ht_pump_propKW = pd.to_numeric(ht_pump_propKW, errors='coerce').round(1)
    #                     ht_pump_propKWH = pd.to_numeric(ht_pump_propKWH, errors='coerce').round(1)
    #                     ht_pump_baseKW = pd.to_numeric(ht_pump_baseKW, errors='coerce').round(1)
    #                     ht_pump_baseKWH = pd.to_numeric(ht_pump_baseKWH, errors='coerce').round(1)
    #                     total_propKW = pd.to_numeric(total_propKW, errors='coerce').round(1)
    #                     total_propKWH = pd.to_numeric(total_propKWH, errors='coerce').round(1)
    #                     total_baseKW = pd.to_numeric(total_baseKW, errors='coerce').round(1)
    #                     total_baseKWH = pd.to_numeric(total_baseKWH, errors='coerce').round(1)

    #                     # LIGHTS
    #                     if elfh_propKWH == elfh_propKW and elfh_propKW != 0:
    #                         elfh_prop = 1
    #                     elif elfh_propKWH == elfh_propKW and elfh_propKW == 0:
    #                         elfh_prop = 0
    #                     else:
    #                         elfh_prop = round((elfh_propKWH / elfh_propKW), 1)

    #                     if elfh_baseKWH == elfh_baseKW and elfh_baseKW != 0:
    #                         elfh_base = 1
    #                     elif elfh_baseKWH == elfh_baseKW and elfh_baseKW == 0:
    #                         elfh_base = 0
    #                     else:
    #                         elfh_base = round((elfh_baseKWH / elfh_baseKW), 1)
                        
    #                     # EQUIPMENT
    #                     if equip_propKWH == equip_propKW and equip_propKW != 0:
    #                         equip_prop = 1
    #                     elif equip_propKWH == equip_propKW and equip_propKW == 0:
    #                         equip_prop = 0
    #                     else:
    #                         equip_prop = round((equip_propKWH / equip_propKW), 1)

    #                     if equip_baseKWH == equip_baseKW and equip_baseKW != 0:
    #                         equip_base = 1
    #                     elif equip_baseKWH == equip_baseKW and equip_baseKW == 0:
    #                         equip_base = 0
    #                     else:
    #                         equip_base = round((equip_baseKWH / equip_baseKW), 1)

    #                     # FANS
    #                     if fans_propKWH == fans_propKW and fans_propKW != 0:
    #                         fans_prop = 1
    #                     elif fans_propKWH == fans_propKW and fans_propKW == 0:
    #                         fans_prop = 0
    #                     else:
    #                         fans_prop = round((fans_propKWH / fans_propKW), 1)
                        
    #                     if fans_baseKWH == fans_baseKW and fans_baseKW != 0:
    #                         fans_base = 1
    #                     elif fans_baseKWH == fans_baseKW and fans_baseKW == 0:
    #                         fans_base = 0
    #                     else:
    #                         fans_base = round((fans_baseKWH / fans_baseKW), 1)

    #                     # COOLING
    #                     if cool_propKWH == cool_propKW and cool_propKW != 0:
    #                         cool_prop = 1
    #                     elif cool_propKWH == cool_propKW and cool_propKW == 0:
    #                         cool_prop = 0
    #                     else:
    #                         cool_prop = round((cool_propKWH / cool_propKW), 1)
                        
    #                     if cool_baseKWH == cool_baseKW and cool_baseKW != 0:
    #                         cool_base = 1
    #                     elif cool_baseKWH == cool_baseKW and cool_baseKW == 0:
    #                         cool_base = 0
    #                     else:
    #                         cool_base = round((cool_baseKWH / cool_baseKW), 1)

    #                     # HEATING
    #                     if heat_propKWH == heat_propKW and heat_propKW != 0:
    #                         heat_prop = 1
    #                     elif heat_propKWH == heat_propKW and heat_propKW == 0:
    #                         heat_prop = 0
    #                     else:
    #                         heat_prop = round((heat_propKWH / heat_propKW), 1)

    #                     if heat_baseKWH == heat_baseKW and heat_baseKW != 0:
    #                         heat_base = 1
    #                     elif heat_baseKWH == heat_baseKW and heat_baseKW == 0:
    #                         heat_base = 0
    #                     else:
    #                         heat_base = round((heat_baseKWH / heat_baseKW), 1)
                        
    #                     # EXTERNAL
    #                     if ext_propKWH == ext_propKW and ext_propKW != 0:
    #                         ext_prop = 1
    #                     elif ext_propKWH == ext_propKW and ext_propKW == 0:
    #                         ext_prop = 0
    #                     else:
    #                         ext_prop = round((ext_propKWH / ext_propKW), 1)
                        
    #                     if ext_baseKWH == ext_baseKW and ext_baseKW != 0:
    #                         ext_base = 1
    #                     elif ext_baseKWH == ext_baseKW and ext_baseKW == 0:
    #                         ext_base = 0
    #                     else:
    #                         ext_base = round((ext_baseKWH / ext_baseKW), 1)
                        
    #                     # DOMESTIC
    #                     if domest_propKWH == domest_propKW and domest_propKW != 0:
    #                         domest_prop = 1
    #                     elif domest_propKWH == domest_propKW and domest_propKW == 0:
    #                         domest_prop = 0
    #                     else:
    #                         domest_prop = round((domest_propKWH / domest_propKW), 1)
                        
    #                     if domest_baseKWH == domest_baseKW and domest_baseKW != 0:
    #                         domest_base = 1
    #                     elif domest_baseKWH == domest_baseKW and domest_baseKW == 0:
    #                         domest_base = 0
    #                     else:
    #                         domest_base = round((domest_baseKWH / domest_baseKW), 1)

    #                     # PUMPS
    #                     if pumps_baseKWH == pumps_baseKW and pumps_baseKW != 0:
    #                         pumps_base = 1
    #                     elif pumps_baseKWH == pumps_baseKW and pumps_baseKW == 0:
    #                         pumps_base = 0
    #                     else:
    #                         pumps_base = round((pumps_baseKWH / pumps_baseKW), 1)
                        
    #                     if pumps_propKWH == pumps_propKW and pumps_propKW != 0:
    #                         pumps_prop = 1
    #                     elif pumps_propKWH == pumps_propKW and pumps_propKW == 0:
    #                         pumps_prop = 0
    #                     else:
    #                         pumps_prop = round((pumps_propKWH / pumps_propKW), 1)

    #                     # REFRIGERATION
    #                     if refringe_baseKWH == refringe_baseKW and refringe_baseKW != 0:
    #                         refringe_base = 1
    #                     elif refringe_baseKWH == refringe_baseKW and refringe_baseKW == 0:
    #                         refringe_base = 0
    #                     else:
    #                         refringe_base = round((refringe_baseKWH / refringe_baseKWH), 1)

    #                     if refringe_propKWH == refringe_propKW and refringe_propKW != 0:
    #                         refringe_prop = 1
    #                     elif refringe_propKWH == refringe_propKW and refringe_propKW == 0:
    #                         refringe_prop = 0
    #                     else:
    #                         refringe_prop = round((refringe_propKWH / refringe_propKWH), 1)

    #                     # HT_PUMP
    #                     if ht_pump_baseKWH == ht_pump_baseKW and ht_pump_baseKW != 0:
    #                         ht_pump_base = 1
    #                     elif ht_pump_baseKWH == ht_pump_baseKW and ht_pump_baseKW == 0:
    #                         ht_pump_base = 0
    #                     else:
    #                         ht_pump_base = round((ht_pump_baseKWH / ht_pump_baseKW), 1)

    #                     if ht_pump_propKWH == ht_pump_propKW and ht_pump_propKW != 0:
    #                         ht_pump_prop = 1
    #                     elif ht_pump_propKWH == ht_pump_propKW and ht_pump_propKW == 0:
    #                         ht_pump_prop = 0
    #                     else:
    #                         ht_pump_prop = round((ht_pump_propKWH / ht_pump_propKW), 1)

    #                     # TOTAL
    #                     if total_baseKWH == total_baseKW and total_baseKW != 0:
    #                         total_base = 1
    #                     elif total_baseKWH == total_baseKW and total_baseKW == 0:
    #                         total_base = 0
    #                     else:
    #                         total_base = round((total_baseKWH / total_baseKW), 1)
                        
    #                     if total_propKWH == total_propKW and total_propKW != 0:
    #                         total_prop = 1
    #                     elif total_propKWH == total_propKW and total_propKW == 0:
    #                         total_prop = 0
    #                     else:
    #                         total_prop = round((total_propKWH / total_propKW), 1)


    #                     ratio1 = 0 if elfh_baseKWH == elfh_propKWH and elfh_baseKWH == 0 else round((elfh_propKWH / elfh_baseKWH), 1)
    #                     ratio2 = 0 if elfh_baseKW == elfh_propKW  and elfh_baseKW == 0 else round((elfh_propKW / elfh_baseKW), 1)
    #                     ratio3 = 0 if equip_baseKWH == equip_propKWH and equip_baseKWH == 0  else round((equip_propKWH / equip_baseKWH), 1)
    #                     ratio4 = 0 if equip_baseKW == equip_propKW and equip_baseKW == 0  else round((equip_propKW / equip_baseKW), 1)
    #                     ratio5 = 0 if fans_baseKWH == fans_propKWH and fans_baseKWH == 0  else round((fans_propKWH / fans_baseKWH), 1)
    #                     ratio6 = 0 if fans_baseKW == fans_propKW and fans_baseKW == 0  else round((fans_propKW / fans_baseKW), 1)
    #                     ratio7 = 0 if cool_baseKWH == cool_propKWH and cool_baseKWH == 0  else round((cool_propKWH / cool_baseKWH), 1)
    #                     ratio8 = 0 if cool_baseKW == cool_propKW and cool_baseKW == 0  else round((cool_propKW / cool_baseKW), 1)
    #                     ratio9 = 0 if heat_baseKWH == heat_propKWH and heat_baseKWH == 0  else round((heat_propKWH / heat_baseKWH), 1)
    #                     ratio10 = 0 if heat_baseKW == heat_propKW and heat_baseKW == 0  else round((heat_propKW / heat_baseKW), 1)
    #                     ratio11 = 0 if ext_baseKWH == ext_propKWH and ext_baseKWH == 0  else round((ext_propKWH / ext_baseKWH), 1)
    #                     ratio12 = 0 if ext_baseKW == ext_propKW and ext_baseKW == 0  else round((ext_propKW / ext_baseKW), 1)
    #                     ratio13 = 0 if domest_baseKWH == domest_propKWH and domest_baseKWH == 0  else round((domest_propKWH / domest_baseKWH), 1)
    #                     ratio14 = 0 if domest_baseKW == domest_propKW and domest_baseKW == 0  else round((domest_propKW / domest_baseKW), 1)
    #                     ratio15 = 0 if pumps_baseKWH == pumps_propKWH and pumps_baseKWH == 0  else round((pumps_propKWH / pumps_baseKWH), 1)
    #                     ratio16 = 0 if pumps_baseKW == pumps_propKW and pumps_baseKW == 0  else round((pumps_propKW / pumps_baseKW), 1)
    #                     ratio17 = 0 if refringe_baseKWH == refringe_propKWH and refringe_baseKWH == 0  else round((refringe_propKWH / refringe_baseKWH), 1)
    #                     ratio18 = 0 if refringe_baseKW == refringe_propKW and refringe_baseKW == 0  else round((refringe_propKW / refringe_baseKW), 1)
    #                     ratio19 = 0 if ht_pump_baseKWH == ht_pump_propKWH and ht_pump_baseKWH == 0  else round((ht_pump_propKWH / ht_pump_baseKWH), 1)
    #                     ratio20 = 0 if ht_pump_baseKW == ht_pump_propKW and ht_pump_baseKW == 0  else round((ht_pump_propKW / ht_pump_baseKW), 1)
    #                     ratio21 = 0 if total_baseKWH == total_propKWH and total_baseKWH == 0  else round((total_propKWH / total_baseKWH), 1)
    #                     ratio22 = 0 if total_baseKW == total_propKW and total_baseKW == 0  else round((total_propKW / total_baseKW), 1)

    #                     data_ps_f = {
    #                         'Item': ['Light', 'Light', 'Equipment', 'Equipment', 'Vent Fans', 'Vent Fans', 'Space Cooling', 'Space Cooling', 'Heat Reject', 'Heat Reject', 'External Usage', 'External Usage', 'Domest Hot Air', 'Domest Hot Air', 'Pumps & AUX', 'Pumps & AUX', 'Refrig Display', 'Refrig Display', 'Ht Pump Suppl', 'Ht Pump Suppl', 'Total', 'Total'],
    #                         'Unit': ['kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW', 'kWh', 'kW'],
    #                         'Baseline': [elfh_baseKWH, elfh_baseKW, equip_baseKWH, equip_baseKW, fans_baseKWH, fans_baseKW, cool_baseKWH, cool_baseKW, heat_baseKWH, heat_baseKW, ext_baseKWH, ext_baseKW, domest_baseKWH, domest_baseKW, pumps_baseKWH, pumps_baseKW, refringe_baseKWH, refringe_baseKW, ht_pump_baseKWH, ht_pump_baseKW, total_baseKWH, total_baseKW],
    #                         'Proposed': [elfh_propKWH, elfh_propKW, equip_propKWH, equip_propKW, fans_propKWH, fans_propKW, cool_propKWH, cool_propKW, heat_propKWH, heat_propKW, ext_propKWH, ext_propKW, domest_propKWH, domest_propKW, pumps_propKWH, pumps_propKW, refringe_propKWH, refringe_propKW, ht_pump_propKWH, ht_pump_propKW, total_propKWH, total_propKW],
    #                         'Savings(in %)': [(1 - ratio1), (1 - ratio2), (1 - ratio3), (1 - ratio4), (1 - ratio5), (1 - ratio6), (1 - ratio7), (1 - ratio8), (1 - ratio9), (1 - ratio10), (1 - ratio11), (1 - ratio12), (1 - ratio13), (1 - ratio14), (1 - ratio15), (1 - ratio16), (1 - ratio17), (1 - ratio18), (1 - ratio19), (1 - ratio20), (1 - ratio21), (1 - ratio22)],
    #                     }

    #                     data_elfh = {
    #                         'Item': ['Light', 'Equipment', 'Vent Fans', 'Space Cooling', 'Heat Reject', 'External Usage', 'Domest Hot Air', 'Pumps & AUX', 'Refrig Display', 'Ht Pump Suppl', 'Total'],
    #                         'Baseline(kWh/kW)': [elfh_base, equip_base, fans_base, cool_base, heat_base, ext_base, domest_base, pumps_base, refringe_base, ht_pump_base, total_base],
    #                         'Proposed(kWh/kW)': [elfh_prop, equip_prop, fans_prop, cool_prop, heat_prop, ext_prop, domest_prop, pumps_prop, refringe_prop, ht_pump_prop, total_prop],
    #                     }

    #                     # Create DataFrames
    #                     df_ps_f = pd.DataFrame(data_ps_f)
    #                     df_elfh = pd.DataFrame(data_elfh)

    #                     # Create a function to build the HTML table with merged cells
    #                     def create_html_table(df):
    #                         html = '<table border="1" style="border-collapse: collapse; width: 100%;">'
    #                         html += '<tr>'
    #                         for col in df.columns:
    #                             html += f'<th>{col}</th>'
    #                         html += '</tr>'

    #                         previous_item = None
    #                         for i, row in df.iterrows():
    #                             html += '<tr>'
    #                             if row['Item'] != previous_item:
    #                                 rowspan = df['Item'].value_counts()[row['Item']]
    #                                 html += f'<td rowspan="{rowspan}">{row["Item"]}</td>'
    #                                 previous_item = row['Item']
    #                             html += f'<td>{row["Unit"]}</td>'
    #                             html += f'<td>{row["Baseline"]}</td>'
    #                             html += f'<td>{row["Proposed"]}</td>'
    #                             html += f'<td>{row["Savings(in %)"]:.1%}</td>'
    #                             html += '</tr>'

    #                         html += '</table>'
    #                         return html

    #                     # Generate the HTML table
    #                     df_ps_f = create_html_table(df_ps_f)
    #                     st.markdown(df_ps_f, unsafe_allow_html=True)
                        
    #                     st.markdown("""<h7 style="color:green;"><b>EFLH table</b></h7>""", unsafe_allow_html=True)
    #                     st.table(df_elfh.style.format({
    #                         'Baseline(kWh/kW)': '{:.1f}',
    #                         'Proposed(kWh/kW)': '{:.1f}'
    #                     }))
    #                     break
                        
        # return 0
    
    if st.button("View Report"):
        prop_data = psf.get_PSF_report_Prop_all(sim_p_path)
        base_data = psf.get_PSF_report_Base_all(sim_b_path)

        # Add new column at start of dataframe named Filename in prop_data and base_data
        prop_data['Filename'] = "Proposed"
        base_data['Filename'] = "Baseline"
        cols1 = list(prop_data.columns)
        cols2 = list(base_data.columns)
        prop_data = prop_data[[cols1[-1]] + cols1[:-1]]
        base_data = base_data[[cols2[-1]] + cols2[:-1]]
        # st.write(prop_data)
        
        # Concatenate prop_data and base_data vertically
        data = pd.concat([prop_data, base_data], axis=0, ignore_index=True)
        data = data.reset_index(drop=True)

        # if KWH or MAX KW or THERM or MAX THERM/HR or MBTU or MAX MBTU/HR is in LIGHTS column then put that in corresponding UNIT column in data dataframe
        for i in range(len(data)):
            if data['LIGHTS'][i] == 'KWH':
                data['UNIT'][i] = 'KWH'
            elif data['LIGHTS'][i] == 'MAX KW':
                data['UNIT'][i] = 'MAX KW'
            elif data['LIGHTS'][i] == 'THERM':
                data['UNIT'][i] = 'THERM'
            elif data['LIGHTS'][i] == 'MAX THERM/HR':
                data['UNIT'][i] = 'MAX THERM/HR'
            elif data['LIGHTS'][i] == 'MBTU':
                data['UNIT'][i] = 'MBTU'
            elif data['LIGHTS'][i] == 'MAX MBTU/HR':
                data['UNIT'][i] = 'MAX MBTU/HR'
            elif data['TASK LIGHTS'][i] == 'KWH':
                data['UNIT'][i] = 'KWH'
            elif data['TASK LIGHTS'][i] == 'MAX KWH':
                data['UNIT'][i] = 'MAX KWH'
            elif data['TASK LIGHTS'][i] == 'THERM':
                data['UNIT'][i] = 'THERM'
            elif data['TASK LIGHTS'][i] == 'MAX THERM/HR':
                data['UNIT'][i] = 'MAX THERM/HR'
            elif data['TASK LIGHTS'][i] == 'MBTU':
                data['UNIT'][i] = 'MBTU'
            elif data['TASK LIGHTS'][i] == 'MAX MBTU/HR':
                data['UNIT'][i] = 'MAX MBTU/HR'
            elif data['MISC EQUIP'][i] == 'KWH':
                data['UNIT'][i] = 'KWH'
            elif data['MISC EQUIP'][i] == 'MAX KW':
                data['UNIT'][i] = 'MAX KW'
            elif data['MISC EQUIP'][i] == 'THERM':
                data['UNIT'][i] = 'THERM'
            elif data['MISC EQUIP'][i] == 'MAX THERM/HR':
                data['UNIT'][i] = 'MAX THERM/HR'
            elif data['MISC EQUIP'][i] == 'MBTU':
                data['UNIT'][i] = 'MBTU'
            elif data['MISC EQUIP'][i] == 'MAX MBTU/HR':
                data['UNIT'][i] = 'MAX MBTU/HR'
            elif data['SPACE EQUIP'][i] == 'KWH':
                data['UNIT'][i] = 'KWH'
            elif data['SPACE EQUIP'][i] == 'MAX KW':
                data['UNIT'][i] = 'MAX KW'
            elif data['SPACE EQUIP'][i] == 'THERM':
                data['UNIT'][i] = 'THERM'
            elif data['SPACE EQUIP'][i] == 'MAX THERM/HR':
                data['UNIT'][i] = 'MAX THERM/HR'
            elif data['SPACE EQUIP'][i] == 'MBTU':
                data['UNIT'][i] = 'MBTU'
            elif data['SPACE EQUIP'][i] == 'MAX MBTU/HR':
                data['UNIT'][i] = 'MAX MBTU/HR'
            elif data['SPACE COOLING'][i] == 'KWH':
                data['UNIT'][i] = 'KWH'
            elif data['SPACE COOLING'][i] == 'MAX KW':
                data['UNIT'][i] = 'MAX KW'
            elif data['SPACE COOLING'][i] == 'THERM':
                data['UNIT'][i] = 'THERM'
            elif data['SPACE COOLING'][i] == 'MAX THERM/HR':
                data['UNIT'][i] = 'MAX THERM/HR'
            elif data['SPACE COOLING'][i] == 'MBTU':
                data['UNIT'][i] = 'MBTU'
            elif data['SPACE COOLING'][i] == 'MAX MBTU/HR':
                data['UNIT'][i] = 'MAX MBTU/HR'
            elif data['HEAT REJECT'][i] == 'KWH':
                data['UNIT'][i] = 'KWH'
            elif data['HEAT REJECT'][i] == 'MAX KW':
                data['UNIT'][i] = 'MAX KW'
            elif data['HEAT REJECT'][i] == 'THERM':
                data['UNIT'][i] = 'THERM'
            elif data['HEAT REJECT'][i] == 'MAX THERM/HR':
                data['UNIT'][i] = 'MAX THERM/HR'
            elif data['HEAT REJECT'][i] == 'MBTU':
                data['UNIT'][i] = 'MBTU'
            elif data['HEAT REJECT'][i] == 'MAX MBTU/HR':
                data['UNIT'][i] = 'MAX MBTU/HR'
            
        # from data dataframe select only rows with 'kWh' or 'kW' in UNIT column
        data_kwh = data[
            data['UNIT'].str.contains('KWH|MAX KW', regex=True) | 
            data['LIGHTS'].str.contains('KWH|MAX KW', regex=True) | 
            data['TASK LIGHTS'].str.contains('KWH|MAX KW', regex=True) | 
            data['MISC EQUIP'].str.contains('KWH|MAX KW', regex=True) | 
            data['SPACE EQUIP'].str.contains('KWH|MAX KW', regex=True) | 
            data['SPACE COOLING'].str.contains('KWH|MAX KW', regex=True) |
            data['HEAT REJECT'].str.contains('KWH|MAX KW', regex=True)
        ]
        data_kwh = data_kwh.reset_index(drop=True)
        
        # from data dataframe select only rows with 'THERM' or 'MAX THERM/HR' in UNIT column
        data_therm = data[
            data['UNIT'].str.contains('THERM|MAX THERM/HR', regex=True) | 
            data['LIGHTS'].str.contains('THERM|MAX THERM/HR', regex=True) |
            data['TASK LIGHTS'].str.contains('THERM|MAX THERM/HR', regex=True) |
            data['MISC EQUIP'].str.contains('THERM|MAX THERM/HR', regex=True) |
            data['SPACE EQUIP'].str.contains('THERM|MAX THERM/HR', regex=True) |
            data['SPACE COOLING'].str.contains('THERM|MAX THERM/HR', regex=True) |
            data['HEAT REJECT'].str.contains('THERM|MAX THERM/HR', regex=True)
        ]
        data_therm = data_therm.reset_index(drop=True)

        # st.markdown(f"""<h6 style="color:blue;">🔵 MBTU & MAX MBTU/HR</h6>""", unsafe_allow_html=True)
        # from data dataframe select only rows with 'MBTU' or 'MAX MBTU/HR' in UNIT column
        data_mbtu = data[
            data['UNIT'].str.contains('MBTU|MAX MBTU/HR', regex=True) |
            data['LIGHTS'].str.contains('MBTU|MAX MBTU/HR', regex=True) |
            data['TASK LIGHTS'].str.contains('MBTU|MAX MBTU/HR', regex=True) |
            data['MISC EQUIP'].str.contains('MBTU|MAX MBTU/HR', regex=True) |
            data['SPACE EQUIP'].str.contains('MBTU|MAX MBTU/HR', regex=True) |
            data['SPACE COOLING'].str.contains('MBTU|MAX MBTU/HR', regex=True) |
            data['HEAT REJECT'].str.contains('MBTU|MAX MBTU/HR', regex=True)
        ]
        data_mbtu = data_mbtu.reset_index(drop=True)
        
        # converting to numeric type and removing comma from data
        data_kwh['LIGHTS'] = pd.to_numeric(data_kwh['LIGHTS'].str.replace(',',''), errors='coerce')
        data_kwh['TASK LIGHTS'] = pd.to_numeric(data_kwh['TASK LIGHTS'].str.replace(',',''), errors='coerce')
        data_kwh['MISC EQUIP'] = pd.to_numeric(data_kwh['MISC EQUIP'].str.replace(',',''), errors='coerce')
        data_kwh['SPACE EQUIP'] = pd.to_numeric(data_kwh['SPACE EQUIP'].str.replace(',',''), errors='coerce')
        data_kwh['SPACE COOLING'] = pd.to_numeric(data_kwh['SPACE COOLING'].str.replace(',',''), errors='coerce')
        data_kwh['HEAT REJECT'] = pd.to_numeric(data_kwh['HEAT REJECT'].str.replace(',',''), errors='coerce')
        data_kwh['PUMPS & AUX'] = pd.to_numeric(data_kwh['PUMPS & AUX'].str.replace(',',''), errors='coerce')
        data_kwh['VENT FANS'] = pd.to_numeric(data_kwh['VENT FANS'].str.replace(',',''), errors='coerce')
        data_kwh['REFRIG DISPLAY'] = pd.to_numeric(data_kwh['REFRIG DISPLAY'].str.replace(',',''), errors='coerce')
        data_kwh['HT PUMP SUPPLEM'] = pd.to_numeric(data_kwh['HT PUMP SUPPLEM'].str.replace(',',''), errors='coerce')
        data_kwh['DOMEST HOT WTR'] = pd.to_numeric(data_kwh['DOMEST HOT WTR'].str.replace(',',''), errors='coerce')
        data_kwh['EXT USAGE'] = pd.to_numeric(data_kwh['EXT USAGE'].str.replace(',',''), errors='coerce')
        data_kwh['TOTAL'] = pd.to_numeric(data_kwh['TOTAL'].str.replace(',',''), errors='coerce')
        # form new dataframe with sum KWH in 1 row and sum MAX KW in 1 row means based on same UNIT column values add into 1 row
        data_kwh_sum = data_kwh.groupby(['UNIT', 'Filename']).sum().reset_index()

        if not data_kwh_sum.empty:
            new_row_3rd = {
                'UNIT': ['Energy Savings'],
                'Filename': [''],
                'Meterings': [''],
            }

            columns = [
                'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING', 
                'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY', 
                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
            ]

            for col in columns:
                value1 = data_kwh_sum.loc[1, col]
                value0 = data_kwh_sum.loc[0, col]

                # Div by 0 put '-'
                if value0 == 0 and value1 == 0:
                    ratio = 0
                elif value0 == 0 and value1 != 0:
                    ratio = '-'
                else:
                    ratio = value1 / value0
                
                if ratio == '-':
                    new_value = '-'
                elif ratio == 1:
                    new_value = (1 - ratio) * 100  # Values are equal, ratio is 1
                elif ratio == 0:
                    new_value = (1 - ratio) * 100  # Value is 0, compute percentage difference
                else:
                    new_value = (1 - ratio) * 100
                
                new_row_3rd[col] = [f'{new_value:.1f}%'] if new_value != '-' else [new_value]

            # Convert new_row_3rd to a DataFrame
            new_row_3rd_df = pd.DataFrame(new_row_3rd)

            # Insert the new row after the 2nd row (index 1)
            data_kwh_sum = pd.concat([data_kwh_sum.iloc[:2], new_row_3rd_df, data_kwh_sum.iloc[2:]]).reset_index(drop=True)

            # Calculate the new row as the ratio of the second last row to the third last row
            new_row_last = {
                'UNIT': ['Demand Savings'],
                'Filename': [''],
                'Meterings': [''],
            }

            columns = [
                'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING',
                'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
            ]

            for col in columns:
                st.write(data_kwh_sum)
                # st.write(data_kwh_sum.shape)
                value4 = data_kwh_sum.loc[4, col]
                value3 = data_kwh_sum.loc[3, col]
                
                if value3 == 0 and value4 == 0:
                    ratio = 0
                elif value3 == 0 and value4 != 0:
                    ratio = '-'
                else:
                    # st.success(value4)
                    # st.success(value3)
                    ratio = value4 / value3
                    
                if ratio == '-':
                    new_value = '-'
                elif ratio == 1:
                    new_value = (1 - ratio) * 100  # Values are equal, ratio is 1
                elif ratio == 0:
                    new_value = (1 - ratio) * 100  # Value is 0, compute percentage difference
                else:
                    new_value = (1 - ratio) * 100
                new_row_last[col] = [f'{new_value:.1f}%'] if new_value != '-' else [new_value]

            # Convert new_row_last to a DataFrame and append it to data_kwh_sum
            new_row_last_df = pd.DataFrame(new_row_last)
            data_kwh_sum = pd.concat([data_kwh_sum, new_row_last_df]).reset_index(drop=True)

            # now append to last row of data_kwh_sum
            if not data_kwh_sum.empty:
                new_row_last = {
                    'UNIT': ['EFLH Baseline'],
                    'Filename': [''],
                    'Meterings': [''],
                }
                new_row_last1 = {
                    'UNIT': ['EFLH Proposed'],
                    'Filename': [''],
                    'Meterings': [''],
                }
                columns = [
                    'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING',
                    'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                    'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
                ]
                
                for col in columns:
                    value0 = data_kwh_sum.loc[0, col]
                    value3 = data_kwh_sum.loc[3, col]

                    if value0 == 0 and value3 == 0:
                        ratio1 = 0
                    elif value0 == 0 and value3 != 0:
                        ratio1 = 0
                    elif value3 == 0 and value0 != 0:
                        ratio1 = '-'
                    else:
                        # value3 = value3.replace("%", "")
                        ratio1 = float(value0)/float(value3)
                    new_row_last[col] = [f'{ratio1:.1f}'] if ratio1 != '-' else [ratio1]

                for col in columns:
                    value1 = data_kwh_sum.loc[1, col]
                    value4 = data_kwh_sum.loc[4, col]
                    if value1 == 0 and value4 == 0:
                        ratio2 = 0
                    elif value4 == 0 and value1 != 0:
                        ratio2 = '-'
                    else:
                        ratio2 = value1 / value4
                    new_row_last1[col] = [f'{ratio2:.1f}'] if ratio2 != '-' else [ratio2]
                
                # Convert new_row_last to a DataFrame and append it to data_kwh_sum
                new_row_last_df = pd.DataFrame(new_row_last)
                new_row_last_df1 = pd.DataFrame(new_row_last1)
                data_kwh_sum = pd.concat([data_kwh_sum, new_row_last_df, new_row_last_df1]).reset_index(drop=True)

        # st.markdown(f"""<h6 style="color:green;">🟡 THERM & MAX THERM/HR</h6>""", unsafe_allow_html=True)
        # converting to numeric type and removing comma from data
        data_therm['LIGHTS'] = pd.to_numeric(data_therm['LIGHTS'].str.replace(',',''), errors='coerce')
        data_therm['TASK LIGHTS'] = pd.to_numeric(data_therm['TASK LIGHTS'].str.replace(',',''), errors='coerce')
        data_therm['MISC EQUIP'] = pd.to_numeric(data_therm['MISC EQUIP'].str.replace(',',''), errors='coerce')
        data_therm['SPACE EQUIP'] = pd.to_numeric(data_therm['SPACE EQUIP'].str.replace(',',''), errors='coerce')
        data_therm['SPACE COOLING'] = pd.to_numeric(data_therm['SPACE COOLING'].str.replace(',',''), errors='coerce')
        data_therm['HEAT REJECT'] = pd.to_numeric(data_therm['HEAT REJECT'].str.replace(',',''), errors='coerce')
        data_therm['PUMPS & AUX'] = pd.to_numeric(data_therm['PUMPS & AUX'].str.replace(',',''), errors='coerce')
        data_therm['VENT FANS'] = pd.to_numeric(data_therm['VENT FANS'].str.replace(',',''), errors='coerce')
        data_therm['REFRIG DISPLAY'] = pd.to_numeric(data_therm['REFRIG DISPLAY'].str.replace(',',''), errors='coerce')
        data_therm['HT PUMP SUPPLEM'] = pd.to_numeric(data_therm['HT PUMP SUPPLEM'].str.replace(',',''), errors='coerce')
        data_therm['DOMEST HOT WTR'] = pd.to_numeric(data_therm['DOMEST HOT WTR'].str.replace(',',''), errors='coerce')
        data_therm['EXT USAGE'] = pd.to_numeric(data_therm['EXT USAGE'].str.replace(',',''), errors='coerce')
        data_therm['TOTAL'] = pd.to_numeric(data_therm['TOTAL'].str.replace(',',''), errors='coerce')

        # form new dataframe with sum THERM in 1 row and sum MAX THERM/HR in 1 row means based on same UNIT column values add into 1 row
        data_therm_sum = data_therm.groupby(['UNIT', 'Filename']).sum().reset_index()

        if not data_therm_sum.empty:
            new_row_3rd = {
                'UNIT': ['Energy Savings'],
                'Filename': [''],
                'Meterings': [''],
            }

            columns = [
                'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING', 
                'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY', 
                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
            ]

            for col in columns:
                value1 = data_therm_sum.loc[1, col]
                value0 = data_therm_sum.loc[0, col]
                
                if value0 == 0 and value1 == 0:
                    ratio = 0
                elif value0 == 0 and value1 != 0:
                    ratio = '-'
                else:
                    ratio = value1 / value0

                if ratio == 1:
                    new_value = (1 - ratio) * 100  # Values are equal, ratio is 1
                elif ratio == 0:
                    new_value = (1 - ratio) * 100  # Value is 0, compute percentage difference
                else:
                    new_value = (1 - ratio) * 100

                new_row_3rd[col] = [f'{new_value:.1f}%'] if new_value != '-' else [new_value]

            # Convert new_row_3rd to a DataFrame
            new_row_3rd_df = pd.DataFrame(new_row_3rd)

            # Insert the new row after the 2nd row (index 1)
            data_therm_sum = pd.concat([data_therm_sum.iloc[:2], new_row_3rd_df, data_therm_sum.iloc[2:]]).reset_index(drop=True)

            # Calculate the new row as the ratio of the second last row to the third last row
            new_row_last = {
                'UNIT': ['Demand Savings'],
                'Filename': [''],
                'Meterings': [''],
            }

            columns = [
                'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING',
                'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
            ]

            for col in columns:
                value4 = data_therm_sum.loc[4, col]
                value3 = data_therm_sum.loc[3, col]
                
                if value3 == 0 and value4 == 0:
                    ratio = 0
                elif value3 == 0 and value4 != 0:
                    ratio = '-'
                else:
                    ratio = value4 / value3
                    
                if ratio == 1:
                    new_value = (1 - ratio) * 100  # Values are equal, ratio is 1
                elif ratio == 0:
                    new_value = (1 - ratio) * 100  # Value is 0, compute percentage difference
                else:
                    new_value = (1 - ratio) * 100
                new_row_last[col] = [f'{new_value:.1f}%'] if new_value != '-' else [new_value]

            # Convert new_row_last to a DataFrame and append it to data_kwh_sum
            new_row_last_df = pd.DataFrame(new_row_last)
            data_therm_sum = pd.concat([data_therm_sum, new_row_last_df]).reset_index(drop=True)

            # now append to last row of data_kwh_sum
            if not data_therm_sum.empty:
                new_row_last = {
                    'UNIT': ['EFLH Baseline'],
                    'Filename': [''],
                    'Meterings': [''],
                }
                new_row_last1 = {
                    'UNIT': ['EFLH Proposed'],
                    'Filename': [''],
                    'Meterings': [''],
                }
                columns = [
                    'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING',
                    'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                    'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
                ]
                
                for col in columns:
                    value0 = data_therm_sum.loc[0, col]
                    value3 = data_therm_sum.loc[3, col]

                    if value0 == 0 and value3 == 0:
                        ratio1 = 0
                    elif value0 == 0 and value3 != 0:
                        ratio1 = 0
                    elif value3 == 0 and value0 != 0:
                        ratio1 = '-'
                    else:
                        ratio1 = value0 / value3
                    new_row_last[col] = [f'{ratio1:.1f}'] if ratio1 != '-' else [ratio1]

                for col in columns:
                    value1 = data_therm_sum.loc[1, col]
                    value4 = data_therm_sum.loc[4, col]
                    if value1 == 0 and value4 == 0:
                        ratio2 = 0
                    elif value1 == 0 and value4 != 0:
                        ratio2 = 0
                    elif value1 != 0 and value4 == 0:
                        ratio2 = '-'
                    else:
                        ratio2 = value1 / value4
                    new_row_last1[col] = [f'{ratio2:.1f}'] if ratio2 != '-' else [ratio2]

                # Convert new_row_last to a DataFrame and append it to data_kwh_sum
                new_row_last_df = pd.DataFrame(new_row_last)
                new_row_last_df1 = pd.DataFrame(new_row_last1)
                data_therm_sum = pd.concat([data_therm_sum, new_row_last_df, new_row_last_df1]).reset_index(drop=True)
       
        # st.markdown(f"""<h6 style="color:blue;">🔵 MBTU & MAX MBTU/HR</h6>""", unsafe_allow_html=True)
        # converting to numeric type and removing comma from data
        data_mbtu['LIGHTS'] = pd.to_numeric(data_mbtu['LIGHTS'].str.replace(',',''), errors='coerce')
        data_mbtu['TASK LIGHTS'] = pd.to_numeric(data_mbtu['TASK LIGHTS'].str.replace(',',''), errors='coerce')
        data_mbtu['MISC EQUIP'] = pd.to_numeric(data_mbtu['MISC EQUIP'].str.replace(',',''), errors='coerce')
        data_mbtu['SPACE EQUIP'] = pd.to_numeric(data_mbtu['SPACE EQUIP'].str.replace(',',''), errors='coerce')
        data_mbtu['SPACE COOLING'] = pd.to_numeric(data_mbtu['SPACE COOLING'].str.replace(',',''), errors='coerce')
        data_mbtu['HEAT REJECT'] = pd.to_numeric(data_mbtu['HEAT REJECT'].str.replace(',',''), errors='coerce')
        data_mbtu['PUMPS & AUX'] = pd.to_numeric(data_mbtu['PUMPS & AUX'].str.replace(',',''), errors='coerce')
        data_mbtu['VENT FANS'] = pd.to_numeric(data_mbtu['VENT FANS'].str.replace(',',''), errors='coerce')
        data_mbtu['REFRIG DISPLAY'] = pd.to_numeric(data_mbtu['REFRIG DISPLAY'].str.replace(',',''), errors='coerce')
        data_mbtu['HT PUMP SUPPLEM'] = pd.to_numeric(data_mbtu['HT PUMP SUPPLEM'].str.replace(',',''), errors='coerce')
        data_mbtu['DOMEST HOT WTR'] = pd.to_numeric(data_mbtu['DOMEST HOT WTR'].str.replace(',',''), errors='coerce')
        data_mbtu['EXT USAGE'] = pd.to_numeric(data_mbtu['EXT USAGE'].str.replace(',',''), errors='coerce')
        data_mbtu['TOTAL'] = pd.to_numeric(data_mbtu['TOTAL'].str.replace(',',''), errors='coerce')

        # form new dataframe with sum MBTU in 1 row and sum MAX MBTU/HR in 1 row means based on same UNIT column values add into 1 row
        data_mbtu_sum = data_mbtu.groupby(['UNIT', 'Filename']).sum().reset_index()

        if not data_mbtu_sum.empty:
            # Calculate the new row as the ratio of the second last row to the third last row
            new_row_3rd = {
                'UNIT': ['Energy Savings'],
                'Filename': [''],
                'Meterings': [''],
            }

            columns = [
                'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING', 
                'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY', 
                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
            ]

            for col in columns:
                value1 = data_mbtu_sum.loc[1, col]
                value0 = data_mbtu_sum.loc[0, col]
                
                if value0 == 0 and value1 == 0:
                    ratio = 0
                elif value0 == 0 and value1 != 0:
                    ratio = '-'
                else:
                    ratio = value1 / value0

                if ratio == 1:
                    new_value = (1 - ratio) * 100  # Values are equal, ratio is 1
                elif ratio == 0:
                    new_value = (1 - ratio) * 100  # Value is 0, compute percentage difference
                else:
                    new_value = (1 - ratio) * 100

                new_row_3rd[col] = [f'{new_value:.1f}%'] if new_value != '-' else [new_value]

            # Convert new_row_3rd to a DataFrame
            new_row_3rd_df = pd.DataFrame(new_row_3rd)

            # Insert the new row after the 2nd row (index 1)
            data_mbtu_sum = pd.concat([data_mbtu_sum.iloc[:2], new_row_3rd_df, data_mbtu_sum.iloc[2:]]).reset_index(drop=True)

            # Calculate the new row as the ratio of the second last row to the third last row
            new_row_last = {
                'UNIT': ['Demand Savings'],
                'Filename': [''],
                'Meterings': [''],
            }

            columns = [
                'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING',
                'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
            ]

            for col in columns:
                value4 = data_mbtu_sum.loc[4, col]
                value3 = data_mbtu_sum.loc[3, col]
                
                if value3 == 0 and value4 == 0:
                    ratio = 0
                elif value3 == 0 and value4 != 0:
                    ratio = '-'
                else:
                    ratio = value4 / value3
                    
                if ratio == 1:
                    new_value = (1 - ratio) * 100  # Values are equal, ratio is 1
                elif ratio == 0:
                    new_value = (1 - ratio) * 100  # Value is 0, compute percentage difference
                else:
                    new_value = (1 - ratio) * 100
                new_row_last[col] = [f'{new_value:.1f}%'] if new_value != '-' else [new_value]

            # Convert new_row_last to a DataFrame and append it to data_kwh_sum
            new_row_last_df = pd.DataFrame(new_row_last)
            data_mbtu_sum = pd.concat([data_mbtu_sum, new_row_last_df]).reset_index(drop=True)

            # now append to last row of data_kwh_sum
            if not data_mbtu_sum.empty:
                new_row_last = {
                    'UNIT': ['EFLH Baseline'],
                    'Filename': [''],
                    'Meterings': [''],
                }
                new_row_last1 = {
                    'UNIT': ['EFLH Proposed'],
                    'Filename': [''],
                    'Meterings': [''],
                }
                columns = [
                    'LIGHTS', 'TASK LIGHTS', 'MISC EQUIP', 'SPACE EQUIP', 'SPACE COOLING',
                    'HEAT REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                    'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL'
                ]
                
                for col in columns:
                    value0 = data_mbtu_sum.loc[0, col]
                    value3 = data_mbtu_sum.loc[3, col]

                    if value0 == 0 and value3 == 0:
                        ratio1 = 0
                    elif value0 == 0 and value3 != 0:
                        ratio1 = 0
                    elif value3 == 0 and value0 != 0:
                        ratio1 = '-'
                    else:
                        ratio1 = value0 / value3
                    new_row_last[col] = [f'{ratio1:.1f}'] if ratio1 != '-' else [ratio1]

                for col in columns:
                    value1 = data_mbtu_sum.loc[1, col]
                    value4 = data_mbtu_sum.loc[4, col]
                    if value1 == 0 and value4 == 0:
                        ratio2 = 0
                    elif value1 == 0 and value4 != 0:
                        ratio2 = 0
                    elif value1 != 0 and value4 == 0:
                        ratio2 = '-'
                    else:
                        ratio2 = value1 / value4
                    new_row_last1[col] = [f'{ratio2:.1f}'] if ratio2 != '-' else [ratio2]

                # Convert new_row_last to a DataFrame and append it to data_kwh_sum
                new_row_last_df = pd.DataFrame(new_row_last)
                new_row_last_df1 = pd.DataFrame(new_row_last1)
                data_mbtu_sum = pd.concat([data_mbtu_sum, new_row_last_df, new_row_last_df1]).reset_index(drop=True)

        ###############################################################################################################
        ################################################## Pie CHART ##################################################
        ###############################################################################################################
        
        st.markdown(f"""<h6 style="color:red;">🔴 ENERGY DISTRIBUTION PIE CHART BASED ON UNITS</h6>""", unsafe_allow_html=True)
        if not data_kwh_sum.empty:
            st.markdown(f"""<h7 style="color:blue;">🔵 kWH </h7>""", unsafe_allow_html=True)
            # Select the rows to be used for the pie charts
            row3 = data_kwh_sum.iloc[0, :-1]
            row_last = data_kwh_sum.iloc[1, :-1]
            # Ensure the rows are numeric
            if pd.to_numeric(row3, errors='coerce').sum() == 0 and pd.to_numeric(row_last, errors='coerce').sum() == 0:
                st.markdown("""<p><strong>Note:</strong> All values are zero. No meaningful visualization can be displayed.</p>""", unsafe_allow_html=True)
            else:
                fig1 = px.pie(values=row3.values, names=row3.index, title='Baseline')
                fig2 = px.pie(values=row_last.values, names=row_last.index, title='Proposed')
        
                fig1.update_traces(textinfo='percent+label')
                fig2.update_traces(textinfo='percent+label')
        
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig1)
                with col2:
                    st.plotly_chart(fig2)
        else:
            st.markdown("""<p><strong>Note:</strong> No data found for kWH & MAX kW.</p>""", unsafe_allow_html=True)

        st.markdown(f"""<h7 style="color:red;">🔴 MAX THERM/HR</h7>""", unsafe_allow_html=True)
        if not data_therm_sum.empty:
            row3 = data_therm_sum.iloc[0, :-1]
            row_last = data_therm_sum.iloc[1, :-1]
        
            # Ensure the rows are numeric
            if pd.to_numeric(row3, errors='coerce').sum() == 0 and pd.to_numeric(row_last, errors='coerce').sum() == 0:
                st.markdown("""<p><strong>Note:</strong> All values are zero. No meaningful visualization can be displayed.</p>""", unsafe_allow_html=True)
            else:
                fig1 = px.pie(values=row3.values, names=row3.index, title='Baseline')
                fig2 = px.pie(values=row_last.values, names=row_last.index, title='Proposed')
        
                fig1.update_traces(textinfo='percent+label')
                fig2.update_traces(textinfo='percent+label')
        
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig1)
                with col2:
                    st.plotly_chart(fig2)
        else:
            st.markdown("""<p><strong>Note:</strong> No data found for THERM & MAX THERM/HR.</p>""", unsafe_allow_html=True)

        st.markdown(f"""<h7 style="color:orange;">🟠 MAX MBTU/HR</h7>""", unsafe_allow_html=True)
        if not data_mbtu_sum.empty:
            # Select the rows to be used for the pie charts
            row3 = data_mbtu_sum.iloc[0, :-1]  # 3rd row (index 2) 
            row_last = data_mbtu_sum.iloc[1, :-1]  # Last row 
            # Ensure the rows are numeric
            if pd.to_numeric(row3, errors='coerce').sum() == 0 and pd.to_numeric(row_last, errors='coerce').sum() == 0:
                st.markdown("""<p><strong>Note:</strong> All values are zero. No meaningful visualization can be displayed.</p>""", unsafe_allow_html=True)
            else:
                fig1 = px.pie(values=row3.values, names=row3.index, title='Baseline')
                fig2 = px.pie(values=row_last.values, names=row_last.index, title='Proposed')
        
                fig1.update_traces(textinfo='percent+label')
                fig2.update_traces(textinfo='percent+label')
        
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig1)
                with col2:
                    st.plotly_chart(fig2)
        else:
            st.markdown("""<p><strong>Note:</strong> No data found for MBTU & MAX MBTU/HR.</p>""", unsafe_allow_html=True)

        ###############################################################################################################
        ################################################## EFLH TABLE #################################################
        ###############################################################################################################
        st.markdown(f"""<h6 style="color:red;">🔴 ENERGY DISTRIBUTION BAR CHART BASED ON UNITS</h6>""", unsafe_allow_html=True)
        if not data_kwh_sum.empty:
            st.markdown(f"""<h7 style="color:blue;">🔵 kWH </h7>""", unsafe_allow_html=True)
            # Select the rows to be used for the bar charts
            row0 = data_kwh_sum.iloc[0, 3:-1]  # 3rd row (index 2)
            row1 = data_kwh_sum.iloc[1, 3:-1]  # Last row
            row2 = data_kwh_sum.iloc[2, 3:-1]  # 2nd row (index 1)
            # Ensure the rows are numeric
            if pd.to_numeric(row0, errors='coerce').sum() == 0 and pd.to_numeric(row1, errors='coerce').sum() == 0:
                st.markdown("""<p><strong>Note:</strong> All values are zero. No meaningful visualization can be displayed.</p>""", unsafe_allow_html=True)
            else:
                # Create a combined bar chart
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=row0.index, y=row0.values, name='Baseline', marker_color='red'))
                fig3.add_trace(go.Bar(x=row1.index, y=row1.values, name='Proposed', marker_color='blue'))

                # Add annotations for the percentages from row2
                for i, (category, value) in enumerate(zip(row0.index, row2.values)):
                    fig3.add_annotation(
                        x=category,
                        y=max(row0.values[i], row1.values[i]),
                        text=f"{value}",
                        showarrow=False,
                        yshift=10  # Adjust this value to position the text above the bars
                    )

                # Update layout for the bar chart
                fig3.update_layout(
                    title='Baseline and Proposed Bar Chart', 
                    barmode='group', 
                    xaxis_title='End Uses', 
                    yaxis_title='kWH',
                    legend=dict(
                        orientation="h",  # Horizontal legend
                        yanchor="bottom", 
                        y=-0.3,  # Position the legend below the chart
                        xanchor="center", 
                        x=0.5
                    )
                )
                st.plotly_chart(fig3)
        else:
            st.markdown("""<p><strong>Note:</strong> No data found for kWH & kW.</p>""", unsafe_allow_html=True)

        st.markdown(f"""<h7 style="color:red;">🔴 MAX THERM/HR</h7>""", unsafe_allow_html=True)
        if not data_therm_sum.empty:
            row0 = data_therm_sum.iloc[0, 3:-1]
            row1 = data_therm_sum.iloc[1, 3:-1]
            row2 = data_therm_sum.iloc[2, 3:-1]  # 2nd row (index 1)
            # Ensure the rows are numeric
            if pd.to_numeric(row0, errors='coerce').sum() == 0 and pd.to_numeric(row1, errors='coerce').sum() == 0:
                st.markdown("""<p><strong>Note:</strong> All values are zero. No meaningful visualization can be displayed.</p>""", unsafe_allow_html=True)
            else:
                # Create a combined bar chart
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=row0.index, y=row0.values, name='Baseline', marker_color='red'))
                fig3.add_trace(go.Bar(x=row1.index, y=row1.values, name='Proposed', marker_color='blue'))
                # Add annotations for the percentages from row2
                for i, (category, value) in enumerate(zip(row0.index, row2.values)):
                    fig3.add_annotation(
                        x=category,
                        y=max(row0.values[i], row1.values[i]),
                        text=f"{value}",
                        showarrow=False,
                        yshift=10  # Adjust this value to position the text above the bars
                    )

                # Update layout for the bar chart
                fig3.update_layout(
                    title='Baseline and Proposed Bar Chart', 
                    barmode='group', 
                    xaxis_title='End Uses', 
                    yaxis_title='MAX THERM/HR',
                    legend=dict(
                        orientation="h",  # Horizontal legend
                        yanchor="bottom", 
                        y=-0.3,  # Position the legend below the chart
                        xanchor="center", 
                        x=0.5
                    )
                )

                st.plotly_chart(fig3)
        else:
            st.markdown("""<p><strong>Note:</strong> No data found for THERM & MAX THERM/HR.</p>""", unsafe_allow_html=True)

        st.markdown(f"""<h7 style="color:orange;">🟠 MAX MBTU/HR</h7>""", unsafe_allow_html=True)
        if not data_mbtu_sum.empty:
            # Select the rows to be used for the pie charts
            row0 = data_mbtu_sum.iloc[0, 3:-1]  # 3rd row (index 2) 
            row1 = data_mbtu_sum.iloc[1, 3:-1]  # Last row 
            row2 = data_kwh_sum.iloc[2, 3:-1]  # 2nd row (index 1)
            # Ensure the rows are numeric
            if pd.to_numeric(row0, errors='coerce').sum() == 0 and pd.to_numeric(row1, errors='coerce').sum() == 0:
                st.markdown("""<p><strong>Note:</strong> All values are zero. No meaningful visualization can be displayed.</p>""", unsafe_allow_html=True)
            else:
                # Create a combined bar chart
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=row0.index, y=row0.values, name='Baseline', marker_color='red'))
                fig3.add_trace(go.Bar(x=row1.index, y=row1.values, name='Proposed', marker_color='blue'))

                # Add annotations for the percentages from row2
                for i, (category, value) in enumerate(zip(row0.index, row2.values)):
                    fig3.add_annotation(
                        x=category,
                        y=max(row0.values[i], row1.values[i]),
                        text=f"{value}",
                        showarrow=False,
                        yshift=10  # Adjust this value to position the text above the bars
                    )

                # Update layout for the bar chart
                fig3.update_layout(
                    title='Baseline and Proposed Bar Chart', 
                    barmode='group', 
                    xaxis_title='End Uses', 
                    yaxis_title='MAX MBTU/HR',
                    legend=dict(
                        orientation="h",  # Horizontal legend
                        yanchor="bottom", 
                        y=-0.3,  # Position the legend below the chart
                        xanchor="center", 
                        x=0.5
                    )
                )
                st.plotly_chart(fig3)
        else:
            st.markdown("""<p><strong>Note:</strong> No data found for MBTU & MAX MBTU/HR.</p>""", unsafe_allow_html=True)

        ################################################## MASTER TABLE ##############################################
        with st.expander("📋 **Explore Tables** "):
            st.markdown(f"""<h6 style="color:red;">🔴 MASTER TABLE HAVING SAVINGS(in %), EFLH, % CONTRIBUTION BASED ON UNITS </h6>""", unsafe_allow_html=True)
            st.markdown(f"""<h7 style="color:blue;">🔵 kWH & MAX kW</h7>""", unsafe_allow_html=True)
            # if empty dataframe then write message in markdown - No KWH & MAX KW data found in the selected data
            if data_kwh_sum.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for kWH & MAX kW.</p>""", unsafe_allow_html=True)
            else:
                data_kwh_sum1 = data_kwh.groupby(['Filename', 'UNIT']).sum().reset_index().sort_values(by=['Filename', 'UNIT'], ascending=False)
                # Extract the last column values
                last_column_values = data_kwh_sum1.iloc[:, -1].values
                # Unpack the values into separate variables
                kw_proposed_total, kwh_proposed_total, kw_baseline_total, kwh_baseline_total = last_column_values
                
                # Step 2: Define the new empty row (NaN values)
                empty_row = pd.DataFrame([['']*data_kwh_sum1.shape[1]], columns=data_kwh_sum1.columns)
                # Step 3: Split the DataFrame and insert the new empty row
                df_part1 = data_kwh_sum1.iloc[:2]       # Up to the second row
                df_part2 = data_kwh_sum1.iloc[2:]       # From the third row onward
    
                # Step 4: Concatenate the parts to form the final DataFrame
                data_kwh_sum1 = pd.concat([df_part1, empty_row, df_part2], ignore_index=True)
                
                empty_row1 = pd.DataFrame([['']*data_kwh_sum1.shape[1]], columns=data_kwh_sum1.columns)
                df_part1 = data_kwh_sum1.iloc[:5]
                data_kwh_sum1 = pd.concat([df_part1, empty_row], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_kwh_sum1.columns}
                new_row[data_kwh_sum1.columns[0]] = "% Contribution"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                
                # Step 3: Append the new row to the DataFrame
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                new_row = {
                    'Filename': 'Proposed',  
                    'UNIT': '', 
                    'Meterings': ''
                }
    
                for col in data_kwh_sum1.columns[3:]:
                    if kwh_proposed_total != 0:
                        new_row[col] = f'{round(data_kwh_sum1[col].iloc[1]*100 / kwh_proposed_total,1)}%'
                    elif kwh_proposed_total == 0 and data_kwh_sum1[col].iloc[1] == 0:
                        new_row[col] = '0.0%'
                    elif kwh_proposed_total == 0 and data_kwh_sum1[col].iloc[1] != 0:
                        new_row[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
                
                new_row1 = {
                    'Filename': 'Baseline',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_kwh_sum1.columns[3:]:
                    if kwh_baseline_total != 0:
                        new_row1[col] = f'{round(data_kwh_sum1[col].iloc[4]*100 / kwh_baseline_total,1)}%'
                    elif kwh_baseline_total == 0 and data_kwh_sum1[col].iloc[4] == 0:
                        new_row1[col] = '0.0%'
                    elif kwh_baseline_total == 0 and data_kwh_sum1[col].iloc[4] != 0:
                        new_row1[col] = '-'
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row1])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                # Step 2: Define the new empty row (NaN values)
                empty_row2 = pd.DataFrame([['']*data_kwh_sum1.shape[1]], columns=data_kwh_sum1.columns)
                # Step 3: Split the DataFrame and insert the new empty row
                df_part1 = data_kwh_sum1.iloc[:9]       # Up to the second row
    
                # Step 4: Concatenate the parts to form the final DataFrame
                data_kwh_sum1 = pd.concat([df_part1, empty_row2], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_kwh_sum1.columns}
                new_row[data_kwh_sum1.columns[0]] = "% Savings"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                new_row0 = {
                    'Filename': 'Energy',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_kwh_sum1.columns[3:]:
                    if data_kwh_sum1[col].iloc[4] != 0:  # Check to avoid division by zero
                        new_row0[col] = f'{round((1 - (data_kwh_sum1[col].iloc[1] / data_kwh_sum1[col].iloc[4]))*100,1)}%'
                    elif data_kwh_sum1[col].iloc[4] == 0 and data_kwh_sum1[col].iloc[1] == 0:
                        new_row0[col] = '100.0%'
                    elif data_kwh_sum1[col].iloc[4] == 0 and data_kwh_sum1[col].iloc[1] != 0:
                        new_row0[col] = '-'
                
                new_row_df = pd.DataFrame([new_row0])
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
                new_row00 = {
                    'Filename': 'Demand',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_kwh_sum1.columns[3:]:
                    if data_kwh_sum1[col].iloc[3] != 0:  # Check to avoid division by zero
                        new_row00[col] = f'{round((1 - (data_kwh_sum1[col].iloc[0] / data_kwh_sum1[col].iloc[3]))*100,1)}%'
                    elif data_kwh_sum1[col].iloc[0] == 0 and data_kwh_sum1[col].iloc[3] == 0:
                        new_row00[col] = '100.0%'
                    elif data_kwh_sum1[col].iloc[3] == 0 and data_kwh_sum1[col].iloc[0] != 0:
                        new_row00[col] = '-'
                
                new_row_df = pd.DataFrame([new_row00])
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                empty_row3 = pd.DataFrame([['']*data_kwh_sum1.shape[1]], columns=data_kwh_sum1.columns)
                df_part1 = data_kwh_sum1.iloc[:13] # upto 13 rows
                data_kwh_sum1 = pd.concat([df_part1, empty_row3], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_kwh_sum1.columns}
                new_row[data_kwh_sum1.columns[0]] = "EFLH"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                
                # Step 3: Append the new row to the DataFrame
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                new_row2 = {
                    'Filename': 'Proposed',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_kwh_sum1.columns[3:]:
                    if data_kwh_sum1[col].iloc[0] != 0:  # Check to avoid division by zero
                        new_row2[col] = round(data_kwh_sum1[col].iloc[1] / data_kwh_sum1[col].iloc[0], 1)
                    elif data_kwh_sum1[col].iloc[0] == 0 and data_kwh_sum1[col].iloc[1] == 0:
                        new_row2[col] = '0.0'
                    elif data_kwh_sum1[col].iloc[0] == 0 and data_kwh_sum1[col].iloc[1] != 0:
                        new_row2[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row2])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                new_row3 = {
                    'Filename': 'Baseline',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_kwh_sum1.columns[3:]:
                    if data_kwh_sum1[col].iloc[3] != 0:
                        new_row3[col] = round(data_kwh_sum1[col].iloc[4] / data_kwh_sum1[col].iloc[3], 1)
                    elif data_kwh_sum1[col].iloc[3] == 0 and data_kwh_sum1[col].iloc[4] == 0:
                        new_row3[col] = '0.0'
                    elif data_kwh_sum1[col].iloc[3] == 0 and data_kwh_sum1[col].iloc[4] != 0:
                        new_row3[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row3])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
    
                new_row4 = {
                    'Filename': '% Difference',  
                    'UNIT': '', 
                    'Meterings': ''
                }
    
                for col in data_kwh_sum1.columns[3:]:
                    try:
                        # Ensure the values are numeric
                        val_16 = float(data_kwh_sum1[col].iloc[16])
                        val_15 = float(data_kwh_sum1[col].iloc[15])
                        
                        if val_16 != 0:
                            new_row4[col] = f'{round((1 - (val_15 / val_16)) * 100, 1)}%'
                        elif val_16 == 0 and val_15 == 0:
                            new_row4[col] = '100.0%'
                        elif val_16 == 0 and val_15 != 0:
                            new_row4[col] = '-'
                    except ValueError:
                        new_row4[col] = 'Invalid data'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row4])
                data_kwh_sum1 = pd.concat([data_kwh_sum1, new_row_df], ignore_index=True)
                # st.write(data_kwh_sum1)
    
            st.markdown(f"""<h7 style="color:red;">🔴 THERM & MAX THERM/HR</h7>""", unsafe_allow_html=True)
            # if empty dataframe then write message in markdown - No THERM & MAX THERM/HR data found in the selected data
            if data_therm_sum.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for THERM & MAX THERM/HR.</p>""", unsafe_allow_html=True)
            else:
                data_therm_sum1 = data_therm.groupby(['Filename', 'UNIT']).sum().reset_index().sort_values(by=['Filename', 'UNIT'], ascending=False)
                # Extract the last column values
                last_column_values = data_therm_sum1.iloc[:, -1].values
                # Unpack the values into separate variables
                therm_proposed_total, thermhr_proposed_total, therm_baseline_total, thermhr_baseline_total = last_column_values
                
                # Step 2: Define the new empty row (NaN values)
                empty_row = pd.DataFrame([['']*data_therm_sum1.shape[1]], columns=data_therm_sum1.columns)
                # Step 3: Split the DataFrame and insert the new empty row
                df_part1 = data_therm_sum1.iloc[:2]       # Up to the second row
                df_part2 = data_therm_sum1.iloc[2:]       # From the third row onward
    
                # Step 4: Concatenate the parts to form the final DataFrame
                data_therm_sum1 = pd.concat([df_part1, empty_row, df_part2], ignore_index=True)
                
                empty_row1 = pd.DataFrame([['']*data_therm_sum1.shape[1]], columns=data_therm_sum1.columns)
                df_part1 = data_therm_sum1.iloc[:5]
                data_therm_sum1 = pd.concat([df_part1, empty_row], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_therm_sum1.columns}
                new_row[data_therm_sum1.columns[0]] = "% Contribution"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                
                # Step 3: Append the new row to the DataFrame
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                new_row = {
                    'Filename': 'Proposed',  
                    'UNIT': '', 
                    'Meterings': ''
                }
    
                for col in data_therm_sum1.columns[3:]:
                    if thermhr_proposed_total != 0:
                        new_row[col] = f'{round(data_therm_sum1[col].iloc[1]*100 / thermhr_proposed_total,1)}%'
                    elif thermhr_proposed_total == 0 and data_therm_sum1[col].iloc[1] == 0:
                        new_row[col] = '0.0%'
                    elif thermhr_proposed_total == 0 and data_therm_sum1[col].iloc[1] != 0:
                        new_row[col] = '-'
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
                new_row1 = {
                    'Filename': 'Baseline',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_therm_sum1.columns[3:]:
                    if thermhr_baseline_total != 0:
                        new_row1[col] = f'{round(data_therm_sum1[col].iloc[4]*100 / thermhr_baseline_total,1)}%'
                    elif thermhr_baseline_total == 0 and data_therm_sum1[col].iloc[4] == 0:
                        new_row1[col] = '0.0%'
                    elif thermhr_baseline_total == 0 and data_therm_sum1[col].iloc[4] != 0:
                        new_row1[col] = '-'
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row1])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                # Step 2: Define the new empty row (NaN values)
                empty_row2 = pd.DataFrame([['']*data_therm_sum1.shape[1]], columns=data_therm_sum1.columns)
                # Step 3: Split the DataFrame and insert the new empty row
                df_part1 = data_therm_sum1.iloc[:9]       # Up to the second row
    
                # Step 4: Concatenate the parts to form the final DataFrame
                data_therm_sum1 = pd.concat([df_part1, empty_row2], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_therm_sum1.columns}
                new_row[data_therm_sum1.columns[0]] = "% Savings"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                new_row0 = {
                    'Filename': 'Energy',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_therm_sum1.columns[3:]:
                    if data_therm_sum1[col].iloc[4] != 0:  # Check to avoid division by zero
                        new_row0[col] = f'{round((1 - (data_therm_sum1[col].iloc[1] / data_therm_sum1[col].iloc[4])) * 100, 1)}%'
                    elif data_therm_sum1[col].iloc[4] == 0 and data_therm_sum1[col].iloc[1] == 0:
                        new_row0[col] = '100.0%'
                    elif data_therm_sum1[col].iloc[4] == 0 and data_therm_sum1[col].iloc[1] != 0:
                        new_row0[col] = '-'
    
                new_row_df = pd.DataFrame([new_row0])
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
                new_row00 = {
                    'Filename': 'Demand',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_therm_sum1.columns[3:]:
                    if data_therm_sum1[col].iloc[3] != 0:  # Check to avoid division by zero
                        new_row00[col] = f'{round((1 - (data_therm_sum1[col].iloc[0] / data_therm_sum1[col].iloc[3]))*100,1)}%'
                    elif data_therm_sum1[col].iloc[3] == 0 and data_therm_sum1[col].iloc[0] == 0:
                        new_row00[col] = '100.0%'
                    elif data_therm_sum1[col].iloc[3] == 0 and data_therm_sum1[col].iloc[0] != 0:
                        new_row00[col] = '-'
                
                new_row_df = pd.DataFrame([new_row00])
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                empty_row3 = pd.DataFrame([['']*data_therm_sum1.shape[1]], columns=data_therm_sum1.columns)
                df_part1 = data_therm_sum1.iloc[:13] # upto 13 rows
                data_therm_sum1 = pd.concat([df_part1, empty_row3], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_therm_sum1.columns}
                new_row[data_therm_sum1.columns[0]] = "EFLH"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                
                # Step 3: Append the new row to the DataFrame
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                new_row2 = {
                    'Filename': 'Proposed',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_therm_sum1.columns[3:]:
                    if data_therm_sum1[col].iloc[0] != 0:  # Check to avoid division by zero
                        new_row2[col] = round(data_therm_sum1[col].iloc[1] / data_therm_sum1[col].iloc[0], 1)
                    elif data_therm_sum1[col].iloc[1] == 0 and data_therm_sum1[col].iloc[0] == 0:
                        new_row2[col] = '0.0'
                    elif data_therm_sum1[col].iloc[1] != 0 and data_therm_sum1[col].iloc[0] == 0:
                        new_row2[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row2])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                new_row3 = {
                    'Filename': 'Baseline',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_therm_sum1.columns[3:]:
                    if data_therm_sum1[col].iloc[3] != 0:
                        new_row3[col] = round(data_therm_sum1[col].iloc[4] / data_therm_sum1[col].iloc[3],1)
                    elif data_therm_sum1[col].iloc[4] == 0 and data_therm_sum1[col].iloc[3] == 0:
                        new_row3[col] = '0.0'
                    elif data_therm_sum1[col].iloc[4] != 0 and data_therm_sum1[col].iloc[3] == 0:
                        new_row3[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row3])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
    
                new_row4 = {
                    'Filename': '% Difference',  
                    'UNIT': '', 
                    'Meterings': ''
                }
    
                for col in data_therm_sum1.columns[3:]:
                    try:
                        # Ensure the values are numeric
                        val_16 = float(data_therm_sum1[col].iloc[16])
                        val_15 = float(data_therm_sum1[col].iloc[15])
                        
                        if val_16 != 0:
                            new_row4[col] = f'{round((1 - (val_15 / val_16)) * 100, 1)}%'
                        elif val_16 == 0 and val_15 == 0:
                            new_row4[col] = '100.0%'
                        elif val_16 == 0 and val_15 != 0:
                            new_row4[col] = '-'
                    except ValueError:
                        new_row4[col] = 'Invalid data'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row4])
                data_therm_sum1 = pd.concat([data_therm_sum1, new_row_df], ignore_index=True)
                # st.write(data_therm_sum1)
            
            st.markdown(f"""<h7 style="color:orange;">🟠 MBTU & MAX MBTU/HR</h7>""", unsafe_allow_html=True)
             # if empty dataframe then write message in markdown - No MBTU & MAX MBTU data found in the selected data
            if data_mbtu_sum.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for MBTU & MAX MBTU/HR.</p>""", unsafe_allow_html=True)
            else:
                data_mbtu_sum1 = data_mbtu.groupby(['Filename', 'UNIT']).sum().reset_index().sort_values(by=['Filename', 'UNIT'], ascending=False)
                # Extract the last column values
                last_column_values = data_mbtu_sum1.iloc[:, -1].values
                # Unpack the values into separate variables
                mbtu_proposed_total, mbtuhr_proposed_total, mbtu_baseline_total, mbtuhr_baseline_total = last_column_values
                
                # Step 2: Define the new empty row (NaN values)
                empty_row = pd.DataFrame([['']*data_mbtu_sum1.shape[1]], columns=data_mbtu_sum1.columns)
                # Step 3: Split the DataFrame and insert the new empty row
                df_part1 = data_mbtu_sum1.iloc[:2]       # Up to the second row
                df_part2 = data_mbtu_sum1.iloc[2:]       # From the third row onward
    
                # Step 4: Concatenate the parts to form the final DataFrame
                data_mbtu_sum1 = pd.concat([df_part1, empty_row, df_part2], ignore_index=True)
                
                empty_row1 = pd.DataFrame([['']*data_mbtu_sum1.shape[1]], columns=data_mbtu_sum1.columns)
                df_part1 = data_mbtu_sum1.iloc[:5]
                data_mbtu_sum1 = pd.concat([df_part1, empty_row], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_mbtu_sum1.columns}
                new_row[data_mbtu_sum1.columns[0]] = "% Contribution"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                
                # Step 3: Append the new row to the DataFrame
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                new_row = {
                    'Filename': 'Proposed',  
                    'UNIT': '', 
                    'Meterings': ''
                }
    
                for col in data_mbtu_sum1.columns[3:]:
                    if mbtuhr_proposed_total != 0:
                        new_row[col] = f'{round(data_mbtu_sum1[col].iloc[1]*100 / mbtuhr_proposed_total,1)}%'
                    elif mbtuhr_proposed_total == 0 and data_mbtu_sum1[col].iloc[1] == 0:
                        new_row[col] = '0.0%'
                    elif data_mbtu_sum1[col].iloc[1] != 0 and mbtuhr_proposed_total == 0:
                        new_row[col] = '-'
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row])
                
                # Concatenate the new row DataFrame with the existing DataFrame
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
                new_row1 = {
                    'Filename': 'Baseline',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_mbtu_sum1.columns[3:]:
                    if mbtuhr_baseline_total != 0:
                        new_row1[col] = f'{round(data_mbtu_sum1[col].iloc[4]*100 / mbtuhr_baseline_total,1)}%'
                    elif mbtuhr_baseline_total == 0 and data_mbtu_sum1[col].iloc[4] == 0:
                        new_row1[col] = '0.0%'
                    elif data_mbtu_sum1[col].iloc[4] != 0 and mbtuhr_baseline_total == 0:
                        new_row1[col] = '-'
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row1])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                # Step 2: Define the new empty row (NaN values)
                empty_row2 = pd.DataFrame([['']*data_mbtu_sum1.shape[1]], columns=data_mbtu_sum1.columns)
                # Step 3: Split the DataFrame and insert the new empty row
                df_part1 = data_mbtu_sum1.iloc[:9]       # Up to the second row
    
                # Step 4: Concatenate the parts to form the final DataFrame
                data_mbtu_sum1 = pd.concat([df_part1, empty_row2], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_mbtu_sum1.columns}
                new_row[data_mbtu_sum1.columns[0]] = "% Savings"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                new_row0 = {
                    'Filename': 'Energy',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_mbtu_sum1.columns[3:]:
                    if data_mbtu_sum1[col].iloc[4] != 0:  # Check to avoid division by zero
                        new_row0[col] = f'{round((1 - (data_mbtu_sum1[col].iloc[1] / data_mbtu_sum1[col].iloc[4]))*100,1)}%'
                    elif data_mbtu_sum1[col].iloc[4] == 0 and data_mbtu_sum1[col].iloc[1] == 0:
                        new_row0[col] = '100.0%'
                    elif data_mbtu_sum1[col].iloc[4] == 0 and data_mbtu_sum1[col].iloc[1] != 0:
                    # else:
                        new_row0[col] = '-'
                
                new_row_df = pd.DataFrame([new_row0])
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
                new_row00 = {
                    'Filename': 'Demand',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_mbtu_sum1.columns[3:]:
                    if data_mbtu_sum1[col].iloc[3] != 0:  # Check to avoid division by zero
                        new_row00[col] = f'{round((1 - (data_mbtu_sum1[col].iloc[0] / data_mbtu_sum1[col].iloc[3]))*100,1)}%'
                    elif data_mbtu_sum1[col].iloc[3] == 0 and data_mbtu_sum1[col].iloc[0] == 0:
                        new_row00[col] = '100.0%'
                    elif data_mbtu_sum1[col].iloc[3] == 0 and data_mbtu_sum1[col].iloc[0] != 0:
                    # else:
                        new_row00[col] = '-'
                
                new_row_df = pd.DataFrame([new_row00])
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                empty_row3 = pd.DataFrame([['']*data_mbtu_sum1.shape[1]], columns=data_mbtu_sum1.columns)
                df_part1 = data_mbtu_sum1.iloc[:13] # upto 13 rows
                data_mbtu_sum1 = pd.concat([df_part1, empty_row3], ignore_index=True)
    
                # Step 2: Dynamically create the new row with a value in the first column and empty strings in other columns
                new_row = {col: '' for col in data_mbtu_sum1.columns}
                new_row[data_mbtu_sum1.columns[0]] = "EFLH"
                
                # Convert the new row to a DataFrame
                new_row_df = pd.DataFrame([new_row])
                
                # Step 3: Append the new row to the DataFrame
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                new_row2 = {
                    'Filename': 'Proposed',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_mbtu_sum1.columns[3:]:
                    if data_mbtu_sum1[col].iloc[0] != 0:  # Check to avoid division by zero
                        new_row2[col] = round(data_mbtu_sum1[col].iloc[1] / data_mbtu_sum1[col].iloc[0], 1)
                    elif data_mbtu_sum1[col].iloc[0] == 0 and data_mbtu_sum1[col].iloc[1] == 0:
                        new_row2[col] = '0.0'
                    elif data_mbtu_sum1[col].iloc[0] == 0 and data_mbtu_sum1[col].iloc[1] != 0:
                        new_row2[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row2])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                new_row3 = {
                    'Filename': 'Baseline',  
                    'UNIT': '', 
                    'Meterings': ''
                }
                for col in data_mbtu_sum1.columns[3:]:
                    if data_mbtu_sum1[col].iloc[3] != 0:
                        new_row3[col] = round(data_mbtu_sum1[col].iloc[4] / data_mbtu_sum1[col].iloc[3],1)
                    elif data_mbtu_sum1[col].iloc[3] == 0 and data_mbtu_sum1[col].iloc[4] == 0:
                        new_row3[col] = '0.0'
                    elif data_mbtu_sum1[col].iloc[3] == 0 and data_mbtu_sum1[col].iloc[4] != 0:
                        new_row3[col] = '-'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row3])
                # Concatenate the new row DataFrame with the existing DataFrame
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
    
                new_row4 = {
                    'Filename': '% Difference',  
                    'UNIT': '', 
                    'Meterings': ''
                }
    
                for col in data_mbtu_sum1.columns[3:]:
                    try:
                        # Ensure the values are numeric
                        val_16 = float(data_mbtu_sum1[col].iloc[16])
                        val_15 = float(data_mbtu_sum1[col].iloc[15])
                        
                        if val_16 != 0:
                            new_row4[col] = f'{round((1 - (val_15 / val_16)) * 100, 1)}%'
                        elif val_16 == 0 and val_15 == 0:
                            new_row4[col] = '100.0%'
                        elif val_16 == 0 and val_15 != 0:
                            new_row4[col] = '-'
                    except ValueError:
                        new_row4[col] = 'Invalid data'
                
                # Create a DataFrame from the new row
                new_row_df = pd.DataFrame([new_row4])
                data_mbtu_sum1 = pd.concat([data_mbtu_sum1, new_row_df], ignore_index=True)
                # st.write(data_mbtu_sum1)
                
            ###############################################################################################################
            ################################################## Other Tables ###############################################
            ###############################################################################################################
    
            st.markdown(f"""<h6 style="color:red;">🔴 ENERGY SAVINGS AND DEMAND SAVINGS (in %) </h6>""", unsafe_allow_html=True)
            st.markdown(f"""<h7 style="color:blue;">🔵 kWH & MAX kW</h7>""", unsafe_allow_html=True)
            
            # if empty dataframe then write message in markdown - No KWH & MAX KW data found in the selected data
            if data_kwh_sum.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for kWH & MAX kW.</p>""", unsafe_allow_html=True)
            else:
                st.write(data_kwh_sum)
                
            st.markdown(f"""<h7 style="color:red;">🔴 THERM & MAX THERM/HR</h7>""", unsafe_allow_html=True)
            # if empty dataframe then write message in markdown - No THERM & MAX THERM/HR data found in the selected data
            if data_therm_sum.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for THERM & MAX THERM/HR.</p>""", unsafe_allow_html=True)
            else:
                st.write(data_therm_sum)
            
            st.markdown(f"""<h7 style="color:orange;">🟠 MBTU & MAX MBTU/HR</h7>""", unsafe_allow_html=True)
             # if empty dataframe then write message in markdown - No MBTU & MAX MBTU data found in the selected data
            if data_mbtu_sum.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for MBTU & MAX MBTU/HR.</p>""", unsafe_allow_html=True)
            else:
                st.write(data_mbtu_sum)
    
            ############################################# PSF ###############################################
            
            st.markdown(f"""<h6 style="color:red;">🔴 PS-F TABLE FOR ALL UNITS AND ALL METERS</h6>""", unsafe_allow_html=True)
            st.markdown(f"""<h7 style="color:blue;">🔵 kWH & kW</h7>""", unsafe_allow_html=True)
    
            if data_kwh.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for kWH.</p>""", unsafe_allow_html=True)
                # st.info("No data found for KWH & KW")
            else:
                st.write(data_kwh)
            
            st.markdown(f"""<h7 style="color:red;">🔴 THERM & MAX THERM/HR</h7>""", unsafe_allow_html=True)
            if data_therm.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for THERM & MAX THERM/HR.</p>""", unsafe_allow_html=True)
                # st.info("No data found for THERM & MAX THERM/HR")
            else:
                st.write(data_therm)
    
            st.markdown(f"""<h7 style="color:orange;">🟠 MBTU & MAX MBTU/HR</h7>""", unsafe_allow_html=True)
            if data_mbtu.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for MBTU & MAX MBTU/HR.</p>""", unsafe_allow_html=True)
                # st.info("No data found for MBTU & MAX MBTU/HR")
            else:
                st.write(data_mbtu)
        
        ############################################# LVD ###############################################
        with st.expander("📘 **Envelope Summary**"):
            st.markdown(f"""<h6 style="color:red;">🔴 TABLE HAVING Wall, Roof, Glazing U-Value and WWR </h6>""", unsafe_allow_html=True)
            # The two dfs are lvd_summary_p and lvd_summary_b
            if lvd_summary_p.empty and lvd_summary_b.empty:
                st.markdown("""<p><strong>Note:</strong> No data found for Wall, Roof, Glazing U-Value and WWR.</p>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<h7 style="color:red;">🔵 Proposed and Baseline Table </h7>""", unsafe_allow_html=True)
                data = {
                    "Component": ["Wall", "Roof", "Fenestration", "Fenestration", "Window to Wall Ratio"],
                    "Units": ["U-value (BTU/hr.ft²°F)", "U-value (BTU/hr.ft²°F)", "U-value (BTU/hr.ft²°F)", "SHGC", "%"],
                    "Proposed Design": ["", "", "", "", ""],
                    "Baseline Design": ["", "", "", "", ""]
                }
                df = pd.DataFrame(data)
                for idx, row in df.iterrows():
                    if row["Component"] == "Wall":
                        df.at[idx, "Proposed Design"] = lvd_summary_p[lvd_summary_p["AZIMUTH"] == "ALL WALLS"]["AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"].values[0]
                        df.at[idx, "Baseline Design"] = lvd_summary_b[lvd_summary_b["AZIMUTH"] == "ALL WALLS"]["AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"].values[0]
                    elif row["Component"] == "Roof":
                        df.at[idx, "Proposed Design"] = lvd_summary_p[lvd_summary_p["AZIMUTH"] == "ROOF"]["AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"].values[0]
                        df.at[idx, "Baseline Design"] = lvd_summary_b[lvd_summary_b["AZIMUTH"] == "ROOF"]["AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"].values[0]
                    elif row["Component"] == "Fenestration" and row["Units"] != "SHGC":
                        df.at[idx, "Proposed Design"] = lvd_summary_p[lvd_summary_p["AZIMUTH"] == "ALL WALLS"]["AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)"].values[0]
                        df.at[idx, "Baseline Design"] = lvd_summary_b[lvd_summary_b["AZIMUTH"] == "ALL WALLS"]["AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)"].values[0]
                    elif row["Component"] == "Window to Wall Ratio":
                        # For Proposed Design
                        window_area_p = pd.to_numeric(lvd_summary_p[lvd_summary_p["AZIMUTH"] == "ALL WALLS"]["WINDOW(AREA)(SQFT)"].values[0])
                        window_wall_area_p = pd.to_numeric(lvd_summary_p[lvd_summary_p["AZIMUTH"] == "ALL WALLS"]["WINDOW+WALL(AREA)(SQFT)"].values[0])
                        proposed_percentage = round((window_area_p * 100) / window_wall_area_p, 2)
                        df.at[idx, "Proposed Design"] = f"{proposed_percentage}%"
                    
                        # For Baseline Design
                        window_area_b = pd.to_numeric(lvd_summary_b[lvd_summary_b["AZIMUTH"] == "ALL WALLS"]["WINDOW(AREA)(SQFT)"].values[0])
                        window_wall_area_b = pd.to_numeric(lvd_summary_b[lvd_summary_b["AZIMUTH"] == "ALL WALLS"]["WINDOW+WALL(AREA)(SQFT)"].values[0])
                        baseline_percentage = round((window_area_b * 100) / window_wall_area_b, 2)
                        df.at[idx, "Baseline Design"] = f"{baseline_percentage}%"
                st.dataframe(df)
            
            if prop_data is None or base_data is None:
                st.error("Error: Failed to retrieve simulation data.")
                return
