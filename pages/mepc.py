import streamlit as st
import subprocess
import os
import pandas as pd
from streamlit_card import card
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json
import streamlit.components.v1 as components
import re
import tempfile
from MEP_Calculator import loads

# -------------------------
# Helper utilities
# -------------------------

def safe_round(value, ndigits=2):
    try:
        return round(float(value), ndigits)
    except Exception:
        return value


def compute_weighted_average(df, weight_col, value_col):
    if df.empty:
        return None
    total_w = df[weight_col].sum()
    if total_w == 0:
        return None
    return (df[weight_col] * df[value_col]).sum() / total_w


# -------------------------
# Streamlit config
# -------------------------
st.set_page_config(
    page_title="eQUEST Utilities",
    page_icon="💡",
    layout='wide',
)

# Ensure session state defaults
if 'analysis_option' not in st.session_state:
    st.session_state.analysis_option = None
if 'mapped_spaces' not in st.session_state:
    st.session_state.mapped_spaces = set()
if 'mapped_df' not in st.session_state:
    st.session_state.mapped_df = pd.DataFrame(
        columns=["SPACE", "AREA(SQFT)", "EQUIP(WATT / SOFT)", "LIGHTS(WATT / SOFT)", "Building Type"]
    )

# -------------------------
# Top description + CSS
# -------------------------
st.markdown("""<h4 style="color:red;">♻️ MEPC Tool</h4>""",unsafe_allow_html=True,)
st.markdown("""
    <style>
    .stButton button { height: 30px; width: 166px; }
    html { scroll-behavior: smooth; }
    div[data-testid="stAppViewContainer"] > .main { padding-top: 90px !important; }

    /* Fixed header visuals (keeps anchors visible) */
    .fixed-header {
        position: fixed; top: 0; left: 0; right: 0; height: 52px; background-color: white;
        display: flex; align-items: center; justify-content: center; gap: 14px;
        border-bottom: 1px solid #ddd; z-index: 9999; padding: 6px 10px;
    }
    .fixed-header a { text-decoration: none; font-weight: bold; color: #333; font-size: 14px; }
    .fixed-header a:hover { color: #0073e6; }
    .section { padding-top: 40px; padding-bottom: 50px; }
    </style>
""", unsafe_allow_html=True)
# -------------------------
# Persistent navigation (horizontal only)
# -------------------------
# --- Inject CSS ---
st.markdown(
    """
    <style>
    html {
        scroll-behavior: smooth;
    }
    /* push content down so it's not hidden behind header */
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 70px !important;
    }
    /* ---- FIXED HEADER ---- */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 40px;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        border-bottom: 1px solid #ddd;
        z-index: 1000;
    }
    .fixed-header a {
        text-decoration: none;
        font-weight: bold;
        color: #333;
        font-size: 16px;
    }
    .fixed-header a:hover {
        color: #0073e6;
    }
    .section {
        padding-top: 40px;
        padding-bottom: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER (after description, but fixed at top) ---
st.markdown(
    """
    <div class="fixed-header">
        <a href="#upload">Upload SIM Files</a>
        <a href="#unmatched">Unmatched Spaces</a>
        <a href="#edit">Review-Edit Spaces</a>
        <a href="#list">Matched Spaces</a>
        <a href="#calculator">Final Summary</a>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Upload Section
# -------------------------

st.markdown('<div id="upload" class="section"></div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    uploaded_0_degree = st.file_uploader("Upload 0° SIM File", type=["sim"], key="up0")
with col2:
    uploaded_90_degree = st.file_uploader("Upload 90° SIM File", type=["sim"], key="up90")
with col3:
    uploaded_180_degree = st.file_uploader("Upload 180° SIM File", type=["sim"], key="up180")
with col4:
    uploaded_270_degree = st.file_uploader("Upload 270° SIM File", type=["sim"], key="up270")
with col5:
    uploaded_proposed_file = st.file_uploader("Upload Proposed SIM File", type=["sim"], key="upprop")

# Only continue processing when required files are present
if uploaded_0_degree is not None and uploaded_proposed_file is not None:
    # load database once
    databse = r'MEP_Calculator/database/eQUEST_database.csv'
    try:
        database = pd.read_csv(databse)
    except Exception as e:
        st.error(f"Unable to read database file: {e}")
        st.stop()

    # write uploaded files to temporary paths so MEP_Calculator.loads can read them
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(uploaded_proposed_file.read())
        temp_file_path_proposed = temp_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sim") as temp_file:
        temp_file.write(uploaded_0_degree.read())
        temp_file_path_baseline = temp_file.name

    # Use the helper functions from loads
    lv_d_proposed = loads.get_LVB_Report(temp_file_path_proposed)
    lv_d_baseline = loads.get_LVB_Report(temp_file_path_baseline)

    # Keep only required columns if they exist
    required_cols = ['SPACE', 'AREA(SQFT)', 'EQUIP(WATT / SOFT)', 'LIGHTS(WATT / SOFT)']
    for df in [lv_d_baseline, lv_d_proposed]:
        for c in required_cols:
            if c not in df.columns:
                df[c] = np.nan

    lv_d_baseline = lv_d_baseline[required_cols]
    lv_d_proposed = lv_d_proposed[required_cols]

    # ----------------- STEP 1: match identical modeled spaces -----------------
    merged_df = lv_d_baseline.merge(
        lv_d_proposed,
        on='SPACE',
        suffixes=('_baseline', '_proposed'),
        how='outer'
    )

    merged_df['Mark'] = merged_df.apply(
        lambda row: "Yes" if (
            pd.notna(row['AREA(SQFT)_baseline']) and pd.notna(row['AREA(SQFT)_proposed'])
            and row['AREA(SQFT)_baseline'] == row['AREA(SQFT)_proposed']
            and row['EQUIP(WATT / SOFT)_baseline'] == row['EQUIP(WATT / SOFT)_proposed']
        ) else "No",
        axis=1
    )

    # Create Code 3 safely
    database['Code 3'] = database.get('Code', '').astype(str).str[:2].str.capitalize() + \
                         database.get('Space type', '').astype(str).str[:2].str.capitalize()

    # Filter baseline spaces with valid SPACE
    lv_b_baseline = lv_d_baseline.dropna(subset=['SPACE'])

    filtered_data = database[['Building_Type', 'Code 3']].dropna()

    # Build summary rows per building type using baseline
    summary_rows = []
    for btype in filtered_data['Building_Type'].unique():
        btype_filtered = filtered_data[filtered_data['Building_Type'] == btype]
        matched_list = []
        for _, row in lv_b_baseline.iterrows():
            space_val = str(row['SPACE'])
            for _, code_row in btype_filtered.iterrows():
                code_3 = str(code_row['Code 3'])
                if code_3 and code_3 in space_val:
                    matched_list.append({
                        'AREA(SQFT)': row['AREA(SQFT)'],
                        'EQUIP(WATT / SOFT)': row['EQUIP(WATT / SOFT)'],
                        'LIGHTS(WATT / SOFT)': row['LIGHTS(WATT / SOFT)']
                    })
                    break
        if matched_list:
            matched_df = pd.DataFrame(matched_list)
            total_area = matched_df['AREA(SQFT)'].sum()
            weighted_equip = compute_weighted_average(matched_df, 'AREA(SQFT)', 'EQUIP(WATT / SOFT)')
            weighted_light = compute_weighted_average(matched_df, 'AREA(SQFT)', 'LIGHTS(WATT / SOFT)')
            summary_rows.append({
                'Building Type': btype,
                'AREA(SQFT)': total_area,
            })

    # If all spaces match identically then proceed, else show error
    if (merged_df['Mark'] == 'Yes').all():
        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            # add total
            grand_total = summary_df['AREA(SQFT)'].sum()
            total_row = pd.DataFrame([{'Building Type': 'TOTAL', 'AREA(SQFT)': grand_total}])
            summary_df = pd.concat([summary_df, total_row], ignore_index=True)
        else:
            st.warning("No matches found for any building type in baseline. Continuing with proposed mapping.")

        # ----------------- create matched and unmatched from proposed -----------------
        lv_b_proposed = lv_d_proposed.dropna(subset=['SPACE'])
        filtered_data = database[['Building_Type', 'Code 3']].dropna()

        matched_spaces = []
        unmatched_spaces = []
        for _, row in lv_b_proposed.iterrows():
            space_val = str(row['SPACE'])
            matched_type = None
            for _, code_row in filtered_data.iterrows():
                if str(code_row['Code 3']) and str(code_row['Code 3']) in space_val:
                    matched_type = code_row['Building_Type']
                    break
            if matched_type:
                matched_spaces.append({
                    'SPACE': space_val,
                    'Building Type': matched_type,
                    'AREA(SQFT)': row['AREA(SQFT)'],
                    'EQUIP(WATT / SOFT)': row['EQUIP(WATT / SOFT)'],
                    'LIGHTS(WATT / SOFT)': row['LIGHTS(WATT / SOFT)']
                })
            else:
                unmatched_spaces.append({
                    'SPACE': space_val,
                    'AREA(SQFT)': row['AREA(SQFT)'],
                    'EQUIP(WATT / SOFT)': row['EQUIP(WATT / SOFT)'],
                    'LIGHTS(WATT / SOFT)': row['LIGHTS(WATT / SOFT)']
                })

        matched_df = pd.DataFrame(matched_spaces) if matched_spaces else pd.DataFrame(
            columns=['SPACE', 'Building Type', 'AREA(SQFT)', 'EQUIP(WATT / SOFT)', 'LIGHTS(WATT / SOFT)'])

        # --- Unmatched mapping UI ---
        st.markdown("##### ⚠️ Map Unmatched Spaces")
        if unmatched_spaces:
            with st.form("mapping_form"):
                col1, col2 = st.columns([2.8, 1.2])
                with col1:
                    unmatched_df = pd.DataFrame(unmatched_spaces).reset_index(drop=True)

                    selected_spaces = []
                    cols = st.columns(4)
                    for i, row in unmatched_df.iterrows():
                        col = cols[i % 4]
                        is_disabled = row['SPACE'] in st.session_state.mapped_spaces
                        checked = col.checkbox(f"{row['SPACE']}", key=f"check_{i}", disabled=is_disabled)
                        if checked and not is_disabled:
                            selected_spaces.append(row['SPACE'])

                    building_types_list = sorted(database['Building_Type'].dropna().unique(), key=str.lower)

                with col2:
                    selected_btype = st.selectbox("Building Type", options=building_types_list, label_visibility="collapsed")
                    submit = st.form_submit_button("✅ Map Selected")
                    if submit and selected_spaces:
                        for space in selected_spaces:
                            st.session_state.mapped_spaces.add(space)
                            row_data = unmatched_df[unmatched_df['SPACE'] == space].copy()
                            row_data["Building Type"] = selected_btype
                            st.session_state.mapped_df = pd.concat([st.session_state.mapped_df, row_data], ignore_index=True)
                        st.success(f"Mapped {len(selected_spaces)} spaces to '{selected_btype}'")

        # --- Build final_df (auto-matched + manual mapped)
        if not st.session_state.mapped_df.empty:
            final_df = pd.concat([matched_df, st.session_state.mapped_df], ignore_index=True)
        else:
            final_df = matched_df.copy()

        # --- Build summary_df from final_df ---
        summary_rows = []
        for btype in final_df['Building Type'].unique():
            temp_df = final_df[final_df['Building Type'] == btype]
            area = temp_df['AREA(SQFT)'].sum()
            weighted_equip = compute_weighted_average(temp_df, 'AREA(SQFT)', 'EQUIP(WATT / SOFT)')
            weighted_light = compute_weighted_average(temp_df, 'AREA(SQFT)', 'LIGHTS(WATT / SOFT)')

            # baseline lights for those spaces if available
            baseline_spaces = lv_d_baseline[lv_d_baseline['SPACE'].isin(temp_df['SPACE'])]
            baseline_light = compute_weighted_average(baseline_spaces, 'AREA(SQFT)', 'LIGHTS(WATT / SOFT)')

            summary_rows.append({
                'Building Type': btype,
                'AREA(SQFT)': area,
                'EQUIP(WATT / SOFT)': safe_round(weighted_equip, 2) if weighted_equip is not None else None,
                'LIGHTS(WATT / SOFT)': safe_round(weighted_light, 2) if weighted_light is not None else None,
                'LIGHTS(WATT / SOFT) (Baseline)': safe_round(baseline_light, 2) if baseline_light is not None else None,
                'Baseline Modeled Identically': 'Yes'
            })

        summary_df = pd.DataFrame(summary_rows)

        if not summary_df.empty:
            total_area = summary_df['AREA(SQFT)'].sum()
            total_equip = compute_weighted_average(summary_df[['AREA(SQFT)', 'EQUIP(WATT / SOFT)']].rename(columns={
                'AREA(SQFT)': 'AREA(SQFT)', 'EQUIP(WATT / SOFT)': 'EQUIP(WATT / SOFT)'
            }), 'AREA(SQFT)', 'EQUIP(WATT / SOFT)')

            total_light = compute_weighted_average(summary_df[['AREA(SQFT)', 'LIGHTS(WATT / SOFT)']].rename(columns={
                'AREA(SQFT)': 'AREA(SQFT)', 'LIGHTS(WATT / SOFT)': 'LIGHTS(WATT / SOFT)'
            }), 'AREA(SQFT)', 'LIGHTS(WATT / SOFT)')

            total_light_baseline = compute_weighted_average(summary_df[['AREA(SQFT)', 'LIGHTS(WATT / SOFT) (Baseline)']].dropna().rename(columns={
                'AREA(SQFT)': 'AREA(SQFT)', 'LIGHTS(WATT / SOFT) (Baseline)': 'LIGHTS(WATT / SOFT) (Baseline)'
            }), 'AREA(SQFT)', 'LIGHTS(WATT / SOFT) (Baseline)')

            total_row = pd.DataFrame([{
                'Building Type': 'TOTAL',
                'AREA(SQFT)': total_area,
                'EQUIP(WATT / SOFT)': safe_round(total_equip, 2) if total_equip is not None else None,
                'LIGHTS(WATT / SOFT)': safe_round(total_light, 2) if total_light is not None else None,
                'LIGHTS(WATT / SOFT) (Baseline)': safe_round(total_light_baseline, 2) if total_light_baseline is not None else None
            }])

            summary_df = pd.concat([summary_df, total_row], ignore_index=True)

        # --- Display review/edit table with delete buttons ---
        st.markdown("##### 📝 Mapped Spaces: Review & Edit")
        if summary_df.empty:
            st.info("No mapped building types to show yet.")
        else:
            table_data = summary_df.to_dict('records')
            header_cols = st.columns([1, 0.6, 0.6, 0.6])
            for col, header in zip(header_cols, ["Building Type", "AREA (SQFT)", "EQUIP (WATT / SQFT)", "Action"]):
                col.markdown(f"**{header}**")

            for i, row in enumerate(table_data):
                row_cols = st.columns([1, 0.6, 0.6, 0.6])
                row_cols[0].write(row.get('Building Type', ''))
                area_val = row.get('AREA(SQFT)', 0) or 0
                row_cols[1].write(f"{safe_round(area_val,2):.2f}")
                equip_val = row.get('EQUIP(WATT / SOFT)', 0) or 0
                try:
                    row_cols[2].write(f"{safe_round(equip_val,2):.2f}")
                except Exception:
                    row_cols[2].write(equip_val)

                if row.get('Building Type') != "TOTAL":
                    # show delete only for manually mapped types
                    if row.get('Building Type') in st.session_state.mapped_df['Building Type'].tolist():
                        if row_cols[3].button("🗑️ Delete", key=f"del_{i}"):
                            st.session_state.mapped_df = st.session_state.mapped_df[st.session_state.mapped_df['Building Type'] != row.get('Building Type')]
                            # remove mapped spaces corresponding to this building type
                            removed_spaces = final_df[final_df['Building Type'] == row.get('Building Type')]['SPACE'].tolist()
                            for space in removed_spaces:
                                st.session_state.mapped_spaces.discard(space)
                            st.experimental_rerun()
                    else:
                        row_cols[3].markdown("🔒 Auto-matched", unsafe_allow_html=True)
                else:
                    row_cols[3].write("")

        # --- Matched list expander ---
        with st.expander("✅ See List of Matched Spaces"):
            if not final_df.empty:
                st.markdown("##### 📋 Current Matched Spaces (Auto + Manual)")
                st.dataframe(final_df)
            else:
                st.info("No matched spaces found yet.")

    else:
        st.error("Baseline didn't Model Identically. Please verify baseline and proposed SIM files.")

    # =====================================================================================
    # --- Calculator section ---
    if 'summary_df' in locals() and summary_df is not None:
        st.markdown("""<h6 style="color:red;">🔴 Select Calculator</h6>""", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("Performance Output"):
                st.session_state.analysis_option = "Performance Outputs"
        with col2:
            if st.button("Shade & Fenes."):
                st.session_state.analysis_option = "Shading and Fenestration"
        with col3:
            if st.button("Schedules"):
                st.session_state.analysis_option = "Schedules"
        with col4:
            if st.button("Lighting"):
                st.session_state.analysis_option = "lighting"
        with col5:
            if st.button("Process Loads"):
                st.session_state.analysis_option = "Process Loads"

    # ----------------- Execute selected analysis -----------------
    if st.session_state.analysis_option:
        st.write(f"You selected: **{st.session_state.analysis_option}**")
        analysis_option = st.session_state.analysis_option

        csv_file = r'MEP_Calculator/tables/MEP Calculator.csv'
        databse = r'MEP_Calculator/database/eQUEST_database.csv'
        df = pd.read_csv(csv_file) if os.path.exists(csv_file) else pd.DataFrame()
        db = pd.read_csv(databse) if os.path.exists(databse) else pd.DataFrame()

        if analysis_option == "Process Loads":
            st.markdown("##### 📊 Final Summary")
            if "EQUIP(WATT / SOFT)" in summary_df.columns:
                # Remove lighting-only columns
                summary_df_proc = summary_df.copy()
                summary_df_proc = summary_df_proc.drop(columns=[c for c in ["LIGHTS(WATT / SOFT)", "LIGHTS(WATT / SOFT) (Baseline)"] if c in summary_df_proc.columns], errors='ignore')
                # Insert blank column per original behaviour
                insert_at = summary_df_proc.columns.get_loc("Building Type") + 1 if "Building Type" in summary_df_proc.columns else 1
                summary_df_proc.insert(insert_at, "Building Type ", "")

                result = None
                try:
                    result = round((summary_df_proc["AREA(SQFT)"] * summary_df_proc["EQUIP(WATT / SOFT)"]).sum() / 1000, 2)
                except Exception:
                    result = None

                new_row = {
                    "Building Type": "Total power modeled using space by space method(kW)",
                    "Baseline Modeled Identically": result
                }

                summary_df_proc = pd.concat([summary_df_proc, pd.DataFrame([new_row])], ignore_index=True)
                summary_df_proc = summary_df_proc.rename(columns={"EQUIP(WATT / SOFT)": "Equipment Power Density(W/ft²)", "AREA(SQFT)": "Area(ft²)"})
                st.dataframe(summary_df_proc)
            else:
                st.dataframe(summary_df)

        elif analysis_option == "Performance Outputs":
            if st.button("Generate Reports"):
                st.markdown(
                    """
                    <div style='background-color:#fff3cd;padding:10px;border-left:6px solid #ffecb5;'>
                        <strong>Disclaimer:</strong> <br>1. This tool is used when completing baseline results for each of the four building orientations.<br>
                        2. This Tool looks at PS-E Meters and assumes all <strong>electric</strong> meters currently.
                        Units used are <strong>kWh</strong> (Consumption) and <strong>kW</strong> (Demand).
                    </div><br>
                    """,
                    unsafe_allow_html=True
                )
                # ps_e.get_END_USE_Proposed(...)  # uncomment when ps_e is available
            else:
                st.info("Please upload all 4 rotation SIM files for Performance Outputs.")

        elif analysis_option == "Shading and Fenestration":
            if uploaded_0_degree is not None and uploaded_proposed_file is not None:
                if st.button("Generate Reports"):
                    # lv_d.generateFenestration(uploaded_0_degree, uploaded_proposed_file)
                    st.info("Fenestration report generation invoked.")

        elif analysis_option == "Schedules":
            if uploaded_0_degree is not None and uploaded_proposed_file is not None:
                cols = st.columns(8)
                with cols[0]:
                    holiday = st.number_input("Holiday", min_value=0, max_value=365, value=11, key="holiday")
                with cols[1]:
                    monday = st.number_input("Monday", min_value=0, max_value=365, value=50, key="monday")
                with cols[2]:
                    tuesday = st.number_input("Tuesday", min_value=0, max_value=365, value=50, key="tuesday")
                with cols[3]:
                    wednesday = st.number_input("Wednesday", min_value=0, max_value=365, value=50, key="wednesday")
                with cols[4]:
                    thursday = st.number_input("Thursday", min_value=0, max_value=365, value=50, key="thursday")
                with cols[5]:
                    friday = st.number_input("Friday", min_value=0, max_value=365, value=50, key="friday")
                with cols[6]:
                    saturday = st.number_input("Saturday", min_value=0, max_value=365, value=52, key="saturday")
                with cols[7]:
                    sunday = st.number_input("Sunday", min_value=0, max_value=365, value=52, key="sunday")
                tot_days = (holiday + monday + tuesday + wednesday + thursday + friday + saturday + sunday)
                if tot_days == 365:
                    if st.button("Generate Reports"):
                        # eflh.generateSchedules(...)
                        st.success("Schedules generation invoked.")
                else:
                    st.error("❌ Total days must equal 365.")

        elif analysis_option == "lighting":
            st.markdown("##### 📊 Final Summary")

            # Work on a copy to avoid accidental mutation
            lighting_df = summary_df.copy()

            # Drop equip column if present (for pure lighting view)
            lighting_df = lighting_df.drop(columns=[c for c in ["EQUIP(WATT / SOFT)", "Baseline Modeled Identically"] if c in lighting_df.columns], errors='ignore')

            # Rename columns where present
            rename_map = {}
            if "LIGHTS(WATT / SOFT)" in lighting_df.columns:
                rename_map["LIGHTS(WATT / SOFT)"] = "Design LPD(W/ft²)"
            if "AREA(SQFT)" in lighting_df.columns:
                rename_map["AREA(SQFT)"] = "Area(ft²)"
            if "LIGHTS(WATT / SOFT) (Baseline)" in lighting_df.columns:
                rename_map["LIGHTS(WATT / SOFT) (Baseline)"] = "Maximum Allowance(W/ft²)"

            lighting_df = lighting_df.rename(columns=rename_map)

            # If both baseline allowance and design LPD exist, create additional columns
            if "Design LPD(W/ft²)" in lighting_df.columns and "Maximum Allowance(W/ft²)" in lighting_df.columns:
                lighting_df["Modeled Design LPD(W/ft²)"] = lighting_df["Design LPD(W/ft²)"].copy()
                # create total baseline allowance column (currently a copy — modify formula if different logic desired)
                lighting_df["Total Baseline LPD Allowance(W/ft²)"] = lighting_df["Maximum Allowance(W/ft²)"].copy()

                # Reorder columns into sensible grouping
                desired_cols = [col for col in ["Building Type", "Area(ft²)", "Maximum Allowance(W/ft²)", "Total Baseline LPD Allowance(W/ft²)", "Design LPD(W/ft²)", "Modeled Design LPD(W/ft²)"] if col in lighting_df.columns]
                lighting_df = lighting_df[desired_cols]

                # Show with MultiIndex header similar to original intention
                try:
                    multi_cols = pd.MultiIndex.from_tuples([
                        ("", "Building Type"),
                        ("", "Area(ft²)"),
                        ("Baseline", "Maximum Allowance(W/ft²)"),
                        ("Baseline", "Total Baseline LPD Allowance(W/ft²)"),
                        ("Proposed", "Design LPD(W/ft²)"),
                        ("Proposed", "Modeled Design LPD(W/ft²)")
                    ])
                    lighting_df.columns = multi_cols
                except Exception:
                    # fallback to normal display if MultiIndex fails
                    pass

                st.dataframe(lighting_df)
            else:
                # If required columns missing, just display what we have but be graceful
                st.dataframe(lighting_df)