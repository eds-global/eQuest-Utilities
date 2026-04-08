import streamlit as st
from MEP_Calculator import loads, ps_e, lv_d
import pandas as pd
import re

st.set_page_config(page_title="eQUEST Utilities", page_icon="💡", layout='wide')

# -------------------------
# Fixed Title + Navigation
# -------------------------
st.markdown(
    """
    <style>
    html { scroll-behavior: smooth; }
    /* Push content so it's not hidden behind the fixed header */
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 120px !important;
    }
    /* Fixed header styling */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 170px;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #ddd;
        z-index: 1000;
    }
    .fixed-header h4 {
        color: red;
        margin: 5px 0;
    }
    .nav-links {
        display: flex;
        gap: 35px;
    }
    .nav-links a {
        text-decoration: none;
        font-weight: bold;
        color: #333;
        font-size: 15px;
    }
    .nav-links a:hover {
        color: #0073e6;
    }
    .section {
        padding-top: 50px;
        padding-bottom: 30px;
    }
    a.button-link {
        background-color: #f0f0f0;
        color: black;
        padding: 8px 16px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
    }
    a.button-link:focus, a.button-link:active {
        color: black !important;
        outline: none;
    }
    </style>

    <div class="fixed-header">
        <h4>LEED MEPC Tool</h4>
        <div class="nav-links">
            <a href="/" target="_self">Home</a>
            <a href="#start">Getting Started</a>
            <a href="#opaque">Opaque Assembly</a>
            <a href="#performance">Performance Outputs</a>
            <a href="#shade">Shading & Fenestration</a>
            <a href="#schedules">Schedules</a>
            <a href="#lighting">Lighting</a>
            <a href="#loads">Process Loads</a>
            <a href="#hvac-air">Air-Side HVAC</a>
            <a href="#hvac-water">Water-Side HVAC</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

button_style = """
    <style>
        .stButton>button {
            box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.8);
        }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

def safe_get_uvalue(df, azimuth, column='AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)'):
    if 'AZIMUTH' not in df.columns:
        print("⚠️ Column 'AZIMUTH' not found. Available:", df.columns)
        return None
    if column not in df.columns:
        print(f"⚠️ Column '{column}' not found. Available:", df.columns)
        return None
    
    # Normalize strings only if they are strings
    rows = df.loc[df['AZIMUTH'].astype(str).str.strip().str.upper() == azimuth.upper(), column]
    if rows.empty:
        print(f"⚠️ No rows found for azimuth='{azimuth}'. Unique AZIMUTH values:", df['AZIMUTH'].unique())
        return None

    return rows.iloc[0]

def get_val(df, azimuth, column):
    row = df.loc[df["AZIMUTH"] == azimuth, column]
    return row.iloc[0] if not row.empty else 0

def safe_get(df, azimuth, column, default=0):
    row = df.loc[df['AZIMUTH'] == azimuth, column]
    if row.empty:
        return default
    val = row.iloc[0]
    if pd.isna(val):
        return default
    return val

# -------------------------
# Section 1 - Upload
# -------------------------
st.markdown('<div id="start" class="section"></div>', unsafe_allow_html=True)
st.markdown(
        '<h5 style="color:red;">Upload SIM Files</h5>',
        unsafe_allow_html=True
    )
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    uploaded_0_degree = st.file_uploader("Upload 0° SIM File", type=["sim"], accept_multiple_files=False)
with col2:
    uploaded_90_degree = st.file_uploader("Upload 90° SIM File", type=["sim"], accept_multiple_files=False)
with col3:
    uploaded_180_degree = st.file_uploader("Upload 180° SIM File", type=["sim"], accept_multiple_files=False)
with col4:
    uploaded_270_degree = st.file_uploader("Upload 270° SIM File", type=["sim"], accept_multiple_files=False)
with col5:
    uploaded_proposed_file = st.file_uploader("Upload a Proposed SIM file", type=["sim"], accept_multiple_files=False)

