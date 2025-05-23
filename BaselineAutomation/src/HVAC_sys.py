def HVAC_Modification(data):
    start_marker = "Pumps"
    end_marker = "HVAC Systems / Zones"

    start_marker1 = "HVAC Systems / Zones"
    end_marker1 = "Metering & Misc HVAC"

    # Finding start and end indices
    start_index = None
    end_index = None

    start_index1 = None
    end_index1 = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i
        if end_marker in line:
            end_index = i
            break

    for i, line in enumerate(data):
        if start_marker1 in line:
            start_index1 = i
        if end_marker1 in line:
            end_index1 = i
            break

    if start_index is not None and end_index is not None:
        # Update lines within the specified range
        for i in range(start_index, end_index):
            if "=" in data[i] or ".." in data[i]:
                data[i] = ""  # Remove line if it doesn't contain "$"

    if start_index1 is not None and end_index1 is not None:
        # Update lines within the specified range
        for i in range(start_index1, end_index1):
            if "= SYSTEM" in data[i]:
                while ".." not in data[i]:
                    data[i] = ""  # Remove line until ".." is encountered
                    i += 1  # Move to the next line
                data[i] = ""  # Remove the line containing ".." as well
    return data

def systems(data, system_dataa):
    start_marker = "Pumps"
    end_marker = "HVAC Systems / Zones"

    with open(system_dataa, 'r') as file:
        system_data = file.readlines()
    
    # Finding start and end indices
    start_index = None
    end_index = None
    
    for i, line in enumerate(system_data):
        if start_marker in line:
            start_index = i + 3
        if end_marker in line:
            end_index = i - 4
            break
    
    for i, line in enumerate(data):
        if start_marker in line:
            start_index1 = i + 3
        if end_marker in line:
            end_index1 = i - 4
            break

    if start_index is not None and end_index is not None:
        extracted_data = system_data[start_index:end_index]
        data[start_index1+1:end_index1] = extracted_data

    return data

def modify_conditioned(data, system_data):
    start_marker = "HVAC Systems / Zones"
    end_marker = "Metering & Misc HVAC"

    start_marker1 = "= SYSTEM"
    end_marker1 = ".."

    with open(system_data, 'r') as file:
        system_data_lines = file.readlines()

    # Finding start and end indices in system_data
    start_index1 = None
    end_index1 = None

    for i, line in enumerate(system_data_lines):
        if start_marker1 in line:
            start_index1 = i
        if end_marker1 in line:
            end_index1 = i + 1

    extracted_data = system_data_lines[start_index1:end_index1]

    # Finding start and end indices in data
    start_index = None
    end_index = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i + 4
        if end_marker in line:
            end_index = i - 4
            break

    record_index = []
    if start_index is not None and end_index is not None:
        for i in range(start_index, end_index - 1):
            if "= ZONE" in data[i] and "= CONDITIONED" in data[i + 1]:
                # Find the index of the line before "= ZONE" line
                insert_index = i
                record_index.append(insert_index)

    for i in range(len(record_index)-1, -1, -1):
        x= record_index[i]
        
        system_text = ""
        for line in extracted_data:
            if "= SYSTEM" in line:
                system_text += "\"HVAC SYSTEM " + str(i+1) + "\" = SYSTEM  \n"
            else:
                system_text += line 
        data[x] = "\n" + system_text +"\n" + data[x]
    return data

def modify_floor(data, system_data):
    start_marker = "HVAC Systems / Zones"
    end_marker = "Metering & Misc HVAC"

    start_marker1 = "= SYSTEM"
    end_marker1 = ".."

    with open(system_data, 'r') as file:
        system_data_lines = file.readlines()

    # Finding start and end indices in system_data
    start_index1 = None
    end_index1 = None

    for i, line in enumerate(system_data_lines):
        if start_marker1 in line:
            start_index1 = i
        if end_marker1 in line:
            end_index1 = i + 1

    extracted_data = system_data_lines[start_index1:end_index1]

    # Finding start and end indices in data
    start_index = None
    end_index = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i + 4
        if end_marker in line:
            end_index = i - 4
            break

    zone_list = []
    zone_dict = {}
    for i in range(start_index, end_index):
        line = data[i].strip()  # Remove leading and trailing whitespaces
        if "= ZONE" in line:
            zone_id = line[1:4]  # Extract the first 2 characters
            zone_object_data = ""
            j = i  # Start from the current line
            while j < end_index and data[j].strip() != "..":  # Continue till ".." is encountered or reach end_index
                zone_object_data += data[j]
                j += 1
            if j < end_index:
                zone_object_data += data[j]
            # print(zone_object_data)  # Add debug print statement
            if zone_id in zone_dict:
                zone_dict[zone_id] += zone_object_data
            else:
                zone_dict[zone_id] = zone_object_data
            zone_list.append(zone_id)

    # Remove duplicates from zone_list
    zone_list = list(set(zone_list))

    if start_index is not None and end_index is not None:
        del data[start_index:end_index+1]

    # Insert zone_dict values into data list
    for zone_id in zone_list:
        data.insert(start_index, zone_dict[zone_id])
        start_index += 1
    
    for i, line in enumerate(data):
        if start_marker in line:
            start_index2 = i + 4
        if end_marker in line:
            end_index2 = i - 4
            break 

    j = 0
    record_index = []
    for i in range(start_index2, end_index2 + 1):
        if "= ZONE" in data[i] and j < len(zone_list) and zone_list[j] in data[i]:
            insert_index = i
            record_index.append(insert_index)
            j += 1
    
    # Insert 
    for i in range(len(record_index) - 1, -1, -1):
        x = record_index[i]
        system_text = ""
        for line in extracted_data:
            if "= SYSTEM" in line:
                system_text += "\"HVAC SYSTEM " + str(i + 1) + "\" = SYSTEM  \n"
            else:
                system_text += line 
        data[x] = "\n" + system_text +"\n" + data[x]

    return data
