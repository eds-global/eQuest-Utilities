import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw 
import re
import streamlit as st
import tempfile
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
import numpy as np

warnings.filterwarnings("ignore")

def get_LVD_Summary(name):
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
            lvd_summ.columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 
                                'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                            'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
            lvd_summ = lvd_summ[pd.to_numeric(lvd_summ['WINDOW+WALL(AREA)(SQFT)'], errors='coerce').notna()]
            
            lvd_summ.index.name = name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            # get the value before '.' in 1st column
            name = name1.rsplit(".", 1)[0]
            # insert into 1st column as RUNNAME
            lvd_summ.insert(0, 'RUNNAME', name) 
            
        return lvd_summ

    except Exception as e:
        columns = ['RUNNAME', 'AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 
                                'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                            'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame(columns=columns)

############################################  SVA ###############################################

def get_SVA_report(name):
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

def generateFenestration(baseline, proposed):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(baseline.read())
        temp_file_path_baseline = temp_file.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(proposed.read())
        temp_file_path_proposed = temp_file.name

    lv_d_proposed = get_LVD_Summary(temp_file_path_proposed)
    lv_d_baseline = get_LVD_Summary(temp_file_path_baseline)
    sv_a_baseline = get_SVA_report(temp_file_path_baseline)
    sv_a_proposed = get_SVA_report(temp_file_path_proposed)
    
    north_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    south_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    east_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'EAST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    west_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'WEST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    north_east_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-EAST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    south_east_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-EAST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    south_west_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-WEST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    north_west_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-WEST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    roof_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ROOF', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    allWalls_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ALL WALLS', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    undergrnd_wind_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'UNDERGRND', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]

    north_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    south_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    east_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'EAST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    west_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'WEST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    north_east_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-EAST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    south_east_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-EAST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    south_west_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-WEST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    north_west_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-WEST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    roof_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ROOF', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    allWalls_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ALL WALLS', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    undergrnd_wall_u = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'UNDERGRND', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]

    north_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH', 'WINDOW(AREA)(SQFT)'].iloc[0]
    south_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH', 'WINDOW(AREA)(SQFT)'].iloc[0]
    east_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'EAST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    west_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'WEST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    north_east_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-EAST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    south_east_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-EAST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    south_west_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-WEST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    north_west_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-WEST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    roof_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ROOF', 'WINDOW(AREA)(SQFT)'].iloc[0]
    allWalls_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ALL WALLS', 'WINDOW(AREA)(SQFT)'].iloc[0]
    undergrnd_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'UNDERGRND', 'WINDOW(AREA)(SQFT)'].iloc[0]
    wall_roof_wind_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'WALLS+ROOFS', 'WINDOW(AREA)(SQFT)'].iloc[0]

    north_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH', 'WALL(AREA)(SQFT)'].iloc[0]
    south_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH', 'WALL(AREA)(SQFT)'].iloc[0]
    east_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'EAST', 'WALL(AREA)(SQFT)'].iloc[0]
    west_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'WEST', 'WALL(AREA)(SQFT)'].iloc[0]
    north_east_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-EAST', 'WALL(AREA)(SQFT)'].iloc[0]
    south_east_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-EAST', 'WALL(AREA)(SQFT)'].iloc[0]
    south_west_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'SOUTH-WEST', 'WALL(AREA)(SQFT)'].iloc[0]
    north_west_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'NORTH-WEST', 'WALL(AREA)(SQFT)'].iloc[0]
    roof_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ROOF', 'WALL(AREA)(SQFT)'].iloc[0]
    allWalls_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'ALL WALLS', 'WALL(AREA)(SQFT)'].iloc[0]
    undergrnd_wall_area = lv_d_baseline.loc[lv_d_baseline['AZIMUTH'] == 'UNDERGRND', 'WALL(AREA)(SQFT)'].iloc[0]

    north_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    south_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    east_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'EAST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    west_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'WEST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    north_east_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH-EAST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    south_east_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH-EAST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    south_west_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH-WEST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    north_west_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH-WEST', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    roof_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'ROOF', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    allWalls_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'ALL WALLS', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]
    undergrnd_wind_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'UNDERGRND', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'].iloc[0]

    north_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    south_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    east_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'EAST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    west_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'WEST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    north_east_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH-EAST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    south_east_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH-EAST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    south_west_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH-WEST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    north_west_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH-WEST', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    roof_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'ROOF', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    allWalls_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'ALL WALLS', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]
    undergrnd_wall_u_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'UNDERGRND', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)'].iloc[0]

    north_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH', 'WINDOW(AREA)(SQFT)'].iloc[0]
    south_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH', 'WINDOW(AREA)(SQFT)'].iloc[0]
    east_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'EAST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    west_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'WEST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    north_east_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH-EAST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    south_east_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH-EAST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    south_west_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'SOUTH-WEST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    north_west_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'NORTH-WEST', 'WINDOW(AREA)(SQFT)'].iloc[0]
    roof_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'ROOF', 'WINDOW(AREA)(SQFT)'].iloc[0]
    allWalls_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'ALL WALLS', 'WINDOW(AREA)(SQFT)'].iloc[0]
    undergrnd_wind_area_p = lv_d_proposed.loc[lv_d_proposed['AZIMUTH'] == 'UNDERGRND', 'WINDOW(AREA)(SQFT)'].iloc[0]

    north_wind_area = float(north_wind_area) + float(north_east_wind_area)
    east_wind_area = float(east_wind_area) + float(south_east_wind_area)
    south_wind_area = float(south_wind_area) + float(south_west_wind_area)
    west_wind_area = float(west_wind_area) + float(north_west_wind_area)
    ag_wind_area = (north_wind_area + east_wind_area + south_wind_area + west_wind_area)

    north_wall_area = float(north_wall_area) + float(north_east_wall_area)
    east_wall_area = float(east_wall_area) + float(south_east_wall_area)
    south_wall_area = float(south_wall_area) + float(south_west_wall_area)
    west_wall_area = float(west_wall_area) + float(north_west_wall_area)
    ag_wall_area = (north_wall_area + east_wall_area + south_wall_area + west_wall_area)

    north_wind_area_p = float(north_wind_area_p) + float(north_east_wind_area_p)
    east_wind_area_p = float(east_wind_area_p) + float(south_east_wind_area_p)
    south_wind_area_p = float(south_wind_area_p) + float(south_west_wind_area_p)
    west_wind_area_p = float(west_wind_area_p) + float(north_west_wind_area_p)
    ag_wind_area_p = (north_wind_area_p + east_wind_area_p + south_wind_area_p + west_wind_area_p)

    columns = pd.MultiIndex.from_tuples([
        ("", "Orientation"),
        ("Baseline", "Above-Grade Wall Area (sq m)"),
        ("Baseline", "Vertical Glazing Area (sq m)"),
        ("Baseline", "Vertical Glazing Area (%)"),
        ("Proposed", "Above-Grade Wall Area (sq m)"),
        ("Proposed", "Vertical Glazing Area (sq m)"),
        ("Proposed", "Vertical Glazing Area (%)"),
    ])

    data = [
        ["North", round(north_wall_area*0.092903,2), round(north_wind_area*0.092903,2), round(round(north_wind_area*0.092903,2)*100/round(north_wall_area*0.092903,2),2), "Identical to baseline", round(north_wind_area_p*0.092903,2), round(round(north_wind_area_p*0.092903,2)*100/round(north_wall_area*0.092903,2),2)],
        ["East", round(east_wall_area*0.092903,2), round(east_wind_area*0.092903,2), round(round(east_wind_area*0.092903,2)*100/round(east_wall_area*0.092903,2),2), "Identical to baseline", round(east_wind_area_p*0.092903,2), round(round(east_wind_area_p*0.092903,2)*100/round(east_wall_area*0.092903,2),2)],
        ["South", round(south_wall_area*0.092903,2), round(south_wind_area*0.092903,2), round(round(south_wind_area*0.092903,2)*100/round(south_wall_area*0.092903,2),2), "Identical to baseline", round(south_wind_area_p*0.092903,2), round(round(south_wind_area_p*0.092903,2)*100/round(south_wall_area*0.092903,2),2)],
        ["West", round(west_wall_area*0.092903,2), round(west_wind_area*0.092903,2), round(round(west_wind_area*0.092903,2)*100/round(west_wall_area*0.092903,2),2), "Identical to baseline", round(west_wind_area_p*0.092903,2), round(round(west_wind_area_p*0.092903,2)*100/round(west_wall_area*0.092903,2),2)],
        ["Total", round(ag_wall_area*0.092903,2), round(ag_wind_area*0.092903,2), round(round(ag_wind_area*0.092903,2)*100/round(ag_wall_area*0.092903,2),2), round(ag_wall_area*0.092903,2), round(ag_wind_area_p*0.092903,2), round(round(ag_wind_area_p*0.092903,2)*100/round(ag_wall_area*0.092903,2),2)],
    ]

    df = pd.DataFrame(data, columns=columns)
    numeric_columns = [
        ("Baseline", "Above-Grade Wall Area (sq m)"),
        ("Baseline", "Vertical Glazing Area (sq m)"),
        ("Baseline", "Vertical Glazing Area (%)"),
        ("Proposed", "Above-Grade Wall Area (sq m)"),
        ("Proposed", "Vertical Glazing Area (sq m)"),
        ("Proposed", "Vertical Glazing Area (%)"),
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.fillna(0, inplace=True)

    df1 = pd.DataFrame(data, columns=columns)
    columns2 = pd.MultiIndex.from_tuples([
        ("", "Roof Area (sq m)"),
        ("", "Skylight Area (sq m)"),
        ("Baseline", "Conditioned"),
        ("Baseline", "Semi-heated"),
        ("Baseline", "Unconditioned"),
        ("Proposed", "Conditioned"),
        ("Proposed", "Semi-heated"),
        ("Proposed", "Unconditioned"),
    ])

    if wall_roof_wind_area != allWalls_wind_area:
        diff_area = wall_roof_wind_area - allWalls_wind_area
    else:
        diff_area = 0
    converted_area = round(float(diff_area) * 0.092903, 2)

    conditioned_count_base = (sv_a_baseline['SUPPLY-FLOW(CFM)'] != 0).sum()
    unconditioned_count_base = (sv_a_baseline['SUPPLY-FLOW(CFM)'] == 0).sum() 
    conditioned_count_pro = (sv_a_proposed['SUPPLY-FLOW(CFM)'] != 0).sum()
    unconditioned_count_pro = (sv_a_proposed['SUPPLY-FLOW(CFM)'] == 0).sum()

    data_row = [
        round(float(roof_wall_area)*0.092903, 2),  # Converted area
        roof_wind_area,                            # Roof window area
        conditioned_count_base,                   # Conditioned base
        "",                                       # Placeholder for condition comparison
        unconditioned_count_base,                 # Unconditioned base
        "", "", ""                                # Remaining placeholders
    ]

    # Fill "Identical to Baseline" if applicable
    if conditioned_count_base == conditioned_count_pro:
        data_row[5] = "Identical to Baseline"

    if unconditioned_count_base == unconditioned_count_pro:
        data_row[7] = "Identical to Baseline"

    data2 = [data_row]

    df2 = pd.DataFrame(data2, columns=columns2)
    st.markdown("""<h6 style="color:red;">🔴 Shading</h6>""", unsafe_allow_html=True)
    st.write("🪷 Above-grade Wall and Glazing")
    st.write(df1)
    if df1['Proposed']['Vertical Glazing Area (%)'][4] < 40.0 or df1['Baseline']['Vertical Glazing Area (%)'][4] < 40:
        st.info("ℹ️ The vertical glazing percentage is below 40%, supporting good thermal performance.")

    st.write("🪷 Roof/Skylight & Thermal Blocks")
    st.write(df2)

    # st.markdown("""<h6 style="color:red;">🔴 Fenestration</h6>""", unsafe_allow_html=True)
    columns = pd.MultiIndex.from_tuples([
        ("General Information", "Building ID"),
        ("General Information", "New or Existing Construction"),
        ("General Information", "Space-Conditioning Category"),
        ("Baseline", "Description"),
        ("Baseline", "Assembly U-factor"),
        ("Baseline", "SHGC"),
        ("Proposed", "Description"),
        ("Proposed", "Assembly U-factor"),
        ("Proposed", "SHGC"),
        ("Proposed", "VLT"),
    ])

    data = [[
        "",  # Building ID
        "",                                # New or Existing Construction
        "",                     # Space-Conditioning Category
        "",            # Baseline Description
        "",                                 # Baseline U-factor
        "",                                 # Baseline SHGC
        "",                                # Proposed Description
        "",                                  # Proposed U-factor
        "",                                 # Proposed SHGC
        ""                                   # Proposed VLT
    ]]
    dfss = pd.DataFrame(data, columns=columns)
    # st.write(dfss)

    # st.markdown("""<h6 style="color:red;">🔴 Fenestration New</h6>""", unsafe_allow_html=True)
    # columns = pd.MultiIndex.from_tuples([
    #     ("General Information", "Building ID"),
    #     ("General Information", "New or Existing Construction"),
    #     ("General Information", "Space-Conditioning Category"),
    #     ("Baseline", "Description"),
    #     ("Baseline", "Assembly U-factor"),
    #     ("Baseline", "SHGC"),
    #     ("Proposed", "Description"),
    #     ("Proposed", "Assembly U-factor"),
    #     ("Proposed", "SHGC"),
    #     ("Proposed", "VLT"),
    # ])

    # data = [[
    #     "Saudi Aramco Corporate Academy -",  # Building ID
    #     "New",                                # New or Existing Construction
    #     "Nonresidential",                     # Space-Conditioning Category
    #     "Nonmetal framing (all)",            # Baseline Description
    #     6.81,                                 # Baseline U-factor
    #     0.25,                                 # Baseline SHGC
    #     "DGU",                                # Proposed Description
    #     1.6,                                  # Proposed U-factor
    #     0.25,                                 # Proposed SHGC
    #     0.5                                   # Proposed VLT
    # ]]
    # dfss = pd.DataFrame(data, columns=columns)
    # st.write(dfss)