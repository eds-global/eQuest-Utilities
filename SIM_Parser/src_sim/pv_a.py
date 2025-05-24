import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw # Xlwings is a Python library that makes it easy to call Python from Excel

warnings.filterwarnings("ignore")

def get_PVA_report(name):
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
        columns = ['RUNNAME', 'HEATING_CAPACITY(MBTU/HR)', 'COOLING_CAPACITY(MBTU/HR)', 'LOOP_FLOW(GAL/MIN)',
                   'TOTAL_HEAD(FT)', 'SUPPLY_UA PRODUCT(BTU/HR-F)', 'SUPPLY_LOSS_DT(F)',
                   'RETURN_UA PRODUCT(BTU/HR-F)', 'RETURN_LOSS_DT(F)', 'LOOP_VOLUME(GAL)', 'FLUID_HEAT(CAPACITY)(BTU/LB-F)']
        return pd.DataFrame(columns=columns)
