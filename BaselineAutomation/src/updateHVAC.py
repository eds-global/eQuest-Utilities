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