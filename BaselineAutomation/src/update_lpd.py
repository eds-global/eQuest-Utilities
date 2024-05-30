import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def preprocess_activity_desc(activity_desc):
    # Remove asterisks, extra spaces, and equals sign
    return activity_desc.replace('*', '').replace('=', '').strip()

def preprocess_database_space_type(space_type):
    # Remove leading/trailing spaces and convert to lowercase
    return space_type.strip().lower()

def find_best_match(activity_desc, database):
    # Use fuzzy matching to find the best match in the database
    activity_desc_lower = activity_desc.lower()
    # Ensure all entries in 'Activity Description_eQUEST' are strings and handle NaN values
    choices = database['Activity Description_eQUEST'].fillna('').astype(str).tolist()
    best_match, score = process.extractOne(activity_desc_lower, choices, scorer=fuzz.partial_ratio)
    return best_match if score >= 80 else None  # Threshold can be adjusted

def updateLPD(inp_data, sim_data):
    # Define markers to identify the section of interest
    start_marker = "Floors / Spaces / Walls / Windows / Doors"
    end_marker = "Electric & Fuel Meters"

    # Load database
    database = pd.read_csv("database/eQUEST_database.csv")

    # Preprocess database Activity Description_eQUEST type column
    database['Activity Description_eQUEST'] = database['Activity Description_eQUEST'].str.strip().str.lower()

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

    # Loop through the lines between start and end indices
    for i in range(start_index, end_index):
        line = inp_data[i].strip()  # Remove leading and trailing whitespace from the line
        if "= SPACE" in line:
            k = i
            # Extracting C-ACTIVITY-DESC value
            activity_desc = None
            while not line.startswith(".."):  # Continue until the end of the section
                if "C-ACTIVITY-DESC" in line:
                    activity_desc = line.split("C-ACTIVITY-DESC")[1].strip()  # Extract activity description
                    activity_desc = preprocess_activity_desc(activity_desc)  # Preprocess activity description
                    break
                i += 1
                if i >= end_index:  # Break loop if end of section is reached
                    break
                line = inp_data[i].strip()

            # If C-ACTIVITY-DESC is found
            if activity_desc:
                # Find the best match using fuzzy matching
                best_match = find_best_match(activity_desc, database)
                if best_match:
                    # Get corresponding LPD value
                    matches = database[database['Activity Description_eQUEST'] == best_match]
                    if not matches.empty:
                        lpd_value = matches.iloc[0]['Lighting Power density (W/sqft)']
                        # Update LIGHTING-W/AREA only if it is found after the C-ACTIVITY-DESC line
                        for j in range(k, len(inp_data)):
                            if inp_data[j].strip().startswith("LIGHTING-W/AREA"):
                                inp_data[j] = f"   LIGHTING-W/AREA = ( {lpd_value} )" + "\n"  # Update LPD value
                                break
                            elif inp_data[j].startswith(".."):  # Break loop if a new section starts
                                break

    return inp_data
