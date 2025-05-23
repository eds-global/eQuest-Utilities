import json
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_climate_path(climate_zone, building_type):
    config_path = resource_path('config.json')
    # print(f"Config path: {config_path}")
    try:
        with open(config_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found at: {config_path}")
        sys.exit(1)

    for entry in data:
        if entry['climate'] == str(climate_zone):
            if building_type == 1:
                return resource_path(entry['construction_library_path'])
            elif building_type == 0:
                return resource_path(entry['construction_library_path_residential'])
    return None

def get_system_path(building_type, heat_type, area, floor):
    area = int(area)
    floor = int(floor)
    
    config_path = resource_path('config.json')
    # print(f"Config path: {config_path}")
    try:
        with open(config_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found at: {config_path}")
        sys.exit(1)

    # Extracting paths of construction_library_systems
    construction_library_systems_paths = [entry["construction_library_systems"] for entry in data]

    # Find the entry with the specified climate zone
    if building_type == 0: # residential
        if heat_type == 0: # Hybrid/Fossil
            return construction_library_systems_paths[0] # 1
        else: # Electric
            return construction_library_systems_paths[1] # 2
            
    elif building_type == 1:
        if area <= 25000 and floor <= 3:
            if heat_type == 0:
                return construction_library_systems_paths[2] # 3
            else:
                return construction_library_systems_paths[3] # 4
        elif area > 25000 and area < 150000: # Building type 1 with area less than 150000
            if floor <= 5:
                if heat_type == 0:
                    return construction_library_systems_paths[4] # 5
                else:
                    return construction_library_systems_paths[5] # 6
        elif area<= 25000:
            if floor == 4 or floor == 5: # Additional condition for floor 4 or 5
                if heat_type == 0:
                    return construction_library_systems_paths[4] # 5
                else:
                    return construction_library_systems_paths[5] # 6
        else: # Building type 1 with area greater than or equal to 150000
            if floor > 5:
                if heat_type == 0:
                    return construction_library_systems_paths[6] # 7
                else:
                    return construction_library_systems_paths[7] # 8
            else:
                if heat_type == 0:
                    return construction_library_systems_paths[6] # 7
                else:
                    return construction_library_systems_paths[7] # 8
                

    # If the climate zone is not found, return None
    return None

# function to insert matarials, layers and construction at specific position
def insert_material_data(climate_zone_file, amenity_data):
    start_marker1 = "= MATERIAL"
    end_marker1 = ".."

    with open(climate_zone_file, 'r') as file:
        data_climate_zone = file.readlines()

    # Finding start and end indices
    start_indices1 = [i for i, line in enumerate(data_climate_zone) if start_marker1 in line]
    end_indice1 = [i for i, line in enumerate(data_climate_zone) if end_marker1 in line]
    end_indices1 = []
    for i in range(0, len(start_indices1)):
        end_indices1.append(end_indice1[i])

    # with open(amenity_file, 'r') as file:
    #     amenity_data = file.readlines()

    layer_index = None

    # Finding index where "= LAYERS" occur
    for i, line in enumerate(amenity_data):
        if "= LAYERS" in line:
            layer_index = i
            break

    # Writing extracted data to Amenity_PC v26.inp
    if layer_index is not None:
        for start_idx, end_idx in zip(start_indices1, end_indices1):
            material_data = data_climate_zone[start_idx:end_idx+1]  # Including the end marker line
            amenity_data = amenity_data[:layer_index] + material_data + amenity_data[layer_index:]
            
    return amenity_data


def insert_layers_data(climate_zone_file, mat_data):
    start_marker2 = "= LAYERS"
    strt_mrk1 = "TYPE             = LAYERS"
    end_marker2 = ".."

    with open(climate_zone_file, 'r') as file:
        data_climate_zone = file.readlines()

    # Finding start and end indices
    start_indices2 = [i for i, line in enumerate(data_climate_zone) if start_marker2 in line and strt_mrk1 not in line]
    end_indice2 = [i for i, line in enumerate(data_climate_zone) if end_marker2 in line]
    end_indicee2 = [x for x in end_indice2 if x > start_indices2[0]]
    
    end_indices2 = []
    for i in range(0, len(start_indices2)):
        end_indices2.append(end_indicee2[i])

    construction_index = None

    # Finding index where "= LAYERS" occur
    for i, line in enumerate(mat_data):
        if "= CONSTRUCTION" in line:
            construction_index = i
            break  

    # If "= CONSTRUCTION" is not found, insert at the end of the file
    if construction_index is None:
        construction_index = len(mat_data)
    else:
        # Writing extracted data to Amenity_PC v26.inp
        for start_idx, end_idx in zip(start_indices2, end_indices2):
            layer_data = data_climate_zone[start_idx:end_idx+1]  # Including the end marker line
            mat_data = mat_data[:construction_index] + layer_data + mat_data[construction_index:]
            
    return mat_data


def insert_const_data(climate_zone_file, lyr_data):
    start_marker3 = "= CONSTRUCTION"
    end_marker3 = ".."
    
    with open(climate_zone_file, 'r') as file:
        data_climate_zone = file.readlines()

    # Finding start and end indices
    start_indices3 = [i for i, line in enumerate(data_climate_zone) if start_marker3 in line]
    end_indices3 = [i for i, line in enumerate(data_climate_zone) if end_marker3 in line and i > start_indices3[0]]

    construction_index = None

    # Finding index where "Glass Type Codes" occur
    for i, line in enumerate(lyr_data):
        if "Glass Type Codes" in line:
            construction_index = i - 2
            break

    # If "Glass Type Codes" is not found, insert at the end of the file
    if construction_index is None:
        construction_index = len(lyr_data)

    # Collecting the material data to be inserted
    material_data = []
    for start_idx, end_idx in zip(start_indices3, end_indices3):
        material_data.extend(data_climate_zone[start_idx:end_idx+1])  # Including the end marker line

    # Inserting the material data into lyr_data before "Glass Type Codes"
    lyr_data = lyr_data[:construction_index] + material_data + lyr_data[construction_index:]

    return lyr_data
