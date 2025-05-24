import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw # Xlwings is a Python library that makes it easy to call Python from Excel
import numpy as np

warnings.filterwarnings("ignore")

def get_conditionedAboveArea(sva_df):
    conditionedAbove_Area = 0
    sys = sva_df['SYSTEM_TYPE'].to_list()
    for i in range(0, len(sva_df['SYSTEM_TYPE'])):
        if(sys[i] != 'SUM'):
            conditionedAbove_Area = conditionedAbove_Area + sva_df['FLOOR_AREA'][i]
        # else:
        #     UnconditionedAbove_Area = UnconditionedAbove_Area + sva_df['FLOOR_AREA'][i]
    return conditionedAbove_Area

def get_UnconditionedAboveArea(sva_df):
    UnconditionedAbove_Area = 0
    sys = sva_df['SYSTEM_TYPE'].to_list()
    for i in range(0, len(sva_df['SYSTEM_TYPE'])):
        if(sys[i] == 'SUM'):
            UnconditionedAbove_Area = UnconditionedAbove_Area + sva_df['FLOOR_AREA'][i]
        # else:
        #     UnconditionedAbove_Area = UnconditionedAbove_Area + sva_df['FLOOR_AREA'][i]
    return UnconditionedAbove_Area

def get_SVA_Zone_report(name):
    try:
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
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame()
