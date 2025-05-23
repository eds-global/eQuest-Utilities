import pandas as pd

def zoneSpace(file_path):
    # Step 1: Read the input file
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        inp_data = file.readlines()

    # Step 2: Identify the markers for the "HVAC Systems / Zones" section
    start_marker1 = "HVAC Systems / Zones"
    end_marker1 = "Metering & Misc HVAC"

    # Variables to store the start and end indices of the section
    start_index1 = None
    end_index1 = None

    # Loop through the input data to find the start and end indices
    for i, line in enumerate(inp_data):
        if start_marker1 in line:
            start_index1 = i + 4  # Start index is 4 lines below the start marker
        if end_marker1 in line:
            end_index1 = i - 2  # End index is 2 lines above the end marker
            break

    # Extract the relevant section
    relevant_section1 = inp_data[start_index1:end_index1]

    # Initialize lists to store SPACE and ZONE values
    spaces = []
    zones = []
    current_zone = None

    # Flag to track if we are inside a ZONE section
    inside_zone = False

    # Step 3: Parse the relevant section
    for line in relevant_section1:
        line = line.strip()
        if line.startswith('"') and '=' in line:
            # Extract the ZONE name
            current_zone = line.split('=', 1)[0].strip().strip('"')
            # Set the flag indicating we are inside a ZONE section
            inside_zone = True
        elif 'SPACE' in line and inside_zone:
            # Extract the SPACE information
            current_space = line.split('=', 1)[1].strip().strip('"')
            # Append the SPACE and ZONE information to the lists
            spaces.append(current_space)
            zones.append(current_zone)
        elif line == '..' and inside_zone:
            # Reset the current_zone and current_space variables
            current_zone = None
            current_space = None
            # Reset the flag since we're exiting the ZONE section
            inside_zone = False

    # Step 4: Create the DataFrame
    inp_df1 = pd.DataFrame({
        'ZONE': zones,
        'SPACE': spaces
    })

    return inp_df1