if uploaded_0_degree is not None and uploaded_proposed_file is not None:
    sim_file_for_use1 = uploaded_0_degree
    sim_file_proposed_for_use1 = uploaded_proposed_file
    sim_file_for_use90 = uploaded_90_degree
    sim_file_for_use180 = uploaded_180_degree
    sim_file_for_use270 = uploaded_270_degree
    databse = r'MEP_Calculator/database/eQUEST_database.csv'
    csv_file = r'MEP_Calculator/tables/MEP Calculator.csv'
    dfsss = pd.read_csv(csv_file)
    db = pd.read_csv(databse)
    summary_df, sv_a_df, sv_a_zone_df, sv_a_df_p, pva_df, pva_primary, ps_e_df_b, lv_d_summ_p, lv_d_summ_b, lv_g_baseline, lv_g_proposed, ps_e_proposed, pse_90, pse_180, pse_270, lvd_base, pva_pumps, pva_loop_p, pva_pumps_p, pva_primary_p, pva_tower, pva_tower_p = loads.getProcessLoads(db, sim_file_proposed_for_use1, sim_file_for_use1, sim_file_for_use90, sim_file_for_use180, sim_file_for_use270)
    st.markdown('<div id="opaque" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown('<h5 style="color:red;">Opaque Assemblies</h5>',unsafe_allow_html=True)
    try:
        roof = lvd_base[lvd_base['AZIMUTH'].str.upper() == "ROOF"]
        floor = lvd_base[lvd_base['AZIMUTH'].str.upper() == "FLOOR"]
        below_grade = lvd_base[lvd_base['AZIMUTH'].str.upper() == "UNDERGRND"]
        wall_orientations = ["NORTH", "SOUTH", "EAST", "WEST", "NORTH-EAST", "NORTH-WEST", "SOUTH-EAST", "SOUTH-WEST"]
        above_grade = lvd_base[lvd_base['AZIMUTH'].str.upper().isin(wall_orientations)]
        u_col = "U-VALUE_Wall(BTU/HR-SQFT-F)"
        roof_unique_u = roof[u_col].nunique()
        floor_unique_u = floor[u_col].nunique()
        below_grade_unique_u = below_grade[u_col].nunique()
        above_grade_unique_u = above_grade[u_col].nunique()

        st.markdown('<h7 style="color:red;">Roof Constructions</h7>', unsafe_allow_html=True)
        cols = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),

            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),

            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor"),

            ("Roof Solar Reflectance and Thermal Emittance", "Baseline"),
            ("Roof Solar Reflectance and Thermal Emittance", "Proposed")
        ])

        # Number of rows = unique roof U-values
        num_rows = roof_unique_u
        df = pd.DataFrame([[""] * len(cols)] * num_rows, columns=cols)

        roof_p_vals = lv_d_summ_p.loc[
            lv_d_summ_p["AZIMUTH"] == "ROOF",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        roof_b_vals = lv_d_summ_b.loc[
            lv_d_summ_b["AZIMUTH"] == "ROOF",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        for i in range(num_rows):
            df.at[i, ("Proposed", "Assembly U-factor")] = roof_p_vals[i] if i < len(roof_p_vals) else ""
            df.at[i, ("Baseline", "Assembly U-factor")] = roof_b_vals[i] if i < len(roof_b_vals) else ""
        st.dataframe(df, use_container_width=True)

        st.markdown('<h7 style="color:red;">Above-Grade Exterior Wall Constructions</h7>', unsafe_allow_html=True)
        cols = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),

            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),

            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor")
        ])

        num_rows = above_grade_unique_u
        df = pd.DataFrame([[""] * len(cols)] * num_rows, columns=cols)

        ag_p_vals = lv_d_summ_p.loc[
            lv_d_summ_p["AZIMUTH"] == "ALL WALLS",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        ag_b_vals = lv_d_summ_b.loc[
            lv_d_summ_b["AZIMUTH"] == "ALL WALLS",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        for i in range(num_rows):
            df.at[i, ("Proposed", "Assembly U-factor")] = ag_p_vals[i] if i < len(ag_p_vals) else ""
            df.at[i, ("Baseline", "Assembly U-factor")] = ag_b_vals[i] if i < len(ag_b_vals) else ""
        st.dataframe(df, use_container_width=True)

        st.markdown('<h7 style="color:red;">Below-Grade Exterior Wall Constructions</h7>', unsafe_allow_html=True)
        cols = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),

            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),

            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor")
        ])

        num_rows = below_grade_unique_u
        df = pd.DataFrame([[""] * len(cols)] * num_rows, columns=cols)

        bg_p_vals = lv_d_summ_p.loc[
            lv_d_summ_p["AZIMUTH"] == "UNDERGRND",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        bg_b_vals = lv_d_summ_b.loc[
            lv_d_summ_b["AZIMUTH"] == "UNDERGRND",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        for i in range(num_rows):
            df.at[i, ("Proposed", "Assembly U-factor")] = bg_p_vals[i] if i < len(bg_p_vals) else ""
            df.at[i, ("Baseline", "Assembly U-factor")] = bg_b_vals[i] if i < len(bg_b_vals) else ""

        st.dataframe(df, use_container_width=True)

        st.markdown('<h7 style="color:red;">Eposed Floor Constructions</h7>', unsafe_allow_html=True)
        cols = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),

            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),

            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor")
        ])

        num_rows = floor_unique_u
        df = pd.DataFrame([[""] * len(cols)] * num_rows, columns=cols)

        fl_p_vals = lv_d_summ_p.loc[
            lv_d_summ_p["AZIMUTH"] == "FLOOR",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        fl_b_vals = lv_d_summ_b.loc[
            lv_d_summ_b["AZIMUTH"] == "FLOOR",
            "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)"
        ].unique()

        for i in range(num_rows):
            df.at[i, ("Proposed", "Assembly U-factor")] = fl_p_vals[i] if i < len(fl_p_vals) else ""
            df.at[i, ("Baseline", "Assembly U-factor")] = fl_b_vals[i] if i < len(fl_b_vals) else ""

        st.dataframe(df, use_container_width=True)

        st.markdown('<h7 style="color:red;">Slab on Grade Floors</h7>',unsafe_allow_html=True)
        # Creating multi-level column headers
        cols = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),

            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),

            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor")
        ])

        # Create empty row
        df = pd.DataFrame([[""] * len(cols)], columns=cols)
        # ---- Get value from original data ----
        match_p = lv_d_summ_p.loc[lv_d_summ_p['AZIMUTH'] == 'ROOF','AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)']
        match_b = lv_d_summ_b.loc[lv_d_summ_b['AZIMUTH'] == 'ROOF', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)']

        roof_u_value_p = match_p.iloc[0] if not match_p.empty else ""
        roof_u_value_b = match_b.iloc[0] if not match_b.empty else ""
        # ---- Put the value in the Proposed Assembly column ----
        df.at[0, ("Proposed", "Assembly U-factor")] = roof_u_value_p
        df.at[0, ("Baseline", "Assembly U-factor")] = roof_u_value_b
        st.dataframe(df, use_container_width=True)

        st.markdown('<h7 style="color:red;">Opaque Doors</h7>',unsafe_allow_html=True)
        # Creating multi-level column headers
        cols = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),

            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),

            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor")
        ])

        # Create empty row
        df = pd.DataFrame([[""] * len(cols)], columns=cols)
        # ---- Get value from original data ----
        match_p = lv_d_summ_p.loc[lv_d_summ_p['AZIMUTH'] == 'ROOF','AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)']
        match_b = lv_d_summ_b.loc[lv_d_summ_b['AZIMUTH'] == 'ROOF', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)']

        roof_u_value_p = match_p.iloc[0] if not match_p.empty else ""
        roof_u_value_b = match_b.iloc[0] if not match_b.empty else ""
        # ---- Put the value in the Proposed Assembly column ----
        df.at[0, ("Proposed", "Assembly U-factor")] = roof_u_value_p
        df.at[0, ("Baseline", "Assembly U-factor")] = roof_u_value_b
        st.dataframe(df, use_container_width=True)

        # -------------------------
        # Section 2 - Performance Outputs
        # -------------------------
        st.markdown('<div id="performance" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""",unsafe_allow_html=True)
        st.markdown(
            '<h5 style="color:red;">Performance Outputs</h5>',
            unsafe_allow_html=True
        )
        if uploaded_90_degree is not None and uploaded_180_degree is not None and uploaded_270_degree is not None:
            # if st.button("Generate Reports"):
            # st.write(ps_e_df_b)
            # st.write(bepu_df_b)
            st.markdown(
                """<div style='background-color:#fff3cd;padding:10px;border-left:6px solid #ffecb5;'>
                    <strong>Disclaimer:</strong> <br>1. This tool is used when completing baseline results for each of the four building orientations.<br>
                    2. This Tool looks at PS-E Meters and assumes all <strong>electric</strong> meters currently.
                    Units used are <strong>kWh</strong> (Consumption) and <strong>kW</strong> (Demand).
                </div><br>""",unsafe_allow_html=True)
            # ps_e.get_END_USE_Proposed(df, uploaded_0_degree, uploaded_90_degree, uploaded_180_degree, uploaded_270_degree, uploaded_proposed_file)
            sim_files = []
            sim_files.append(ps_e_df_b)
            sim_files.append(pse_90)
            sim_files.append(pse_180)
            sim_files.append(pse_270)
            sim_files.append(ps_e_proposed)

            end_use_map = {
                "Interior lighting": "LIGHTS",
                "Exterior lighting": "EXT USAGE",
                "Space heating": "SPACE_HEATING",
                "Space cooling": "SPACE_COOLING",
                "Pumps": "PUMPS & AUX",
                "Heat rejection": "HEAT_REJECT",
                "Fans - interior ventilation": "VENT FANS",
                "Service water heating": "DOMEST HOT WTR",
                "Receptacle equipment": ""
            }

            pse_dfs = []
            rotation_labels = [
                'Baseline 0° rotation',
                'Baseline 90° rotation',
                'Baseline 180° rotation',
                'Baseline 270° rotation',
                'Proposed'
            ]

            # ********************************************
            # FIX: Ensure rotation columns exist in df
            # ********************************************
            for col in rotation_labels:
                if col not in dfsss.columns:
                    dfsss[col] = None
            # ********************************************

            for i, sim_file in enumerate(sim_files):
                pse_df = sim_file
                # st.write(pse_df)

                pse_df_int_light_kwh = pse_df['LIGHTS'][0]
                pse_df_int_light_kw = pse_df['LIGHTS'][1]
                pse_df_ext_light_kwh = pse_df['EXT USAGE'][0]
                pse_df_ext_light_kw = pse_df['EXT USAGE'][1]
                pse_df_heat_kwh = pse_df['SPACE_HEATING'][0]
                pse_df_heat_kw = pse_df['SPACE_HEATING'][1]
                pse_df_cool_kwh = pse_df['SPACE_COOLING'][0]
                pse_df_cool_kw = pse_df['SPACE_COOLING'][1]
                pse_df_pumps_kwh = pse_df['PUMPS & AUX'][0]
                pse_df_pumps_kw = pse_df['PUMPS & AUX'][1]
                pse_df_heat_reject_kwh = pse_df['HEAT_REJECT'][0]
                pse_df_heat_reject_kw = pse_df['HEAT_REJECT'][1]
                pse_df_fans_kwh = pse_df['VENT FANS'][0]
                pse_df_fans_kw = pse_df['VENT FANS'][1]
                pse_df_wtr_kwh = pse_df['DOMEST HOT WTR'][0]
                pse_df_wtr_kw = pse_df['DOMEST HOT WTR'][1]
                pse_df_equip_kwh = pse_df['MISC_EQUIP'][0]
                pse_df_equip_kw = pse_df['MISC_EQUIP'][1]

                col = rotation_labels[i]
                # st.write(pse_df_cool_kw)

                dfsss[col][0] = float(pse_df_int_light_kwh)
                # st.write(dfsss[col][0])
                dfsss[col][1] = float(pse_df_int_light_kw)
                dfsss[col][2] = float(pse_df_ext_light_kwh)
                dfsss[col][3] = float(pse_df_ext_light_kw)
                dfsss[col][4] = float(pse_df_heat_kwh)
                dfsss[col][5] = float(pse_df_heat_kw)
                dfsss[col][6] = float(pse_df_cool_kwh)
                dfsss[col][7] = float(pse_df_cool_kw)
                dfsss[col][8] = float(pse_df_pumps_kwh)
                dfsss[col][9] = float(pse_df_pumps_kw)
                dfsss[col][10] = float(pse_df_heat_reject_kwh)
                dfsss[col][11] = float(pse_df_heat_reject_kw)
                dfsss[col][12] = float(pse_df_fans_kwh)
                dfsss[col][13] = float(pse_df_fans_kw)
                dfsss[col][16] = float(pse_df_wtr_kwh)
                dfsss[col][17] = float(pse_df_wtr_kw)
                dfsss[col][18] = float(pse_df_equip_kwh)
                dfsss[col][19] = float(pse_df_equip_kw)
            
            # st.write(dfsss)
            cols = [
                'Baseline 0° rotation',
                'Baseline 90° rotation',
                'Baseline 180° rotation',
                'Baseline 270° rotation',
                'Proposed'
            ]

            dfsss = dfsss.iloc[:, :-2]
            dfsss = dfsss.drop(dfsss.columns[1], axis=1)
            dfsss[cols] = dfsss[cols].apply(pd.to_numeric, errors='coerce')
            third_col_name = dfsss.columns[3]
            total_0_degree = dfsss.loc[dfsss[third_col_name] == 'Consumption (kWh)', 'Baseline 0° rotation'].sum()
            total_90_degree = dfsss.loc[dfsss[third_col_name] == 'Consumption (kWh)', 'Baseline 90° rotation'].sum()
            total_180_degree = dfsss.loc[dfsss[third_col_name] == 'Consumption (kWh)', 'Baseline 180° rotation'].sum()
            total_270_degree = dfsss.loc[dfsss[third_col_name] == 'Consumption (kWh)', 'Baseline 270° rotation'].sum()

            dfsss['Baseline 0° rotation'][49] = total_0_degree
            dfsss['Baseline 90° rotation'][49] = total_90_degree
            dfsss['Baseline 180° rotation'][49] = total_180_degree
            dfsss['Baseline 270° rotation'][49] = total_270_degree

            total_0_degree_therm = 0
            total_90_degree_therm = 0
            total_180_degree_therm = 0
            total_270_degree_therm = 0

            dfsss['Baseline 0° rotation'][50] = total_0_degree_therm
            dfsss['Baseline 90° rotation'][50] = total_90_degree_therm
            dfsss['Baseline 180° rotation'][50] = total_180_degree_therm
            dfsss['Baseline 270° rotation'][50] = total_270_degree_therm

            total_0_degree_mwh = 0
            total_90_degree_mwh = 0
            total_180_degree_mwh = 0
            total_270_degree_mwh = 0

            dfsss['Baseline 0° rotation'][51] = total_0_degree_mwh
            dfsss['Baseline 90° rotation'][51] = total_90_degree_mwh
            dfsss['Baseline 180° rotation'][51] = total_180_degree_mwh
            dfsss['Baseline 270° rotation'][51] = total_270_degree_mwh
            # st.write(dfsss)
            dfsss = dfsss.drop(columns=dfsss.columns[-2])
            cols_to_color = dfsss.columns[4:].tolist()
            # remove 2nd last column if it exists in this range
            # if len(cols_to_color) >= 2:
            #     cols_to_color.pop(-2)

            styled_df = (
                dfsss.style
                .format("{:.2f}", subset=dfsss.select_dtypes(include='number').columns)
                .set_properties(
                    subset=cols_to_color,
                    **{'background-color': '#E3F2FD'}
                )
            )
            st.dataframe(styled_df, use_container_width=True)

        # with st.expander("**🔴 Baseline Energy Summary by End Use**"):
        #     dfsss = dfsss.head(-2)
        #     dfsss = dfsss[dfsss.iloc[:, 3].notna() & (df.iloc[:, 3] != "")]
        #     df_ = dfsss
        #     dfsss = dfsss.iloc[:, :-2]
        #     dfsss = dfsss.iloc[:-4]
        #     st.dataframe(dfsss)

        # with st.expander("**🔴 Proposed Energy Summary by End Use**"):
        #     df_ = df_.iloc[:-4]
        #     cols_to_drop = df_.columns[-6:-1]
        #     df_proposed = df_.drop(columns=cols_to_drop)
        #     third_col_name = df_.columns[3]
        #     total_proposed = df_.loc[df_[third_col_name] == 'Consumption (kWh)', 'Proposed'].sum()
        #     st.write(df_proposed)

        else:
            st.info("Please upload all 4 rotation SIM files for Performance Outputs.")

        # -------------------------
        # Section 3 - Shading & Fenestration
        # -------------------------
        st.markdown('<div id="shade" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""",unsafe_allow_html=True)
        st.markdown(
            '<h5 style="color:red;">Shading & Fenestration</h5>',
            unsafe_allow_html=True
        )
        #     if st.button("Generate Reports"):
            # lv_d.generateFenestration(uploaded_0_degree, uploaded_proposed_file)
        north_wall_u       = safe_get_uvalue(lv_d_summ_b, 'NORTH',       column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        south_wall_u       = safe_get_uvalue(lv_d_summ_b, 'SOUTH',       column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        east_wall_u        = safe_get_uvalue(lv_d_summ_b, 'EAST',        column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        west_wall_u        = safe_get_uvalue(lv_d_summ_b, 'WEST',        column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        north_east_wall_u  = safe_get_uvalue(lv_d_summ_b, 'NORTH-EAST',  column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        south_east_wall_u  = safe_get_uvalue(lv_d_summ_b, 'SOUTH-EAST',  column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        south_west_wall_u  = safe_get_uvalue(lv_d_summ_b, 'SOUTH-WEST',  column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        north_west_wall_u  = safe_get_uvalue(lv_d_summ_b, 'NORTH-WEST',  column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        roof_wall_u        = safe_get_uvalue(lv_d_summ_b, 'ROOF',        column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        allWalls_wall_u    = safe_get_uvalue(lv_d_summ_b, 'ALL WALLS',   column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')
        undergrnd_wall_u   = safe_get_uvalue(lv_d_summ_b, 'UNDERGRND',   column='AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)')

        directions = [
            'NORTH', 'SOUTH', 'EAST', 'WEST',
            'NORTH-EAST', 'SOUTH-EAST', 'SOUTH-WEST', 'NORTH-WEST',
            'ROOF', 'ALL WALLS', 'UNDERGRND', 'WALLS+ROOFS'
        ]

        # ==============================
        #      BASELINE (B)
        # ==============================

        # Window Areas
        north_wind_area      = get_val(lv_d_summ_b, "NORTH",       "WINDOW(AREA)(SQFT)")
        south_wind_area      = get_val(lv_d_summ_b, "SOUTH",       "WINDOW(AREA)(SQFT)")
        east_wind_area       = get_val(lv_d_summ_b, "EAST",        "WINDOW(AREA)(SQFT)")
        west_wind_area       = get_val(lv_d_summ_b, "WEST",        "WINDOW(AREA)(SQFT)")
        north_east_wind_area = get_val(lv_d_summ_b, "NORTH-EAST",  "WINDOW(AREA)(SQFT)")
        south_east_wind_area = get_val(lv_d_summ_b, "SOUTH-EAST",  "WINDOW(AREA)(SQFT)")
        south_west_wind_area = get_val(lv_d_summ_b, "SOUTH-WEST",  "WINDOW(AREA)(SQFT)")
        north_west_wind_area = get_val(lv_d_summ_b, "NORTH-WEST",  "WINDOW(AREA)(SQFT)")
        roof_wind_area       = get_val(lv_d_summ_b, "ROOF",        "WINDOW(AREA)(SQFT)")
        allWalls_wind_area   = get_val(lv_d_summ_b, "ALL WALLS",   "WINDOW(AREA)(SQFT)")
        undergrnd_wind_area  = get_val(lv_d_summ_b, "UNDERGRND",   "WINDOW(AREA)(SQFT)")
        wall_roof_wind_area  = get_val(lv_d_summ_b, "WALLS+ROOFS", "WINDOW(AREA)(SQFT)")

        # Wall Areas
        north_wall_area      = get_val(lv_d_summ_b, "NORTH",      "WALL(AREA)(SQFT)")
        south_wall_area      = get_val(lv_d_summ_b, "SOUTH",      "WALL(AREA)(SQFT)")
        east_wall_area       = get_val(lv_d_summ_b, "EAST",       "WALL(AREA)(SQFT)")
        west_wall_area       = get_val(lv_d_summ_b, "WEST",       "WALL(AREA)(SQFT)")
        north_east_wall_area = get_val(lv_d_summ_b, "NORTH-EAST", "WALL(AREA)(SQFT)")
        south_east_wall_area = get_val(lv_d_summ_b, "SOUTH-EAST", "WALL(AREA)(SQFT)")
        south_west_wall_area = get_val(lv_d_summ_b, "SOUTH-WEST", "WALL(AREA)(SQFT)")
        north_west_wall_area = get_val(lv_d_summ_b, "NORTH-WEST", "WALL(AREA)(SQFT)")
        roof_wall_area       = get_val(lv_d_summ_b, "ROOF",       "WALL(AREA)(SQFT)")
        allWalls_wall_area   = get_val(lv_d_summ_b, "ALL WALLS",  "WALL(AREA)(SQFT)")
        undergrnd_wall_area  = get_val(lv_d_summ_b, "UNDERGRND",  "WALL(AREA)(SQFT)")


        # ==============================
        #      PROPOSED (P)
        # ==============================

        # Window U-values
        north_wind_u_p      = get_val(lv_d_summ_p, "NORTH",       "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        south_wind_u_p      = get_val(lv_d_summ_p, "SOUTH",       "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        east_wind_u_p       = get_val(lv_d_summ_p, "EAST",        "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        west_wind_u_p       = get_val(lv_d_summ_p, "WEST",        "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        north_east_wind_u_p = get_val(lv_d_summ_p, "NORTH-EAST",  "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        south_east_wind_u_p = get_val(lv_d_summ_p, "SOUTH-EAST",  "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        south_west_wind_u_p = get_val(lv_d_summ_p, "SOUTH-WEST",  "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        north_west_wind_u_p = get_val(lv_d_summ_p, "NORTH-WEST",  "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        roof_wind_u_p       = get_val(lv_d_summ_p, "ROOF",        "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        allWalls_wind_u_p   = get_val(lv_d_summ_p, "ALL WALLS",   "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")
        undergrnd_wind_u_p  = get_val(lv_d_summ_p, "UNDERGRND",   "AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)")


        # Wall U-values (Proposed)
        north_wall_u_p      = get_val(lv_d_summ_p, "NORTH",       "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        south_wall_u_p      = get_val(lv_d_summ_p, "SOUTH",       "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        east_wall_u_p       = get_val(lv_d_summ_p, "EAST",        "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        west_wall_u_p       = get_val(lv_d_summ_p, "WEST",        "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        north_east_wall_u_p = get_val(lv_d_summ_p, "NORTH-EAST",  "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        south_east_wall_u_p = get_val(lv_d_summ_p, "SOUTH-EAST",  "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        south_west_wall_u_p = get_val(lv_d_summ_p, "SOUTH-WEST",  "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        north_west_wall_u_p = get_val(lv_d_summ_p, "NORTH-WEST",  "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        roof_wall_u_p       = get_val(lv_d_summ_p, "ROOF",        "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        allWalls_wall_u_p   = get_val(lv_d_summ_p, "ALL WALLS",   "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")
        undergrnd_wall_u_p  = get_val(lv_d_summ_p, "UNDERGRND",   "AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)")


        # Proposed Window Areas
        north_wind_area_p      = get_val(lv_d_summ_p, "NORTH",       "WINDOW(AREA)(SQFT)")
        south_wind_area_p      = get_val(lv_d_summ_p, "SOUTH",       "WINDOW(AREA)(SQFT)")
        east_wind_area_p       = get_val(lv_d_summ_p, "EAST",        "WINDOW(AREA)(SQFT)")
        west_wind_area_p       = get_val(lv_d_summ_p, "WEST",        "WINDOW(AREA)(SQFT)")
        north_east_wind_area_p = get_val(lv_d_summ_p, "NORTH-EAST",  "WINDOW(AREA)(SQFT)")
        south_east_wind_area_p = get_val(lv_d_summ_p, "SOUTH-EAST",  "WINDOW(AREA)(SQFT)")
        south_west_wind_area_p = get_val(lv_d_summ_p, "SOUTH-WEST",  "WINDOW(AREA)(SQFT)")
        north_west_wind_area_p = get_val(lv_d_summ_p, "NORTH-WEST",  "WINDOW(AREA)(SQFT)")
        roof_wind_area_p       = get_val(lv_d_summ_p, "ROOF",        "WINDOW(AREA)(SQFT)")
        allWalls_wind_area_p   = get_val(lv_d_summ_p, "ALL WALLS",   "WINDOW(AREA)(SQFT)")
        undergrnd_wind_area_p  = get_val(lv_d_summ_p, "UNDERGRND",   "WINDOW(AREA)(SQFT)")
        wall_roof_wind_area_p  = get_val(lv_d_summ_p, "WALLS+ROOFS", "WINDOW(AREA)(SQFT)")

        north_wind_area = float(north_wind_area) + float(north_east_wind_area)
        east_wind_area = float(east_wind_area) + float(south_east_wind_area)
        south_wind_area = float(south_wind_area) + float(south_west_wind_area)
        west_wind_area = float(west_wind_area) + float(north_west_wind_area)
        ag_wind_area = (north_wind_area + east_wind_area + south_wind_area + west_wind_area)

        north_wall_area = float(north_wall_area) + float(north_east_wall_area)
        east_wall_area = float(east_wall_area) + float(south_east_wall_area)
        south_wall_area = float(south_wall_area) + float(south_west_wall_area)
        west_wall_area = float(west_wall_area) + float(north_west_wall_area)
        ag_wall_area = (north_wall_area + east_wall_area + south_wall_area + west_wall_area)

        north_wind_area_p = float(north_wind_area_p) + float(north_east_wind_area_p)
        east_wind_area_p = float(east_wind_area_p) + float(south_east_wind_area_p)
        south_wind_area_p = float(south_wind_area_p) + float(south_west_wind_area_p)
        west_wind_area_p = float(west_wind_area_p) + float(north_west_wind_area_p)
        ag_wind_area_p = (north_wind_area_p + east_wind_area_p + south_wind_area_p + west_wind_area_p)

        columns = pd.MultiIndex.from_tuples([
            ("", "Orientation"),
            ("Baseline", "Above-Grade Wall Area (sq m)"),
            ("Baseline", "Vertical Glazing Area (sq m)"),
            ("Baseline", "Vertical Glazing Area (%)"),
            ("Proposed", "Above-Grade Wall Area (sq m)"),
            ("Proposed", "Vertical Glazing Area (sq m)"),
            ("Proposed", "Vertical Glazing Area (%)"),
        ])

        data = [
            ["North", round(north_wall_area*0.092903,2), round(north_wind_area*0.092903,2), round(round(north_wind_area*0.092903,2)*100/round(north_wall_area*0.092903,2),2), "Identical to baseline", round(north_wind_area_p*0.092903,2), round(round(north_wind_area_p*0.092903,2)*100/round(north_wall_area*0.092903,2),2)],
            ["East", round(east_wall_area*0.092903,2), round(east_wind_area*0.092903,2), round(round(east_wind_area*0.092903,2)*100/round(east_wall_area*0.092903,2),2), "Identical to baseline", round(east_wind_area_p*0.092903,2), round(round(east_wind_area_p*0.092903,2)*100/round(east_wall_area*0.092903,2),2)],
            ["South", round(south_wall_area*0.092903,2), round(south_wind_area*0.092903,2), round(round(south_wind_area*0.092903,2)*100/round(south_wall_area*0.092903,2),2), "Identical to baseline", round(south_wind_area_p*0.092903,2), round(round(south_wind_area_p*0.092903,2)*100/round(south_wall_area*0.092903,2),2)],
            ["West", round(west_wall_area*0.092903,2), round(west_wind_area*0.092903,2), round(round(west_wind_area*0.092903,2)*100/round(west_wall_area*0.092903,2),2), "Identical to baseline", round(west_wind_area_p*0.092903,2), round(round(west_wind_area_p*0.092903,2)*100/round(west_wall_area*0.092903,2),2)],
            ["Total", round(ag_wall_area*0.092903,2), round(ag_wind_area*0.092903,2), round(round(ag_wind_area*0.092903,2)*100/round(ag_wall_area*0.092903,2),2), round(ag_wall_area*0.092903,2), round(ag_wind_area_p*0.092903,2), round(round(ag_wind_area_p*0.092903,2)*100/round(ag_wall_area*0.092903,2),2)],
        ]

        df = pd.DataFrame(data, columns=columns)
        numeric_columns = [
            ("Baseline", "Above-Grade Wall Area (sq m)"),
            ("Baseline", "Vertical Glazing Area (sq m)"),
            ("Baseline", "Vertical Glazing Area (%)"),
            ("Proposed", "Above-Grade Wall Area (sq m)"),
            ("Proposed", "Vertical Glazing Area (sq m)"),
            ("Proposed", "Vertical Glazing Area (%)"),
        ]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.fillna(0, inplace=True)

        df1 = pd.DataFrame(data, columns=columns)
        columns2 = pd.MultiIndex.from_tuples([
            ("", "Roof Area (sq m)"),
            ("", "Skylight Area (sq m)"),
            ("Baseline", "Conditioned"),
            ("Baseline", "Semi-heated"),
            ("Baseline", "Unconditioned"),
            ("Proposed", "Conditioned"),
            ("Proposed", "Semi-heated"),
            ("Proposed", "Unconditioned"),
        ])

        if wall_roof_wind_area != allWalls_wind_area:
            diff_area = wall_roof_wind_area - allWalls_wind_area
        else:
            diff_area = 0
        converted_area = round(float(diff_area) * 0.092903, 2)

        conditioned_count_base = (sv_a_zone_df['SUPPLY-FLOW(CFM)'] != 0).sum()
        unconditioned_count_base = (sv_a_zone_df['SUPPLY-FLOW(CFM)'] == 0).sum() 
        conditioned_count_pro = (sv_a_zone_df['SUPPLY-FLOW(CFM)'] != 0).sum()
        unconditioned_count_pro = (sv_a_zone_df['SUPPLY-FLOW(CFM)'] == 0).sum()

        data_row = [
            round(float(roof_wall_area)*0.092903, 2),  # Converted area
            roof_wind_area,                            # Roof window area
            conditioned_count_base,                   # Conditioned base
            "",                                       # Placeholder for condition comparison
            unconditioned_count_base,                 # Unconditioned base
            "", "", ""                                # Remaining placeholders
        ]

        # Fill "Identical to Baseline" if applicable
        if conditioned_count_base == conditioned_count_pro:
            data_row[5] = "Identical to Baseline"

        if unconditioned_count_base == unconditioned_count_pro:
            data_row[7] = "Identical to Baseline"

        data2 = [data_row]

        df2 = pd.DataFrame(data2, columns=columns2)
        st.markdown("""<h6 style="color:red;">🔴 Shading</h6>""", unsafe_allow_html=True)
        st.write("Above-grade Wall and Glazing")
        # st.write(df1)
        styled_df = (
            df1.style
            .format("{:.2f}", subset=df1.select_dtypes(include='number').columns)
            .set_properties(
                subset=df1.columns[1:],
                **{'background-color': '#E3F2FD'}
            )
        )
        st.dataframe(styled_df, use_container_width=True)
        if df1['Proposed']['Vertical Glazing Area (%)'][4] < 40.0 or df1['Baseline']['Vertical Glazing Area (%)'][4] < 40:
            st.info("ℹ️ The vertical glazing percentage is below 40%, supporting good thermal performance.")

        st.write("Roof/Skylight & Thermal Blocks")
        styled_df = (
            df2.style
            .format("{:.2f}", subset=df2.select_dtypes(include='number').columns)
            .set_properties(
                subset=df2.columns[0:],
                **{'background-color': '#E3F2FD'}
            )
        )
        st.dataframe(styled_df, use_container_width=True)

        # st.markdown("""<h6 style="color:red;">🔴 Fenestration</h6>""", unsafe_allow_html=True)
        columns = pd.MultiIndex.from_tuples([
            ("General Information", "Building ID"),
            ("General Information", "New or Existing Construction"),
            ("General Information", "Space-Conditioning Category"),
            ("Baseline", "Description"),
            ("Baseline", "Assembly U-factor"),
            ("Baseline", "SHGC"),
            ("Proposed", "Description"),
            ("Proposed", "Assembly U-factor"),
            ("Proposed", "SHGC"),
            ("Proposed", "VLT"),
        ])

        data = [[
            "",  # Building ID
            "",                                # New or Existing Construction
            "",                     # Space-Conditioning Category
            "",            # Baseline Description
            "",                                 # Baseline U-factor
            "",                                 # Baseline SHGC
            "",                                # Proposed Description
            "",                                  # Proposed U-factor
            "",                                 # Proposed SHGC
            ""                                   # Proposed VLT
        ]]
        dfss = pd.DataFrame(data, columns=columns)

        # -------------------------
        # Section 4 - Schedules
        # -------------------------
        st.markdown('<div id="schedules" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""",unsafe_allow_html=True)
        st.markdown('<h5 style="color:red;">Schedules</h5>',unsafe_allow_html=True)

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
            # st.write(lv_g_baseline)
            # st.write(lv_g_proposed)
            subset_b = lv_g_baseline.iloc[:, :24]
            numeric_subset_b = subset_b.apply(pd.to_numeric, errors='coerce')
            subset_p = lv_g_baseline.iloc[:, :24]
            numeric_subset_p = subset_p.apply(pd.to_numeric, errors='coerce')
            lv_g_baseline['Hours / Day'] = numeric_subset_b.sum(axis=1)
            lv_g_proposed['Hours / Day'] = numeric_subset_p.sum(axis=1)

            holiday = holiday
            weekday = monday + tuesday + wednesday + thursday + friday
            weekend = saturday + sunday

            def get_multiplier(day_type):
                day_type = str(day_type).upper()
                if 'HOL' in day_type:
                    return holiday
                elif 'SAT' in day_type:
                    return weekend
                elif 'CDD' in day_type:
                    return weekday
                else:
                    return weekday

            lv_g_baseline['Hours / Year'] = lv_g_baseline.apply(lambda row: row['Hours / Day'] * get_multiplier(row['Day Type']), axis=1)
            lv_g_proposed['Hours / Year'] = lv_g_proposed.apply(lambda row: row['Hours / Day'] * get_multiplier(row['Day Type']), axis=1)

            numeric_cols = lv_g_baseline.columns.difference(['Schedule'])
            result_baseline = pd.DataFrame(columns=lv_g_baseline.columns)
            numeric_cols_p = lv_g_proposed.columns.difference(['Schedule'])
            result_proposed = pd.DataFrame(columns=lv_g_proposed.columns)

            cols = lv_g_baseline.columns.tolist()
            second_last_col = cols[-2]
            last_col = cols[-1]
            cols_p = lv_g_proposed.columns.tolist()
            second_last_col_p = cols_p[-2]
            last_col_p = cols_p[-1]

            for name, group in lv_g_baseline.groupby('Schedule'):
                result_baseline = pd.concat([result_baseline, group], ignore_index=True)
                total_values = group[numeric_cols].sum()
                total_row = pd.Series("", index=lv_g_baseline.columns)
                total_row['Schedule'] = 'Total hours of operation'
                total_row[second_last_col] = total_values[second_last_col]
                total_row[last_col] = total_values[last_col]
                result_baseline = pd.concat([result_baseline, pd.DataFrame([total_row])], ignore_index=True)
            
            for name, group in lv_g_proposed.groupby('Schedule'):
                result_proposed = pd.concat([result_proposed, group], ignore_index=True)
                total_values = group[numeric_cols_p].sum()
                total_row_p = pd.Series("", index=lv_g_proposed.columns)
                total_row_p['Schedule'] = 'Total hours of operation'
                total_row_p[second_last_col] = total_values[second_last_col_p]
                total_row_p[last_col_p] = total_values[last_col_p]
                result_proposed = pd.concat([result_proposed, pd.DataFrame([total_row_p])], ignore_index=True)
            total_days = sum([holiday, monday, tuesday, wednesday, thursday, friday, saturday, sunday])
            data = {
                "Days per Year": [
                    holiday,
                    monday,
                    tuesday,
                    wednesday,
                    thursday,
                    friday,
                    saturday,
                    sunday,
                    total_days
                ]
            }
            index = ["Holiday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Total (must equal 365 days/year)"]
            days_ = pd.DataFrame(data, index=index)
            st.markdown("<h6 style='color: red;'>🔰 Yearly Schedule Allocation</h3>", unsafe_allow_html=True)
            st.write(days_)
            st.markdown("<h6 style='color: red;'>🗂️ Baseline LV-G Report - Details of Schedules</h3>", unsafe_allow_html=True)
            st.write(result_baseline)
            st.markdown("<h6 style='color: red;'>🗂️ Proposed LV-G Report - Details of Schedules</h3>", unsafe_allow_html=True)
            st.write(result_proposed)
        else:
            st.error("❌ Total days must equal 365.")

        # -------------------------
        # Section 5 - Lighting
        # -------------------------
        st.markdown('<div id="lighting" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""",unsafe_allow_html=True)
        st.markdown('<h5 style="color:red;">Lighting Loads Summary</h5>', unsafe_allow_html=True)

        if summary_df is not None:
            summary_df.drop(columns=["EQUIP(WATT / SOFT)"], inplace=True, errors="ignore")
            summary_df.drop(columns=["Baseline Modeled Identically"], inplace=True, errors="ignore")

            summary_df = summary_df.rename(columns={"LIGHTS(WATT / SOFT)": "Design LPD(W/ft²)", "AREA(SQFT)": "Area(ft²)"})
            if "Design LPD(W/ft²)" in summary_df.columns:
                summary_df["Modeled Design LPD(W/ft²)"] = summary_df["Design LPD(W/ft²)"]
                # Reorder columns (swap A and B)
                cols = list(summary_df.columns) 
                a_idx, b_idx = cols.index("Design LPD(W/ft²)"), cols.index("LIGHTS(WATT / SOFT) (Baseline)")
                cols[a_idx], cols[b_idx] = cols[b_idx], cols[a_idx]
                summary_df = summary_df[cols]
                summary_df = summary_df.rename(columns={"LIGHTS(WATT / SOFT) (Baseline)": "Maximum Allowance(W/ft²)"})
                summary_df.insert(3, "Total Baseline LPD Allowance(W/ft²)", summary_df["Maximum Allowance(W/ft²)"])
                last4_grouped = summary_df.copy()
                last4_grouped.columns = pd.MultiIndex.from_tuples([
                    ("", "Building Type"),
                    ("", "Area(ft²)"),
                    ("Baseline", "Maximum Allowance(W/ft²)"),
                    ("Baseline", "Total Baseline LPD Allowance(W/ft²)"),
                    ("Proposed", "Design LPD(W/ft²)"),
                    ("Proposed", "Modeled Design LPD(W/ft²)")
                ])
                # st.dataframe(last4_grouped)
                styled_df = (
                    last4_grouped.style
                    .format("{:.2f}", subset=last4_grouped.select_dtypes(include='number').columns)
                    .set_properties(
                        subset=last4_grouped.columns[1:],
                        **{'background-color': '#E3F2FD'}
                    )
                )
                st.dataframe(styled_df, use_container_width=True)
            elif "Design LPD(W/ft²)" not in summary_df.columns:
                styled_df = (
                    summary_df.style
                    .format("{:.2f}", subset=summary_df.select_dtypes(include='number').columns)
                    .set_properties(
                        subset=summary_df.columns[1:],
                        **{'background-color': '#E3F2FD'}
                    )
                )
                st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("Moving to next")

        # -------------------------
        # Section 6 - Calculator
        # -------------------------
        st.markdown('<div id="loads" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""",unsafe_allow_html=True)
        st.markdown(
            '<h5 style="color:red;">Process Loads Summary</h5>',
            unsafe_allow_html=True
        )
        st.markdown("""
            When transferring data to the **MEPC Sheet**, copy the first **‘Building Type’** column the second blank **‘Building Type’** column and then paste them into the **‘Building Type’** cells in MEPC sheet.  
            """)
        if "EQUIP(WATT / SOFT)" in summary_df.columns:
            summary_df.drop(columns=["LIGHTS(WATT / SOFT)"], inplace=True, errors="ignore")
            summary_df.drop(columns=["LIGHTS(WATT / SOFT) (Baseline)"], inplace=True, errors="ignore")
            summary_df.insert(summary_df.columns.get_loc("Building Type")+1, "Building Type ", "")
            
            result = round((summary_df["AREA(SQFT)"] * summary_df["EQUIP(WATT / SOFT)"]).sum() / 1000, 2)
            new_row = {
                "Building Type": "Total power modeled using space by space method(kW)",
                "Baseline Modeled Identically": result
            }

            summary_df = pd.concat([summary_df, pd.DataFrame([new_row])], ignore_index=True)
            summary_df = summary_df.rename(columns={"EQUIP(WATT / SOFT)": "Equipment Power Density(W/ft²)", "AREA(SQFT)": "Area(ft²)"})
            
            styled_df = (
                summary_df.style
                .format("{:.2f}", subset=summary_df.select_dtypes(include='number').columns)
                .set_properties(
                    subset=summary_df.columns[1:],
                    **{'background-color': '#E3F2FD'}
                )
            )
            st.dataframe(styled_df, use_container_width=True)
        elif "EQUIP(WATT / SOFT)" not in summary_df.columns:
            styled_df = (
                summary_df.style
                .format("{:.2f}", subset=summary_df.select_dtypes(include='number').columns)
                .set_properties(
                    subset=summary_df.columns[1:],
                    **{'background-color': '#E3F2FD'}
                )
            )
            st.dataframe(styled_df, use_container_width=True)
        
        # -------------------------
        # Section 7 - Air-Side HVAC
        # -------------------------
        st.markdown('<div id="hvac-air" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""", unsafe_allow_html=True)
        st.markdown('<h5 style="color:red;">Air-Side HVAC</h5>',unsafe_allow_html=True)

        hvac_path = r'MEP_Calculator/database/HVAC_DB.xlsx'
        df_units = pd.read_excel(hvac_path, sheet_name="UnitsMap")
        system_map = pd.read_excel(hvac_path, sheet_name="SystemRanges")

        # static system number
        system = 2
        total_cooling = float(pd.to_numeric(sv_a_df['COOLING_CAPACITY(KBTU/HR)'], errors='coerce').sum())
        total_heating = float(pd.to_numeric(sv_a_df['HEATING_CAPACITY(KBTU/HR)'], errors='coerce').sum())

        # Base table
        data = [
            {"Model Input Parameter": "Total cooling capacity", "Units": "kBtu/h", "Baseline - Total": 0, "Proposed - Total": 0},
            {"Model Input Parameter": "* Table 6.8.1 Unitary Cooling (Systems 1 through 6)", "Units": "kBtu/h", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Unitary cooling efficiency", "Units": "EER", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Unitary cooling part-load efficiency (if applicable)", "Units": "", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Total heating capacity", "Units": "kBtu/h", "Baseline - Total": 0, "Proposed - Total": 0},
            {"Model Input Parameter": "* Table 6.8.1 Unitary Heating (Systems 2, 3, 4, and 9)", "Units": "kBtu/h", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Unitary heating efficiency", "Units": "EER", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "* Fan control", "Units": "", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Supply airflow", "Units": "cfm", "Baseline - Total": 0, "Proposed - Total": 0},
            {"Model Input Parameter": "Outdoor airflow", "Units": "cfm", "Baseline - Total": 0, "Proposed - Total": 0},
            {"Model Input Parameter": "Demand control ventilation", "Units": "n/a", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "* Economizer high-limit shutoff", "Units": "", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "* Supply air temperature reset", "Units": "n/a", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "* Energy Recovery per 6.5.6.1", "Units": "n/a", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Exhaust air energy recovery effectiveness or 6.5.6.1 exception claimed", "Units": "% energy recovery effectiveness", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Fan Power - Supply fan power", "Units": "kW", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Fan Power - Return or relief fan power", "Units": "kW", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Fan Power - Exhaust fan power", "Units": "kW", "Baseline - Total": "", "Proposed - Total": ""},
            {"Model Input Parameter": "Fan Power - System fan power", "Units": "kW", "Baseline - Total": 0, "Proposed - Total": 0},
            {"Model Input Parameter": "Fan Power - Allowed fan power", "Units": "kW", "Baseline - Total": "", "Proposed - Total": ""},
        ]

        df = pd.DataFrame(data)

        # --------------------------------
        # Add dynamic Baseline/Proposed columns
        # --------------------------------
        num_cols = len(sv_a_df)
        num_cols_p = len(sv_a_df_p)
        for i in range(1, num_cols + 1):
            df[f"Baseline - {i}"] = ""
        for i in range(1, num_cols_p + 1):
            df[f"Proposed - {i}"] = ""

        # SYSTEM TYPE row
        system_types = sv_a_df["SYSTEM_TYPE"].astype(str).tolist() if "SYSTEM_TYPE" in sv_a_df.columns else [""] * num_cols
        system_types_p = sv_a_df_p["SYSTEM_TYPE"].astype(str).tolist() if "SYSTEM_TYPE" in sv_a_df_p.columns else [""] * num_cols_p
        system_row = {"Model Input Parameter": "SYSTEM TYPE", "Units": ""}

        for i in range(1, num_cols + 1):
            val = system_types[i - 1]
            system_row[f"Baseline - {i}"] = val
        for i in range(1, num_cols_p + 1):
            valp = system_types_p[i - 1]
            system_row[f"Proposed - {i}"] = valp

        df = pd.concat([pd.DataFrame([system_row]), df], ignore_index=True)
        
        # -------------------------
        # ROW INDEX after SYSTEM TYPE
        # -------------------------
        cooling_row = 1
        cooling_map_row = 2
        cooling_eff_row = 3
        cooling_eir = 4
        heating_row = 5
        heating_map_row = 6
        heating_eff_row = 7
        fan_control_row = 8
        supply_row = 9
        outdoor_row = 10
        fan_power_row = 16

        # -------------------------
        # COOLING VALUES
        # -------------------------
        cooling_values = sv_a_df["COOLING_CAPACITY(KBTU/HR)"].tolist()
        cooling_values_p = sv_a_df_p["COOLING_CAPACITY(KBTU/HR)"].tolist()
        for i, val in enumerate(cooling_values, start=1):
            df.at[cooling_row, f"Baseline - {i}"] = val

            sys_col = f"System{system}"
            mapped_value = ""
            for _, row in system_map.iterrows():
                condition = str(row.get(sys_col, "")).strip()
                if condition and condition not in ["N/A", "All capacities"]:
                    expr = condition.replace("and", "&")
                    try:
                        if eval(str(val) + expr):
                            mapped_value = condition
                            break
                    except:
                        pass
                elif condition == "All capacities":
                    mapped_value = condition
                    break
            df.at[cooling_map_row, f"Baseline - {i}"] = mapped_value
        
        for i, val in enumerate(cooling_values_p, start=1):
            df.at[cooling_row, f"Proposed - {i}"] = val

            sys_col = f"System{system}"
            mapped_value = ""
            for _, row in system_map.iterrows():
                condition = str(row.get(sys_col, "")).strip()
                if condition and condition not in ["N/A", "All capacities"]:
                    expr = condition.replace("and", "&")
                    try:
                        if eval(str(val) + expr):
                            mapped_value = condition
                            break
                    except:
                        pass
                elif condition == "All capacities":
                    mapped_value = condition
                    break
            df.at[cooling_map_row, f"Proposed - {i}"] = "NA"

        # -------------------------
        # UNITARY COOLING EFFICIENCY
        # -------------------------
        for i, cap in enumerate(cooling_values, start=1):
            eff = ""
            for _, r in df_units.iterrows():
                rng = str(r.get("CoolingRange", "")).strip()
                if rng and rng != "N/A":
                    expr = rng.replace("and", "&")
                    try:
                        if eval(str(cap) + expr):
                            eff = r.get("CoolingEfficiency", "")
                            break
                    except:
                        pass
            df.at[cooling_eff_row, f"Baseline - {i}"] = eff
        
        for i, cap in enumerate(cooling_values_p, start=1):
            eff = ""
            for _, r in df_units.iterrows():
                rng = str(r.get("CoolingRange", "")).strip()
                if rng and rng != "N/A":
                    expr = rng.replace("and", "&")
                    try:
                        if eval(str(cap) + expr):
                            eff = r.get("CoolingEfficiency", "")
                            break
                    except:
                        pass
            df.at[cooling_eff_row, f"Proposed - {i}"] = "NA"

        # -------------------------
        # HEATING VALUES
        # -------------------------
        heating_values = sv_a_df["HEATING_CAPACITY(KBTU/HR)"].tolist()
        heating_values_p = sv_a_df_p["HEATING_CAPACITY(KBTU/HR)"].tolist()
        for i, val in enumerate(heating_values, start=1):
            df.at[heating_row, f"Baseline - {i}"] = val

            sys_col1 = f"System{system}"
            mapped_value = ""
            for _, row in system_map.iterrows():
                condition = str(row.get(sys_col1, "")).strip()
                if condition and condition not in ["N/A", "All capacities"]:
                    expr = condition.replace("and", "&")
                    try:
                        if eval(str(val) + expr):
                            mapped_value = condition
                            break
                    except:
                        pass
                elif condition == "All capacities":
                    mapped_value = condition
                    break
            df.at[heating_map_row, f"Baseline - {i}"] = mapped_value
        for i, val in enumerate(heating_values_p, start=1):
            df.at[heating_row, f"Proposed - {i}"] = val
            sys_col1 = f"System{system}"
            mapped_value = ""
            for _, row in system_map.iterrows():
                condition = str(row.get(sys_col1, "")).strip()
                if condition and condition not in ["N/A", "All capacities"]:
                    expr = condition.replace("and", "&")
                    try:
                        if eval(str(val) + expr):
                            mapped_value = condition
                            break
                    except:
                        pass
                elif condition == "All capacities":
                    mapped_value = condition
                    break
            df.at[heating_map_row, f"Proposed - {i}"] = "NA"

        # -------------------------
        # UNITARY HEATING EFFICIENCY
        # -------------------------
        for i, cap in enumerate(heating_values, start=1):
            eff = ""
            for _, r in df_units.iterrows():
                rng = str(r.get("HeatingRange", "")).strip()
                if rng and rng != "N/A":
                    expr = rng.replace("and", "&")
                    try:
                        if eval(str(cap) + expr):
                            eff = r.get("HeatingEfficiency", "")
                            break
                    except:
                        pass
            df.at[heating_eff_row, f"Baseline - {i}"] = eff
            df.at[heating_eff_row, f"Proposed - {i}"] = eff

        # -------------------------
        # FAN CONTROL
        # -------------------------
        fanc = "Variable Speed" if 5 <= system <= 8 else "Constant Speed"
        fanc_p = "Variable Speed" if 5 <= system <= 8 else "Constant Volume"
        for i in range(1, num_cols + 1):
            df.at[fan_control_row, f"Baseline - {i}"] = fanc
        for i in range(1, num_cols_p + 1):
            df.at[fan_control_row, f"Proposed - {i}"] = fanc_p

        # -------------------------
        # AIRFLOW VALUES
        # -------------------------
        supply_airflow = pd.to_numeric(sv_a_zone_df.get("SUPPLY-FLOW(CFM)", 0), errors="coerce").sum()
        outside_airflow = pd.to_numeric(sv_a_zone_df.get("OUTISIDE-AIR-FLOW(CFM)", 0), errors="coerce").sum()
        supply_fan = pd.to_numeric(sv_a_zone_df.get("FAN(KW)", 0), errors="coerce").sum()

        for i in range(1, num_cols + 1):
            df.at[supply_row, f"Baseline - {i}"] = supply_airflow
            df.at[outdoor_row, f"Baseline - {i}"] = outside_airflow
            df.at[fan_power_row, f"Baseline - {i}"] = round(supply_fan,2)
        for i in range(1, num_cols_p + 1):
            df.at[supply_row, f"Proposed - {i}"] = supply_airflow
            df.at[outdoor_row, f"Proposed - {i}"] = outside_airflow
            df.at[fan_power_row, f"Proposed - {i}"] = round(supply_fan,2)

        # -------------------------
        # CALCULATE TOTALS
        # -------------------------
        baseline_cols = [c for c in df.columns if c.startswith("Baseline - ") and c != "Baseline - Total"]
        proposed_cols = [c for c in df.columns if c.startswith("Proposed - ") and c != "Proposed - Total"]

        for idx in range(len(df)):
            bvals = pd.to_numeric(df.loc[idx, baseline_cols], errors="coerce")
            pvals = pd.to_numeric(df.loc[idx, proposed_cols], errors="coerce")
            if bvals.notna().any():
                df.at[idx, "Baseline - Total"] = bvals.sum()
            if pvals.notna().any():
                df.at[idx, "Proposed - Total"] = pvals.sum()

        # ----------------------------------------------------
        # REORDER COLUMNS:
        # Baseline-Total → Proposed-Total → Baseline-i → Proposed-i
        # ----------------------------------------------------
        base_total = ["Baseline - Total"]
        prop_total = ["Proposed - Total"]

        baseline_i = sorted([c for c in df.columns if c.startswith("Baseline - ") and c not in base_total],
                            key=lambda x: int(x.split(" - ")[1]))

        proposed_i = sorted([c for c in df.columns if c.startswith("Proposed - ") and c not in prop_total],
                            key=lambda x: int(x.split(" - ")[1]))

        # First include non-baseline/proposed columns
        other_cols = [c for c in df.columns if not c.startswith("Baseline - ") and not c.startswith("Proposed - ")]

        # Final order:
        # Model Input Parameter | Units | Baseline-Total | Proposed-Total | Baseline-i... | Proposed-i...
        new_order = other_cols + base_total + prop_total + baseline_i + proposed_i

        df = df[new_order]
        # ---------------------------------------
        # INSERT BLANK ROW AS 2nd ROW
        # ---------------------------------------
        blank_row = {col: "" for col in df.columns}
        df = pd.concat([df.iloc[:1], pd.DataFrame([blank_row]), df.iloc[1:]], ignore_index=True)

        # ---------------------------------------
        # FILL 2nd ROW → Equivalent ASHRAE SYSTEM
        # ---------------------------------------

        # Mapping rules
        ashrae_map = {
            "PTAC": lambda h, c: "Sys1" if h == 0 else "Sys2",
            "PSZ":  lambda h, c: "Sys3" if h == 0 else "Sys4",
            "PVAVS": lambda h, c: "Sys5",
            "PIU": lambda h, c: "Sys6" if c > 0 else "Sys8",
            "VAVS": lambda h, c: "Sys7" if c == 0 else "Sys7",
        }

        df.at[1, "Model Input Parameter"] = "Equivalent ASHRAE System"
        df.at[1, "Units"] = ""

        # Fill values for each Baseline-i / Proposed-i
        for i in range(1, num_cols + 1):

            sys_type = sv_a_df.loc[i-1, "SYSTEM_TYPE"]
            h_eir = float(sv_a_df.loc[i-1, "HEATING_EIR(BTU/BTU)"])
            c_eir = float(sv_a_df.loc[i-1, "COOLING_EIR(BTU/BTU)"])
            if sys_type in ashrae_map:
                val = ashrae_map[sys_type](h_eir, c_eir)
            else:
                val = ""

            df.at[1, f"Baseline - {i}"] = val
            if c_eir == 0 or pd.isna(c_eir):
                df.at[4, f"Baseline - {i}"] = ""
            else:
                df.at[4, f"Baseline - {i}"] = round(3.412142/c_eir,2)
            
            if h_eir == 0 or pd.isna(h_eir):
                df.at[8, f"Baseline - {i}"] = ""
            else:
                df.at[8, f"Baseline - {i}"] = round(3.412142/h_eir,2)
            df.at[5, f"Baseline - {i}"] = "NA"
            df.at[12, f"Baseline - {i}"] = "No"
            df.at[13, f"Baseline - {i}"] = "Not Required"
            df.at[14, f"Baseline - {i}"] = "Not Required"
            df.at[15, f"Baseline - {i}"] = "No"
            df.at[16, f"Baseline - {i}"] = "NA"
        
        for i in range(1, num_cols_p + 1):
            sys_type_p = sv_a_df_p.loc[i-1, "SYSTEM_TYPE"]
            h_eir_p = float(sv_a_df_p.loc[i-1, "HEATING_EIR(BTU/BTU)"])
            c_eir_p = float(sv_a_df_p.loc[i-1, "COOLING_EIR(BTU/BTU)"])
            if sys_type_p in ashrae_map:
                val_p = ashrae_map[sys_type_p](h_eir_p, c_eir_p)
            else:
                val_p = ""
            df.at[1, f"Proposed - {i}"] = val_p
            if c_eir_p == 0 or pd.isna(c_eir_p):
                df.at[4, f"Proposed - {i}"] = ""
            else:
                df.at[4, f"Proposed - {i}"] = round(3.412142 / c_eir_p, 2)
            if h_eir_p == 0 or pd.isna(h_eir_p):
                df.at[8, f"Proposed - {i}"] = ""
            else:
                df.at[8, f"Proposed - {i}"] = round(3.412142/h_eir_p,2)
            df.at[5, f"Proposed - {i}"] = "NA"
            df.at[12, f"Proposed - {i}"] = "No"
            df.at[13, f"Proposed - {i}"] = "Not Required"
            df.at[14, f"Proposed - {i}"] = "Not Required"
            df.at[15, f"Proposed - {i}"] = "No"
            df.at[16, f"Proposed - {i}"] = "NA"
        df = df[:-4]

        # -------------------------
        # DISPLAY
        # -------------------------

        # Identify columns where first row == "SUM"
        sum_columns = [col for col in df.columns if str(df.iloc[0][col]).strip().upper() == "SUM"]

        # # Filter dataframe
        # if show_sum:
        #     df_filtered = df.copy()
        # else:
        df_filtered = df.drop(columns=sum_columns)
        df_filtered = df_filtered.apply(
            lambda col: pd.to_numeric(col, errors='ignore').round(1)
            if pd.api.types.is_numeric_dtype(pd.to_numeric(col, errors='ignore'))
            else col
        )
        styled_df = df_filtered.style.set_properties(
            subset=df_filtered.columns[4:],
            **{'background-color': '#E3F2FD;'}
        )
        
        # Data editor
        edited_df = st.data_editor(
            styled_df,
            hide_index=True,
            use_container_width=True,
            key="editor_no_sum"  # Unique key prevents duplicate ID issue
        )

        # -------------------------
        # Section 8 - Water-Side HVAC
        # -------------------------
        st.markdown('<div id="hvac-water" class="section"></div>', unsafe_allow_html=True)
        st.markdown("""<br><br><br>""", unsafe_allow_html=True)
        st.markdown('<h5 style="color:red;">Water-Side HVAC</h5>', unsafe_allow_html=True)
        st.markdown('<h7 style="color:red;">Chilled Water</h7>', unsafe_allow_html=True)
        # st.write(pva_df)
        if pva_primary.empty == True:
            st.info("No chilled water data found in Water-Side HVAC.")
        else:
            # -----------------------------
            # MODEL INPUTS + UNITS
            # -----------------------------
            model_inputs = [
                "Number and type of chillers (and capacity per chiller if more than one type or size of chiller)",
                "Purchased chilled water rate (cost per unit energy)",
                "Total chiller capacity",
                "Chiller efficiency - full load",
                "Chiller efficiency - part load",
                "Chilled water (CHW) supply temp",
                "CHW ΔT",
                "CHW supply temp reset parameters",
                "CHW loop configuration",
                "Number of primary or DES plant CHW pumps",
                "Primary or DES plant CHW pump power",
                "Primary or DES plant CHW pump flow",
                "Primary or DES plant CHW pump control",
                "Number of secondary or building booster CHW pumps",
                "Secondary or building booster CHW pump power",
                "Secondary or building booster CHW pump flow",
                "Secondary or building booster CHW pump control",
                "Water-side economizer",
                "Water-side energy recovery"
            ]

            units = [
                "n/a","$","tons","COP","IPLV","°F","°F","n/a","n/a",
                "#","kW","gpm","n/a","#","kW","gpm","n/a","n/a","n/a"
            ]

            df = pd.DataFrame({
                "Model Input Parameter": model_inputs,
                "Units": units
            })

            # -----------------------------
            # CREATE REQUIRED BASELINE COLUMNS
            # -----------------------------
            row_count = len(pva_df)
            extra_cols = row_count // 2   # number of baselines required

            for i in range(1, extra_cols + 1):
                df[f"Baseline - {i}"] = ""

            df["Proposed"] = ""

            # -----------------------------
            # EXISTING CHILLER CALCULATIONS
            # -----------------------------
            # st.write(pva_primary)
            # st.write(pva_primary_p)

            count_screw = pva_primary['Equipment & Attached To'].str.contains(
                'SCREW', case=True, na=False).sum()
            count_cent = pva_primary['Equipment & Attached To'].str.contains(
                'CENTRIFUGAL', case=True, na=False).sum()
            count_cent = count_cent + pva_primary['Equipment & Attached To'].str.contains(
                'CENT', case=True, na=False).sum()
            count_screw_p = pva_primary_p['Equipment & Attached To'].str.contains(
                'SCREW', case=True, na=False).sum()
            count_cent_p = pva_primary_p['Equipment & Attached To'].str.contains(
                'CENTRIFUGAL', case=True, na=False).sum()
            count_cent_p = count_cent_p + pva_primary_p['Equipment & Attached To'].str.contains(
                'CENT', case=True, na=False).sum()

            chillerCapacity = pva_primary['Rated Capacity(MBTU/HR)'].sum()
            chillerCapacity_p = pva_primary_p['Rated Capacity(MBTU/HR)'].sum()

            pva_primary["Cooling_kW"] = pva_primary["Rated Capacity(MBTU/HR)"] * 293.071
            pva_primary["Input_kW"] = pva_primary["Rated EIR(FRAC)"] * pva_primary["Cooling_kW"]
            pva_primary_p["Cooling_kW"] = pva_primary_p["Rated Capacity(MBTU/HR)"] * 293.071
            pva_primary_p["Input_kW"] = pva_primary_p["Rated EIR(FRAC)"] * pva_primary_p["Cooling_kW"]

            total_cooling = pva_primary["Cooling_kW"].sum()
            total_input = pva_primary["Input_kW"].sum()
            total_cooling_p = pva_primary_p["Cooling_kW"].sum()
            total_input_p = pva_primary_p["Input_kW"].sum()

            chiller_full_load_cop = round(total_cooling / total_input, 2)
            chiller_full_load_cop_p = round(total_cooling_p / total_input_p, 2)

            # -----------------------------
            # FILL ALL BASELINES (Baseline - i)
            # -----------------------------
            for i in range(1, extra_cols + 1):
                baseline_col = f"Baseline - {i}"
                proposed_col = f"Proposed"
                if count_screw > 0:
                    df.at[0, baseline_col] = f"{count_screw} water-cooled screw chillers"
                    df.at[0, proposed_col] = f"{count_screw_p} water-cooled screw chillers"
                elif count_cent > 0:
                    df.at[0, baseline_col] = f"{count_cent} water-cooled centrifugal chillers"
                    df.at[0, proposed_col] = f"{count_cent_p} water-cooled centrifugal chillers"
                else:
                    df.at[0, baseline_col] = "n/a"
                    df.at[0, proposed_col] = "n/a"
                df.at[1, baseline_col] = ""
                df.at[1, proposed_col] = ""
                df.at[2, baseline_col] = f"{round((chillerCapacity*1_000_000) / 12000,1)}"
                df.at[2, proposed_col] = f"{round((chillerCapacity_p*1_000_000) / 12000,1)}"
                df.at[3, baseline_col] = f"{chiller_full_load_cop:.2f}"
                df.at[3, proposed_col] = f"{chiller_full_load_cop_p:.2f}"
                df.at[5, baseline_col] = "44"   # CW supply temp default
                df.at[5, proposed_col] = "44"   # CW supply temp default
                df.at[7, baseline_col] = "44°F (7°C) at outdoor temps 80°F (27°C) and above, 54°F (12°C) at outdoor temps 60°F (16°C) and below, and ramped linearly between 44°F (7°C) and 54°F (12°C) at outdoor temps between 80°F (27°C) and 60°F (16°C) per G3.1.3.9"
                df.at[7, proposed_col] = "CHW Temp Reset based on actual CHW loop conditions"

            # -------------------------------------------------------
            # ODD ROW CALCULATIONS (1st, 3rd, 5th… rows from pva_df)
            # -------------------------------------------------------
            odd_rows = pva_df.iloc[::2]   # rows 0,2,4,...

            col4_vals = pd.to_numeric(odd_rows.iloc[:, 2], errors='coerce')  # 4th column
            col5_vals = pd.to_numeric(odd_rows.iloc[:, 3], errors='coerce')  # 5th column

            mask = col4_vals.notna() & col5_vals.notna()
            col4_vals = col4_vals[mask]
            col5_vals = col5_vals[mask]
            
            # st.write(pva_pumps)
            count_primary = pva_pumps.eq("PRIMARY").any(axis=1).sum()
            count_primary_p = pva_pumps_p.eq("PRIMARY").any(axis=1).sum()
            # st.write(pva_pumps)
            # Condition for EVAPORATOR
            mask_evap = pva_pumps.apply(lambda row: row.astype(str).str.contains('EVAPORATOR', case=False, na=False).any(), axis=1)
            # Condition for CONDENSER
            mask_cond = pva_pumps.apply(lambda row: row.astype(str).str.contains('CONDENSER', case=False, na=False).any(), axis=1)
            df_primary = pva_pumps[mask_evap].copy()
            df_condenser = pva_pumps[mask_cond].copy()
            df_secondary = pva_pumps[~(mask_evap | mask_cond)].copy()
            # st.write(df_primary)
            # st.write(df_condenser)
            # st.write(df_secondary)

            # Condition for EVAPORATOR
            mask_evap_p = pva_pumps_p.apply(lambda row: row.astype(str).str.contains('EVAPORATOR', case=False, na=False).any(), axis=1)
            # Condition for CONDENSER
            mask_cond_p = pva_pumps_p.apply(lambda row: row.astype(str).str.contains('CONDENSER', case=False, na=False).any(), axis=1)
            df_primary_p = pva_pumps_p[mask_evap_p].copy()
            df_condenser_p = pva_pumps_p[mask_cond_p].copy()
            df_secondary_p = pva_pumps_p[~(mask_evap_p | mask_cond_p)].copy()
            # st.write(df_primary)
            # st.write(df_condenser)
            # st.write(df_secondary)
            # st.write(df_secondary_p)
            if len(col4_vals) > 0:
                col4_vals = col4_vals * (10**6)
                col5_vals = col5_vals * (60 * 8.34)
                ratio_vals = col4_vals / col5_vals
                ratio_vals_p = col4_vals / col5_vals
                final_ratio_value = ratio_vals_p.iloc[0]
                final_ratio_value_p = ratio_vals_p.iloc[0]

                # Store into every baseline column (Baseline - i)
                for i in range(1, extra_cols + 1):
                    df.at[6, f"Baseline - {i}"] = f"{final_ratio_value:.2f}"
                    df.at[6, f"Proposed"] = f"{final_ratio_value_p:.2f}"
                    if len(df_primary) > 0:
                        df.at[8, f"Baseline - {i}"] = "Primary/Secondary as per G3.1.3.10"
                    else:
                        df.at[8, f"Baseline - {i}"] = "Primary/Secondary as per G3.1.3.10"
                    if len(df_primary) > 0 and len(df_secondary_p) > 0:
                        df.at[8, f"Proposed"] = "Primary/Secondary as per G3.1.3.10"
                    else:
                        df.at[8, f"Proposed"] = "Primary pumps are modelled, there are no secondary pumps installed in the proposed building layout"
                    df.at[9, f"Baseline - {i}"] = len(df_primary)
                    df.at[9, f"Proposed"] = len(df_primary_p)
                    df.at[10, f"Baseline - {i}"] = df_primary['Power(kW)'].iloc[0]
                    df.at[10, f"Proposed"] = df_primary_p['Power(kW)'].iloc[0]
                    df.at[11, f"Baseline - {i}"] = df_primary['Flow(GPM)'].iloc[0]
                    df.at[11, f"Proposed"] = df_primary_p['Flow(GPM)'].iloc[0]
                    if len(df_primary) > 1 and df_primary['Capacity Control'].iloc[0] == 'ONE-SPEED':
                        df.at[12, f"Baseline - {i}"] = "Constant Speed - each primary pump interlocked with associated chiller"
                    else:
                        df.at[12, f"Baseline - {i}"] = "No primary pumps modeled"
                    if len(df_primary_p) > 1 and df_primary_p['Capacity Control'].iloc[0] == 'ONE-SPEED':
                        df.at[12, f"Proposed"] = "Constant Speed - each primary pump interlocked with associated chiller"
                    elif len(df_primary_p) > 1 and df_primary_p['Capacity Control'].iloc[0] == 'VAR-SPEED':
                        df.at[12, f"Proposed"] = "Constant Speed - each primary pump interlocked with associated chiller"
                    else:
                        df.at[12, f"Proposed"] = "No primary pumps modeled"
                    df.at[13, f"Baseline - {i}"] = len(df_secondary)
                    df.at[13, f"Proposed"] = len(df_secondary_p)
                    if len(df_secondary) > 0:
                        df.at[14, f"Baseline - {i}"] = df_secondary['Power(kW)'].iloc[0]
                        df.at[15, f"Baseline - {i}"] = df_secondary['Flow(GPM)'].iloc[0]
                        df.at[16, f"Baseline - {i}"] = df_secondary['Capacity Control'].iloc[0]
                    if len(df_secondary_p) > 0:
                        df.at[14, f"Proposed"] = df_secondary_p['Power(kW)'].iloc[0]
                        df.at[15, f"Proposed"] = df_secondary_p['Flow(GPM)'].iloc[0]
                        df.at[16, f"Baseline - {i}"] = df_secondary['Capacity Control'].iloc[0]
                    elif len(df_secondary) == 0:
                        df.at[14, f"Baseline - {i}"] = "NA"
                        df.at[15, f"Baseline - {i}"] = "NA"
                        df.at[16, f"Baseline - {i}"] = ""
                    elif len(df_secondary_p) == 0:
                        df.at[14, f"Proposed"] = "NA"
                        df.at[15, f"Proposed"] = "NA"
                        df.at[16, f"Proposed"] = ""
            else:
                for i in range(1, extra_cols + 1):
                    df.at[6, f"Baseline - {i}"] = "NA"
            
            # -----------------------------
            # SHOW FINAL TABLE
            # -----------------------------
            # st.write(count_primary)
            # st.write(df)
            rows_to_color = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
            styled_df = df.style.apply(
                lambda row: [
                    "background-color: #E3F2FD; color: black;"
                    if (row.name in rows_to_color and col in [baseline_col, proposed_col])
                    else ""
                    for col in row.index
                ],
                axis=1
            )

            st.dataframe(styled_df)
            # ----- Legend -----
            st.markdown(
                """
                <div style="margin-top:12px; padding:10px; border-left:4px solid #2196F3; background:#F5FBFF;">
                    <b>🔵 Note:</b>  
                    Cells highlighted in <span style="color:#1976D2; font-weight:bold;">light blue</span> 
                    should be <b>verified and copied by the user</b>.
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("""<br>""",unsafe_allow_html=True)
            st.markdown('<h7 style="color:red;">Cooling Tower and Condenser Water</h7>', unsafe_allow_html=True)
            if pva_primary.empty == True:
                st.info("No chilled water data found in Water-Side HVAC.")
            else:
                # -----------------------------
                # MODEL INPUTS + UNITS
                # -----------------------------
                model_inputs = [
                    "Number and cooling towers or fluid coolers",
                    "Cooling tower fan power",
                    "Cooling tower fan control",
                    "Condenser water (CW) leaving temp",
                    "CW ΔT",
                    "CW loop temp reset parameters",
                    "Number of CW pumps",
                    "CW pump power",
                    "CW pump flow",
                    "CW pump control",
                ]
                units = ["#","gpm/HP","n/a","°F","°F","n/a","#","kW","gpm","n/a"]

                df = pd.DataFrame({
                    "Model Input Parameter": model_inputs,
                    "Units": units
                })
                # -----------------------------
                # CREATE REQUIRED BASELINE COLUMNS
                # -----------------------------
                row_count = len(pva_df)
                extra_cols = row_count // 2   # number of baselines required

                for i in range(1, extra_cols + 1):
                    df[f"Baseline - {i}"] = ""

                df["Proposed"] = ""

                # -----------------------------
                # FILL ALL BASELINES (Baseline - i)
                # -----------------------------
                # Take first row values
                fan_kw = float(pva_tower.loc[0, "Fan Power per Cell(kW)"])
                flow_gpm = float(pva_tower.loc[0, "Flow (GAL/MIN)"])
                fan_kw_p = float(pva_tower_p.loc[0, "Fan Power per Cell(kW)"])
                flow_gpm_p = float(pva_tower_p.loc[0, "Flow (GAL/MIN)"])
                # Convert kW to HP
                hp = fan_kw / 0.746
                hp_p = fan_kw_p / 0.746

                # Calculate gpm per HP
                gpm_per_hp = flow_gpm / hp
                gpm_per_hp = round(gpm_per_hp, 2)
                gpm_per_hp_p = flow_gpm_p / hp_p
                gpm_per_hp_p = round(gpm_per_hp_p, 2)

                for i in range(1, extra_cols + 1):
                    baseline_col = f"Baseline - {i}"
                    proposed_col = f"Proposed"
                    df.at[0, baseline_col] = f"{len(pva_tower)}"
                    df.at[0, proposed_col] = f"{len(pva_tower)}"
                    df.at[1, baseline_col] = f"{gpm_per_hp:.2f}"
                    df.at[1, proposed_col] = f"{gpm_per_hp_p:.2f}"
                    df.at[2, baseline_col] = "Two-speed fan"
                    df.at[2, proposed_col] = ""
                    df.at[6, baseline_col] = f"{len(df_condenser)}"
                    df.at[6, proposed_col] = f"{len(df_condenser_p)}"
                    df.at[7, baseline_col] = df_condenser['Power(kW)'].iloc[0]
                    df.at[7, proposed_col] = df_condenser_p['Power(kW)'].iloc[0]
                    df.at[8, baseline_col] = df_condenser['Flow(GPM)'].iloc[0]
                    df.at[8, proposed_col] = df_condenser_p['Flow(GPM)'].iloc[0]
                    df.at[9, baseline_col] = df_condenser['Capacity Control'].iloc[0]
                    df.at[9, proposed_col] = df_condenser_p['Capacity Control'].iloc[0]
                
                rows_to_color = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                proposed_row = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                highlight_style = "background-color: #E3F2FD; color: black;"

                # Select all baseline columns automatically
                baseline_cols = [col for col in df.columns if "Baseline" in col]
                target_cols = baseline_cols + ["Proposed"]

                df = df.style.apply(
                    lambda row: [
                        highlight_style
                        if (
                            (row.name in rows_to_color and col in target_cols)
                            or (row.name in proposed_row and col == "Proposed")
                        )
                        else ""
                        for col in row.index
                    ],
                    axis=1
                )

                st.write(df)
                st.markdown(
                    """
                    <div style="margin-top:12px; padding:10px; border-left:4px solid #2196F3; background:#F5FBFF;">
                        <b>🔵 Note:</b>  
                        Cells highlighted in <span style="color:#1976D2; font-weight:bold;">light blue</span> 
                        should be <b>verified and copied by the user</b>.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    except Exception as e:
        st.warning(f"Please Select Spaces to get Started!")