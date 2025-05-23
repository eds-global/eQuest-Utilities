import pandas as pd
import os
import re

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
        elif "Undergrd W" in line:
            index = line.find('=')
            if index != -1:
                value_before_equal_under = line[:index].strip()
        elif "BL Roof" in line:
            index = line.find('=')
            if index != -1:
                value_before_equal_roof = line[:index].strip()

    if start_index is not None and end_index is not None:
        inside_exterior_wall = False
        inside_underground_wall = False

        for line_index in range(start_index + 3, end_index - 4):
            line = data[line_index]

            if "EXTERIOR-WALL" in line:
                inside_exterior_wall = True
                inside_underground_wall = False
        
            elif "UNDERGROUND-WALL" in line:
                inside_underground_wall = True
                inside_exterior_wall = False
            
            elif inside_exterior_wall:
                if ".." in line:
                    inside_exterior_wall = False
                elif "CONSTRUCTION" in line:
                    if "extroof" in line:
                        if value_before_equal_roof is not None:
                            data[line_index] = re.sub(r'CONSTRUCTION\s*=\s*".*?"', 'CONSTRUCTION     = {}'.format(value_before_equal_roof), line)
                    else:
                        if "LOCATION" in data[line_index + 1] and "TOP" in data[line_index + 1]:
                            if value_before_equal_roof is not None:
                                data[line_index] = re.sub(r'CONSTRUCTION\s*=\s*".*?"', 'CONSTRUCTION     = {}'.format(value_before_equal_roof), line)
                        else:
                            if value_before_equal_wall is not None:
                                data[line_index] = re.sub(r'CONSTRUCTION\s*=\s*".*?"', 'CONSTRUCTION     = {}'.format(value_before_equal_wall), line)

            elif inside_underground_wall:
                if ".." in line:
                    inside_underground_wall = False
                elif "CONSTRUCTION" in line:
                    if "BOTTOM" not in data[line_index + 1]:
                        if value_before_equal_under is not None:
                            data[line_index] = re.sub(r'CONSTRUCTION\s*=\s*".*?"', 'CONSTRUCTION     = {}'.format(value_before_equal_under), line)

    return data
