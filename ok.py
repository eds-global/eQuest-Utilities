import streamlit as st
import pandas as pd
import re

# Sample DataFrame – replace with your actual file data
df = pd.DataFrame({
    "SPACE": [
        "GF-A_Kitchen", "GF-A_Dish_Washer", "GF-B_Corr-1",
        "FF-A_Hall", "GF-B_Store-1", "GF-B_Gym"
    ],
    "AREA (SQFT)": [300, 150, 100, 200, 180, 250],
    "EQUIP (W/SQFT)": [1.5, 1.2, 0.8, 1.7, 1.0, 2.0]
})

# Predefined list of building types (editable)
building_types = [
    "Dining area", "Corridor/transition", "Storage", "Gym/fitness center",
    "Conference/meeting/multipurpose", "Restrooms", "Office", "Lobby",
    "Electrical/mechanical", "Laboratory medical/industrial/research"
]

# Step 1: Select a building type
selected_btype = st.selectbox("Select Building Type", building_types)

# Step 2: Let user select SPACEs manually
st.write(f"Select SPACEs to associate with **{selected_btype}**:")
selected_spaces = []
for space in df["SPACE"]:
    if st.checkbox(space, key=space):
        selected_spaces.append(space)

# Step 3: Show results
if selected_spaces:
    filtered = df[df["SPACE"].isin(selected_spaces)]
    total_area = filtered["AREA (SQFT)"].sum()
    avg_equip = filtered["EQUIP (W/SQFT)"].mean()

    result = pd.DataFrame([{
        "Building Type": selected_btype,
        "Total Area (SQFT)": total_area,
        "Avg Equip (W/SQFT)": round(avg_equip, 2)
    }])
    st.table(result)
else:
    st.info("Please select at least one SPACE.")
