import pandas as pd
import os
import re

def update_glass(climate_zone_file, amenity_data):
    start_marker = "$Climate Zone"
    end_marker = ".."

    # Read climate data file
    with open(climate_zone_file, 'r') as f:
        data_climate_zone = f.readlines()

    # Extract material data for the specified climate zone
    start_indices = [i for i, line in enumerate(data_climate_zone) if start_marker in line]
    end_indice = [i for i, line in enumerate(data_climate_zone) if end_marker in line]
    end_indices = []
    end_indices.append(end_indice[len(end_indice) - 1])

    # Find material data for the specified climate zone
    material_data = []
    for start_idx, end_idx in zip(start_indices, end_indices):
        material_data += data_climate_zone[start_idx+2:end_idx+1]

    # Finding index where "Window Layers" occur
    window_index = None
    for i, line in enumerate(amenity_data):
        if "Window Layers" in line:
            window_index = i - 3
            break

    # Insert material data before "Window Layers"
    if window_index is not None:
        amenity_data = amenity_data[:window_index] + material_data + amenity_data[window_index:]

    return amenity_data


def update_glass_type(amenity_data):
    start_marker = "Glass Types"
    end_marker = "Window Layers"

    # Extract material data for the specified climate zone
    start_indice = [i for i, line in enumerate(amenity_data) if start_marker in line]
    end_indices = [i for i, line in enumerate(amenity_data) if end_marker in line]
    start_indices = []
    start_indices.append(start_indice[len(start_indice) - 1])

    # Find material data for the specified climate zone
    material_data = []
    for start_idx, end_idx in zip(start_indices, end_indices):
        material_data += amenity_data[start_idx+2:end_idx-1]

    # Assuming material_data is a list of strings
    all_win_value = None
    for line in material_data:
        if "All Win" in line:
            match = re.search(r'"([^"]+)"', line)
            if match:
                all_win_value = match.group(1)
                break  # Assuming there's only one "All Win" line

    if all_win_value is not None:
        ## Paste all_win_value in range "Floors / Spaces / Walls / Windows / Doors" and "Electric & Fuel Meters" ##
        start_marker1 = "Floors / Spaces / Walls / Windows / Doors"
        end_marker1 = "Electric & Fuel Meters"

        # Finding start and end indices
        start_index1 = None
        end_index1 = None

        for i, line in enumerate(amenity_data):
            if start_marker1 in line:
                start_index1 = i
            if end_marker1 in line:
                end_index1 = i
                break

        if start_index1 is not None and end_index1 is not None:
            inside_window = False
            for line_index in range(start_index1 + 3, end_index1 - 4):
                line = amenity_data[line_index]
                if "WINDOW" in line:
                    inside_window = True
                elif inside_window:
                    if ".." in line:
                        inside_window = False
                    elif "GLASS-TYPE" in line:
                        amenity_data[line_index] = re.sub(r'GLASS-TYPE\s*=\s*.*', r'GLASS-TYPE = "{}"'.format(re.escape(all_win_value).replace(r'\ ', ' ').replace('\\', '')), line)

    return amenity_data