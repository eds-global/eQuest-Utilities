import pandas as pd
import re
import ast

def updateBCVentilation(zone_space_df, inp_data, sim_data):
    # Calculate Total People and Total Area from LV-B report
    with open(sim_data, 'r', encoding='utf-8', errors='replace') as file:
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

        lvb_df = lvb_df[['SPACE', 'PEOPLE', 'AREA(SQFT)']]
        
        # convert below columns of lvb_df to numeric datatypes
        lvb_df['AREA(SQFT)'] = pd.to_numeric(lvb_df['AREA(SQFT)'])
        lvb_df['PEOPLE'] = pd.to_numeric(lvb_df['PEOPLE'])
        
        

    ############################################# NOW INP FILE ################################################
    with open(inp_data, 'r', encoding='utf-8', errors='replace') as file:
        inp_data = file.readlines()
        
    # C-ACTIVITY-DESC
    start_marker = "Floors / Spaces / Walls / Windows / Doors"
    end_marker = "Electric & Fuel Meters"

    # Finding start and end indices in data
    start_index = None
    end_index = None

    # Loop through each line of the input data to find the start and end indices
    for i, line in enumerate(inp_data):
        if start_marker in line:
            start_index = i + 4  # Start index is 4 lines below the start marker
        if end_marker in line:
            end_index = i - 4  # End index is 4 lines above the end marker
            break

     # Extract the relevant section
    relevant_section = inp_data[start_index:end_index]
    
    # Initialize lists to store SPACE and C-ACTIVITY-DESC values
    spaces = []
    activity_descs = []
    
    # Initialize variables to hold current SPACE and C-ACTIVITY-DESC
    current_space = None
    current_activity_desc = None
    
    # Parse the relevant section
    for line in relevant_section:
        line = line.strip()
        if line.startswith('"') and '=' in line:
            if current_space and current_activity_desc:
                spaces.append(current_space)
                activity_descs.append(current_activity_desc)
            current_space = line.split('=', 1)[0].strip().strip('"')
            current_activity_desc = None
        elif 'C-ACTIVITY-DESC' in line:
            current_activity_desc = line.split('=', 1)[1].strip().strip('*')
        elif line == '..':
            if current_space and current_activity_desc:
                spaces.append(current_space)
                activity_descs.append(current_activity_desc)
                current_space = None
                current_activity_desc = None
    
    # Append the last space and activity description if present
    if current_space and current_activity_desc:
        spaces.append(current_space)
        activity_descs.append(current_activity_desc)
    
    # Create the DataFrame
    inp_df = pd.DataFrame({
        'SPACE': spaces,
        'C-ACTIVITY-DESC': activity_descs
    })
     
    ################################################## MERGE WITH  CSVs ##############################################
    # Merge the DataFrames on the 'SPACE' column
    merged_df = pd.merge(lvb_df, inp_df, on='SPACE', how='inner')
    csv_df = pd.read_csv('database/eQUEST_database.csv')

    # Clean and prepare the columns for merging
    merged_df['C-ACTIVITY-DESC'] = merged_df['C-ACTIVITY-DESC'].str.strip().str.lower()
    csv_df['Activity Description_eQUEST'] = csv_df['Activity Description_eQUEST'].str.strip().str.lower()

    # Merge the DataFrames on the matching activity description columns
    final_df = pd.merge(merged_df, csv_df, left_on='C-ACTIVITY-DESC', right_on='Activity Description_eQUEST', how='left')

    # Select relevant columns from the merged DataFrame
    final_df = final_df[['SPACE', 'PEOPLE', 'AREA(SQFT)', 'C-ACTIVITY-DESC', 'Fresh air per person (CFM/person)', 'Fresh air per area (CFM/sqft)']]
    # Calculate the OUTSIDE-AIR-FLOW
    final_df['OUTSIDE-AIR-FLOW'] = (final_df['PEOPLE'] * final_df['Fresh air per person (CFM/person)'] + final_df['AREA(SQFT)'] * final_df['Fresh air per area (CFM/sqft)']).round(2)
    # print(final_df)
    # print(zone_space_df)
    new_df = pd.merge(final_df, zone_space_df, on='SPACE', how='inner')

    return new_df

    #################################################################################################################################

    # # Variables to store the start and end indices of the section
    # start_index1 = 0
    # end_index1 = len(inp_data) - 1
    
    # # Check if both start and end indices were found
    # if start_index1 is not None and end_index1 is not None:
    #     # Loop through the lines in the identified section
    #     for i in range(start_index1, end_index1 + 1):
    #         line = inp_data[i].strip()
    #         if "= ZONE" in line and "= SYSTEM" not in line:
    #             zone_name = line.split('=')[0].strip()
    #             print(line)

    #             end_of_zone_index = None
    #             # Find the end of the current zone section
    #             for k in range(i + 1, end_index1):
    #                 zone_line = inp_data[k]
    #                 if ".." in zone_line:
    #                     end_of_zone_index = k
    #                     break

    #             # If no ".." found, this zone is the last in the section
    #             if end_of_zone_index is None:
    #                 end_of_zone_index = end_index1
                
    #             # Check if the ZONE name matches any row in the new_df dataframe
    #             matched_row = new_df[new_df['ZONE'] == zone_name]
                
    #             # If a matching row was found in the dataframe
    #             if not matched_row.empty:
    #                 # Get the OUTSIDE-AIR-FLOW value from the dataframe
    #                 outside_air_flow_value = matched_row['OUTSIDE-AIR-FLOW'].values[0]

    #                 # Check if OUTSIDE-AIR-FLOW already exists in the zone section
    #                 outside_air_flow_found = False
    #                 for j in range(i, end_of_zone_index):
    #                     if "OUTSIDE-AIR-FLOW" in inp_data[j]:
    #                         # Update the existing OUTSIDE-AIR-FLOW value using regular expression substitution
    #                         inp_data[j] = re.sub(r'OUTSIDE-AIR-FLOW\s*=\s*(.*?)$', f'OUTSIDE-AIR-FLOW = {outside_air_flow_value}', inp_data[j])
    #                         outside_air_flow_found = True
    #                         break
                    
    #                 # If OUTSIDE-AIR-FLOW was not found, insert it before the next ".." line
    #                 if not outside_air_flow_found:
    #                     inp_data.insert(end_of_zone_index, f'   OUTSIDE-AIR-FLOW = {outside_air_flow_value}')
                    
    # return inp_data
