import pandas as pd
import re
import ast

def updateBCVentilation(inp_data, sim_data):
    # Calculate Total People and Total Area from LV-B report
    with open(sim_data, 'r') as file:
        sim = file.readlines()

        # Initialize an empty list to store line numbers where 'LV-B' occurs
        lvb_count = [] 
        # Iterate through each line in flist along with its line number
        for num, line in enumerate(sim, 0):
            # If 'LV-B' is in the line, append its line number to lvb_count list
            if 'LV-B' in line:
                lvb_count.append(num)
            # If 'LV-C' is in the line, store its line number as numend
            if 'LV-C' in line:
                numend = num
        # Store the line number of the first occurrence of 'LV-B'
        numstart = lvb_count[0] 
        # Slice flist from the start of 'LV-B' to the line before 'LV-C' and store it in lvb_rpt
        lvb_rpt = sim[numstart:numend]

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
                             'LIGHTS(WATT / SQFT)', 'PEOPLE', 'EQUIP(WATT / SQFT)', 'INFILTRATION_METHOD', 'ACH',
                             'AREA(SQFT)', 'VOLUME(CUFT)']
        
        # convert below columns of lvb_df to numeric datatypes
        lvb_df['AREA(SQFT)'] = pd.to_numeric(lvb_df['AREA(SQFT)'])
        lvb_df['VOLUME(CUFT)'] = pd.to_numeric(lvb_df['VOLUME(CUFT)'])
        lvb_df['SPACE*FLOOR'] = pd.to_numeric(lvb_df['SPACE*FLOOR'])
        lvb_df['LIGHTS(WATT / SQFT)'] = pd.to_numeric(lvb_df['LIGHTS(WATT / SQFT)'])
        lvb_df['EQUIP(WATT / SQFT)'] = pd.to_numeric(lvb_df['EQUIP(WATT / SQFT)'])
        lvb_df['PEOPLE'] = pd.to_numeric(lvb_df['PEOPLE'])

        total_area = lvb_df['AREA(SQFT)'].sum()
        total_people = lvb_df['PEOPLE'].sum()

    print(total_area, total_people)

    ############################################# NOW INP FILE ################################################
    # C-ACTIVITY-DESC
    start_marker = "Floors / Spaces / Walls / Windows / Doors"
    end_marker = "Electric & Fuel Meters"

    # Conditioned or UnConditioned Zone
    start_marker1 = "HVAC Systems / Zones"
    end_marker1 = "Metering & Misc HVAC"

    # Finding start and end indices in data
    start_index = None
    end_index = None

    start_index1 = None
    end_index1 = None

    # Loop through each line of the input data to find the start and end indices
    for i, line in enumerate(inp_data):
        if start_marker in line:
            start_index = i + 4  # Start index is 4 lines below the start marker
        if end_marker in line:
            end_index = i - 4  # End index is 4 lines above the end marker
            break

    for i, line in enumerate(inp_data):
        if start_marker1 in line:
            start_index1 = i + 4  # Start index is 4 lines below the start marker
        if end_marker1 in line:
            end_index1 = i - 4  # End index is 4 lines above the end marker
            break

    if start_index1 is not None and end_index1 is not None:
        for i in range(start_index1, end_index1 - 1):
            if "= ZONE" in inp_data[i] and "= CONDITIONED" in inp_data[i + 1]:
                zone_name = re.search(r'"(.*?)"', inp_data[i]).group(1)
                # Find the end of the zone section
                end_of_zone_index = None
                for k in range(i + 1, end_index1 - 1):
                    if ".." in inp_data[k]:
                        end_of_zone_index = k
                        break
                # Now, within the zone section, search for "OUTSIDE-AIR-FLOW"
                if end_of_zone_index:
                    for j in range(i, end_of_zone_index):
                        if "OUTSIDE-AIR-FLOW" in inp_data[j]:
                            # print("Debugging: ", inp_data[j])  # Debugging output
                            current_value_match = re.search(r'OUTSIDE-AIR-FLOW\s*=\s*(.*?)$', inp_data[j])
                            if current_value_match:
                                current_value = current_value_match.group(1).strip()
                                # Check if the value is enclosed within curly braces
                                if "{" in current_value and "}" in current_value:
                                    try:
                                        # Evaluate the arithmetic expression
                                        expression = current_value.strip('{}')
                                        parts = expression.split('+')
                                        result = 0
                                        for part in parts:
                                            if '*' in part:
                                                factors = part.split('*')
                                                product = 1
                                                for factor in factors:
                                                    product *= float(factor)
                                                result += product
                                            else:
                                                result += float(part)
                                        new_value = result
                                    except ValueError:
                                        print("Error: Invalid arithmetic expression inside curly braces.")
                                        continue
                                else:
                                    # Directly take the number as the new value
                                    try:
                                        new_value = float(current_value)
                                    except ValueError:
                                        print("Error: Invalid numeric value.")
                                        continue
                                # Perform arithmetic operations
                                new_value = new_value * total_area + new_value * total_people
                                # Format the new value to have 2 decimal places
                                new_value_str = "{:.2f}".format(new_value)
                                # Replace the original string with the new value
                                inp_data[j] = re.sub(r'OUTSIDE-AIR-FLOW\s*=\s*(.*?)$', f'OUTSIDE-AIR-FLOW = {new_value_str}', inp_data[j])
                            else:
                                print("No match found for OUTSIDE-AIR-FLOW pattern.")

    return inp_data