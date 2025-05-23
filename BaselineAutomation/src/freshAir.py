import pandas as pd
import re
import ast

def updateFresh(new_df, inp_data):
    # Step 1: Read the input file
    with open(inp_data, 'r', encoding='utf-8', errors='replace') as file:
        inp_data = file.readlines()

    # Step 2: Identify the markers for the "HVAC Systems / Zones" section
    start_marker1 = "HVAC Systems / Zones"
    end_marker1 = "Metering & Misc HVAC"

    # Variables to store the start and end indices of the section
    start_index = None
    end_index = None

    # Loop through the input data to find the start and end indices
    for i, line in enumerate(inp_data):
        if start_marker1 in line:
            start_index = i + 4  # Start index is 4 lines below the start marker
        if end_marker1 in line:
            end_index = i - 2  # End index is 2 lines above the end marker
            break
    
    # Check if both start and end indices were found
    if start_index is not None and end_index is not None:
        # Loop through the lines in the identified section
        for i in range(start_index, end_index + 1):
            line = inp_data[i].strip()
            if "= ZONE" in line:
                zone_name = line.split('=', 1)[0].strip().strip('"')

                end_of_zone_index = None
                # Find the end of the current zone section
                for k in range(i + 1, end_index):
                    zone_line = inp_data[k]
                    if ".." in zone_line:
                        end_of_zone_index = k
                        break
                # If no ".." found, this zone is the last in the section
                if end_of_zone_index is None:
                    end_of_zone_index = end_index
                
                # Check if the ZONE name matches any row in the new_df dataframe
                matched_row = new_df[new_df['ZONE'] == zone_name]
                
                # If a matching row was found in the dataframe
                if not matched_row.empty:
                    # Get the OUTSIDE-AIR-FLOW value from the dataframe
                    outside_air_flow_value = matched_row['OUTSIDE-AIR-FLOW'].values[0]

                    # Check if OUTSIDE-AIR-FLOW already exists in the zone section
                    outside_air_flow_found = False
                    for j in range(i, end_of_zone_index):
                        if "OUTSIDE-AIR-FLOW" in inp_data[j]:
                            # Update the existing OUTSIDE-AIR-FLOW value using regular expression substitution
                            inp_data[j] = re.sub(r'OUTSIDE-AIR-FLOW\s*=\s*(.*?)$', f'OUTSIDE-AIR-FLOW = {outside_air_flow_value}', inp_data[j])
                            outside_air_flow_found = True
                            break
                    
                    # If OUTSIDE-AIR-FLOW was not found, insert it before the next ".." line
                    if not outside_air_flow_found:
                        inp_data.insert(end_of_zone_index, f'   OUTSIDE-AIR-FLOW = {outside_air_flow_value}\n')

    return inp_data

def remove_OAs(inp_data):
    # Step 2: Identify the markers for the "HVAC Systems / Zones" section
    start_marker = "HVAC Systems / Zones"
    end_marker = "Metering & Misc HVAC"

    # Variables to store the start and end indices of the section
    start_index = None
    end_index = None

    # Loop through the input data to find the start and end indices
    for i, line in enumerate(inp_data):
        if start_marker in line:
            start_index = i + 4  # Start index is 4 lines below the start marker
        if end_marker in line:
            end_index = i - 2  # End index is 2 lines above the end marker
            break
    
    # Print start and end indices for debugging
    print(start_index, end_index)

    # Check if we found both markers
    if start_index is None or end_index is None:
        return inp_data

    # Initialize a variable to store the cleaned data
    cleaned_data = inp_data[:start_index]

    # Define the OA markers to be removed
    oa_markers = ["OA FLOW/PERSON", "OA-FLOW/PER", "OA FLOW/AREA", "OA CHANGES"]

    # Process the lines within the identified section
    inside_zone = False
    for i in range(start_index, end_index + 1):
        line = inp_data[i]

        if line.strip().endswith('= ZONE'):
            inside_zone = True
            zone_start_index = i
            zone_lines = [line]
        elif inside_zone and line.strip() == "..":
            inside_zone = False
            # Add the zone end marker
            zone_lines.append(line)

            # Filter out lines containing any of the OA markers
            filtered_zone_lines = [l for l in zone_lines if not any(marker in l for marker in oa_markers)]
            cleaned_data.extend(filtered_zone_lines)
        elif inside_zone:
            zone_lines.append(line)
        else:
            cleaned_data.append(line)

    # Add the remaining lines after the end index
    cleaned_data.extend(inp_data[end_index + 1:])

    return cleaned_data
