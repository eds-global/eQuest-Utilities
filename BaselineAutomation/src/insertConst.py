import pandas as pd
import os
import re

# function to update Construction wall under external-wall and under underground section
def update_external_wall_roof_undergrnd(data):
    start_marker = "Floors / Spaces / Walls / Windows / Doors"
    end_marker = "Electric & Fuel Meters"

    # Finding start and end indices
    start_index = None
    end_index = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i
        if end_marker in line:
            end_index = i
            break

    value_before_equal_wall = None
    value_before_equal_roof = None
    value_before_equal_under = None

    for line in data:
        if "BL Wall" in line:
            index = line.find('=')
            if index != -1:
                value_before_equal_wall = line[:index].strip()
        elif "BL Roof" in line:
            index = line.find('=')
            if index != -1:
                value_before_equal_roof = line[:index].strip()
        elif "Undergrd W" in line:
            index = line.find('=')
            if index != -1:
                value_before_equal_under = line[:index].strip()

    if start_index is not None and end_index is not None:
        inside_exterior_wall = False
        inside_underground_wall = False
        inside_exterior_wall1 = False

        for line_index in range(start_index + 3, end_index - 4):
            line = data[line_index]

            if "EXTERIOR-WALL" in line:
                inside_exterior_wall = True
                inside_underground_wall = False
                inside_exterior_wall1 = True
        
            elif "UNDERGROUND-WALL" in line:
                inside_underground_wall = True
                inside_exterior_wall = False
                inside_exterior_wall1 = False
            
            elif inside_exterior_wall:
                if ".." in line:
                    inside_exterior_wall = False
                elif "CONSTRUCTION" in line:
                    construction_value = re.search(r'CONSTRUCTION\s*=\s*(\S+)', line).group(1)
                    if "TOP" not in construction_value:
                        data[line_index] = re.sub(r'CONSTRUCTION\s*=\s*(\S+)', r'CONSTRUCTION     = {}'.format(value_before_equal_wall), line)
                    elif "TOP" in construction_value:
                        data[line_index] = re.sub(r'CONSTRUCTION\s*=\s*(\S+)', r'CONSTRUCTION     = {}'.format(value_before_equal_roof), line)
            
            elif inside_underground_wall:
                if ".." in line:
                    inside_underground_wall = False
                elif "CONSTRUCTION" in line:
                    if "BOTTOM" not in data[line_index + 1]:
                        data[line_index] = '   CONSTRUCTION     = {}\n'.format(value_before_equal_under)

    return data