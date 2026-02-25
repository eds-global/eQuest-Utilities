import streamlit as st
from MEP_Calculator import loads, ps_e, lv_d
import pandas as pd
import re

st.set_page_config(
    page_title="eQUEST Utilities",
    page_icon="💡",
    layout='wide',
)

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
        <h4>♻️ LEED MEPC Tool</h4>
        <div class="nav-links">
            <a href="/" target="_self">Home</a>
            <a href="#start">Getting Started</a>
            <a href="#performance">Performance Outputs</a>
            <a href="#shade">Shading & Fenestration</a>
            <a href="#schedules">Schedules</a>
            <a href="#lighting">Lighting</a>
            <a href="#loads">Process Loads</a>
            <a href="#hvac">Air-Side HVAC</a>
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
# -------------------------
# Section 1 - Upload
# -------------------------
st.markdown('<div id="start" class="section"></div>', unsafe_allow_html=True)
st.markdown(
        '<h5 style="color:red;">✪ Upload SIM Files</h5>',
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
    databse = r'MEP_Calculator/database/eQUEST_database.csv'
    csv_file = r'MEP_Calculator/tables/MEP Calculator.csv'
    df = pd.read_csv(csv_file)
    db = pd.read_csv(databse)
    summary_df, sv_a_df, sv_a_zone_df, sv_a_df_proposed = loads.getProcessLoads(db, sim_file_proposed_for_use1, sim_file_for_use1)
    
    # -------------------------
    # Section 2 - Unmatched
    # -------------------------
    st.markdown('<div id="performance" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">✪ Performance Outputs</h5>',
        unsafe_allow_html=True
    )
    if uploaded_90_degree is not None and uploaded_180_degree is not None:
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
            ps_e.get_END_USE_Proposed(df, uploaded_0_degree, uploaded_90_degree, uploaded_180_degree, uploaded_270_degree, uploaded_proposed_file)
        else:
            st.info("Please upload all 4 rotation SIM files for Performance Outputs.")

    # -------------------------
    # Section 3 - Review & Edit
    # -------------------------
    st.markdown('<div id="shade" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">✪ Shading & Fenestration</h5>',
        unsafe_allow_html=True
    )
    # if uploaded_0_degree is not None and uploaded_proposed_file is not None:
    #     if st.button("Generate Reports"):
    #         lv_d.generateFenestration(uploaded_0_degree, uploaded_proposed_file)

    # -------------------------
    # Section 4 - Calculator
    # -------------------------
    st.markdown('<div id="schedules" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">✪ Schedules</h5>',
        unsafe_allow_html=True
    )

    # -------------------------
    # Section 5 - Calculator
    # -------------------------
    st.markdown('<div id="lighting" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">✪ Lighting Loads Summary</h5>',
        unsafe_allow_html=True
    )
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
        st.dataframe(last4_grouped)
    elif "Design LPD(W/ft²)" not in summary_df.columns:
        st.dataframe(summary_df)

    # -------------------------
    # Section 6 - Calculator
    # -------------------------
    st.markdown('<div id="loads" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">✪ Process Loads Summary</h5>',
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
        st.dataframe(summary_df)
    elif "EQUIP(WATT / SOFT)" not in summary_df.columns:
        st.dataframe(summary_df)

    # -------------------------
    # Section 7 - Air-Side HVAC
    # -------------------------
    st.markdown('<div id="hvac" class="section"></div>', unsafe_allow_html=True)
    st.markdown("""<br><br><br>""",unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">✪ Air-Side HVAC System Schedule</h5>',
        unsafe_allow_html=True
    )

    hvac_path = r'MEP_Calculator/database/HVAC_DB.xlsx'  # adjust if needed
    df = pd.read_excel(hvac_path, sheet_name="UnitsMap")
    system_map = pd.read_excel(hvac_path, sheet_name="SystemRanges")
    # Dropdown options for Units column
    unit_options = df['Units'].dropna().tolist()
    # col1, col2 = st.columns([1, 3.1])
    # with col1:
    #     # Make two sub-columns: label and dropdown
    #     label_col, dropdown_col = st.columns([1, 1.5])  # adjust ratio for label vs dropdown size

    #     # with label_col:
    #     #     st.markdown("**Select System**")

    #     # with dropdown_col:
    #     #     systems = [f"System {i}" for i in range(1, 11)]
    #     #     system = st.selectbox("", systems, key="unit_select", label_visibility="collapsed")
    #     #     system = int(system.split()[-1])

    system = 2
    total_cooling = float(pd.to_numeric(sv_a_df['COOLING_CAPACITY(KBTU/HR)'], errors='coerce').sum())
    total_heating = float(pd.to_numeric(sv_a_df['HEATING_CAPACITY(KBTU/HR)'], errors='coerce').sum())
    total_cooling_p = float(pd.to_numeric(sv_a_df_proposed['COOLING_CAPACITY(KBTU/HR)'], errors='coerce').sum())
    total_heating_p = float(pd.to_numeric(sv_a_df_proposed['HEATING_CAPACITY(KBTU/HR)'], errors='coerce').sum())
    fan_control = "Variable Speed" if 5 <= system <= 8 else "Constant Speed"
    st.write(sv_a_df)
    st.write(sv_a_df_proposed)
    # Define initial data (all rows from your sheet)
    data = [
        {"Model Input Parameter": "Total cooling capacity", "Units": "tons", "Baseline - Total": 0, "Proposed - Total": 0},
        {"Model Input Parameter": "* Table 6.8.1 Unitary Cooling (Systems 1 through 6)", "Units": "tons", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Unitary cooling efficiency", "Units": "", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Unitary cooling part-load efficiency (if applicable)", "Units": "", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Total heating capacity", "Units": "kBtu/h", "Baseline - Total": 0, "Proposed - Total": 0},
        {"Model Input Parameter": "* Table 6.8.1 Unitary Heating (Systems 2, 3, 4, and 9)", "Units": "kBtu/h", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Unitary heating efficiency", "Units": "", "Baseline - Total": "", "Proposed - Total": ""},
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
        {"Model Input Parameter": "* Pressure Drop Adjustments (Systems 3 through 8) - Fully ducted return and/or exhaust air systems", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Return and/or exhaust airflow control devices", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Exhaust filters, scrubbers, or other exhaust treatment", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Particulate filtration credit: MERV 9 through 12", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Particulate filtration credit: MERV 13 through 15", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Particulate filtration credit: MERV 16 and greater and electronically enhanced filters", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Carbon and other gas-phase air cleaners", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Biosafety cabinet", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Energy recovery device, other than coil runaround loop", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Coil runaround loop", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Evaporative humidifier/cooler in series with another cooling coil", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Sound attenuation section", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Exhaust system serving fume hoods", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Laboratory and vivarium exhaust systems in high-rise buildings", "Units": "CFMD: cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   Adjustment", "Units": "in. w.c.", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Total Table 6.5.3.1.1B pressure drop adjustment (A)", "Units": "bhp", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "Fan power adjustments (Systems 9 through 10) - Non-mechanical cooling fan - additional fan power allowance", "Units": "cfm", "Baseline - Total": "", "Proposed - Total": ""},
        {"Model Input Parameter": "   fan power per cfm", "Units": "kW", "Baseline - Total": "", "Proposed - Total": ""},
    ]

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Dynamically add baseline/proposed columns
    num_cols = len(sv_a_df)
    num_cols_p = len(sv_a_df_proposed)
    for i in range(1, num_cols + 1):
        df[f"Baseline - {i}"] = 0
    for i in range(1, num_cols_p + 1):
        df[f"Proposed - {i}"] = 0

    # --- Baseline Fill Row 1 (Cooling capacity) ---
    cooling_values = sv_a_df["COOLING_CAPACITY(KBTU/HR)"].tolist()
    for i, val in enumerate(cooling_values, start=1):
        df.at[0, f"Baseline - {i}"] = val

        # --- Row 2: Map capacity using SystemRanges ---
        sys_col = f"System{system}"
        mapped_value = ""
        for _, row in system_map.iterrows():
            condition = str(row[sys_col]).strip()
            if condition != "N/A" and condition != "All capacities":
                # Convert ">=65000 and <135000" → check with eval
                expr = condition.replace("and", "&")
                try:
                    if eval(str(val) + expr):  # e.g., 70000 >=65000 & 70000 <135000
                        mapped_value = condition
                        break
                except:
                    pass
            elif condition == "All capacities":
                mapped_value = condition
                break
        df.at[1, f"Baseline - {i}"] = mapped_value
    
    # --- Proposed Fill Row 1 (Cooling capacity) ---
    cooling_values_p = sv_a_df_proposed["COOLING_CAPACITY(KBTU/HR)"].tolist()
    for i, val in enumerate(cooling_values_p, start=1):
        df.at[0, f"Proposed - {i}"] = val

        # --- Row 2: Map capacity using SystemRanges ---
        sys_col = f"System{system}"
        mapped_value = ""
        for _, row in system_map.iterrows():
            condition = str(row[sys_col]).strip()
            if condition != "N/A" and condition != "All capacities":
                # Convert ">=65000 and <135000" → check with eval
                expr = condition.replace("and", "&")
                try:
                    if eval(str(val) + expr):  # e.g., 70000 >=65000 & 70000 <135000
                        mapped_value = condition
                        break
                except:
                    pass
            elif condition == "All capacities":
                mapped_value = condition
                break
        df.at[1, f"Proposed - {i}"] = mapped_value

    # --- Fill Row 5 (Heating capacity) ---
    heating_values = sv_a_df["HEATING_CAPACITY(KBTU/HR)"].tolist()
    for i, val in enumerate(heating_values, start=1):
        df.at[4, f"Baseline - {i}"] = val

        # --- Row 2: Map capacity using SystemRanges ---
        sys_col1 = f"System{system}"
        mapped_value1 = ""
        for _, row in system_map.iterrows():
            condition = str(row[sys_col1]).strip()
            if condition != "N/A" and condition != "All capacities":
                # Convert ">=65000 and <135000" → check with eval
                expr = condition.replace("and", "&")
                try:
                    if eval(str(val) + expr):  # e.g., 70000 >=65000 & 70000 <135000
                        mapped_value1 = condition
                        break
                except:
                    pass
            elif condition == "All capacities":
                mapped_value1 = condition
                break
        df.at[5, f"Baseline - {i}"] = mapped_value1
    
    # --- Fill Row 5 (Heating capacity) ---
    heating_values_p = sv_a_df_proposed["HEATING_CAPACITY(KBTU/HR)"].tolist()
    for i, val in enumerate(heating_values_p, start=1):
        df.at[4, f"Proposed - {i}"] = val

        # --- Row 2: Map capacity using SystemRanges ---
        sys_col1 = f"System{system}"
        mapped_value1 = ""
        for _, row in system_map.iterrows():
            condition = str(row[sys_col1]).strip()
            if condition != "N/A" and condition != "All capacities":
                # Convert ">=65000 and <135000" → check with eval
                expr = condition.replace("and", "&")
                try:
                    if eval(str(val) + expr):  # e.g., 70000 >=65000 & 70000 <135000
                        mapped_value1 = condition
                        break
                except:
                    pass
            elif condition == "All capacities":
                mapped_value1 = condition
                break
        df.at[5, f"Proposed - {i}"] = mapped_value1

    # --- Fill Row 7 (Fan control) ---
    fanc = "Variable Speed" if system > 4 and system < 9 else "Constant Speed"
    for i in range(1, num_cols + 1):
        df.at[7, f"Baseline - {i}"] = fanc
    for i in range(1, num_cols_p + 1):
        df.at[7, f"Proposed - {i}"] = fanc

    # --- Airflows (safe calculation) ---
    if "SUPPLY-FLOW(CFM)" in sv_a_zone_df.columns:
        supply_airflow = pd.to_numeric(sv_a_zone_df["SUPPLY-FLOW(CFM)"], errors="coerce").sum()
    else:
        supply_airflow = 0

    if "OUTISIDE-AIR-FLOW(CFM)" in sv_a_zone_df.columns:
        sv_a_zone_df["OUTISIDE-AIR-FLOW(CFM)"] = pd.to_numeric(sv_a_zone_df["OUTISIDE-AIR-FLOW(CFM)"], errors="coerce")
        outside_airflow = sv_a_zone_df["OUTISIDE-AIR-FLOW(CFM)"].sum()
    else:
        outside_airflow = 0
    
    if "FAN(KW)" in sv_a_zone_df.columns:
        sv_a_zone_df["FAN(KW)"] = pd.to_numeric(sv_a_zone_df["FAN(KW)"], errors="coerce")
        supply_fan = sv_a_zone_df["FAN(KW)"].sum()
    else:
        supply_fan = 0

    # --- Fill Row 8, 9 (Airflows) ---
    for i in range(1, num_cols + 1):
        df.at[8, f"Baseline - {i}"] = supply_airflow
        df.at[9, f"Baseline - {i}"] = outside_airflow
        df.at[15, f"Baseline - {i}"] = supply_fan
    
    for i in range(1, num_cols_p + 1):
        df.at[8, f"Proposed - {i}"] = supply_airflow
        df.at[9, f"Proposed - {i}"] = outside_airflow
        df.at[15, f"Proposed - {i}"] = supply_fan

    # Column config
    column_config = {
        "Units": st.column_config.SelectboxColumn("Units", options=["kBtuh", "Btuh", "tons", "EER", "kW", "SEER", "IEER", "IPLV", "kBtu/h", "HSPF", "COP", "AFUE", "%Et", "%Ec", "°F", "°C"])
    }
    for i in range(1, num_cols + 1):
        column_config[f"Baseline - {i}"] = st.column_config.TextColumn(f"Baseline - {i}")
        column_config[f"Proposed - {i}"] = st.column_config.NumberColumn(f"Proposed - {i}", step=1, default=0)
    
    # --- Update Total columns ---
    baseline_cols = [col for col in df.columns if col.startswith("Baseline - ") and col != "Baseline - Total"]
    proposed_cols = [col for col in df.columns if col.startswith("Proposed - ") and col != "Proposed - Total"]

    for idx in range(len(df)):
        # Only sum numeric columns, ignore text
        baseline_vals = pd.to_numeric(df.loc[idx, baseline_cols], errors="coerce")
        proposed_vals = pd.to_numeric(df.loc[idx, proposed_cols], errors="coerce")

        if baseline_vals.notna().any():
            df.at[idx, "Baseline - Total"] = baseline_vals.sum()
        if proposed_vals.notna().any():
            df.at[idx, "Proposed - Total"] = proposed_vals.sum()

    # Editable table in Streamlit
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True
    ) 
    

    # st.write(sv_a_df)
    # st.write(sv_a_zone_df)

    # rows = df.iloc[:, 0].dropna().astype(str).tolist()
    # options = df.iloc[:, 1].dropna().unique().tolist()
    
    # # Initialize session state
    # if "results" not in st.session_state:
    #     st.session_state["results"] = []
    # if "disabled_items" not in st.session_state:
    #     st.session_state["disabled_items"] = set()

    # # Create the form
    # with st.form("hvac_form"):
    #     col1, col2 = st.columns([4, 1])
    #     selected_items = []

    #     # --- Left column: Checkboxes (3 per row) ---
    #     with col1:
    #         st.markdown(
    #             '<h6 style="color:green;">📝 Model Input Paramter</h6>',
    #             unsafe_allow_html=True
    #         )
    #         for i in range(0, len(rows), 4):
    #             c1, c2, c3, c4 = st.columns(4)
    #             for j, col in enumerate([c1, c2, c3, c4]):
    #                 if i + j < len(rows):
    #                     label = rows[i + j]
    #                     key_name = f"check_{i}_{j}_{label}"

    #                     is_disabled = label in st.session_state["disabled_items"]

    #                     if col.checkbox(label, key=key_name, disabled=is_disabled):
    #                         selected_items.append(label)

    #     # --- Right column: Dropdown + Save button ---
    #     with col2:
    #         st.markdown(
    #             '<h6 style="color:green;">🔌 Units</h6>',
    #             unsafe_allow_html=True
    #         )
    #         dropdown_value = st.selectbox("Choose option", sorted(options), key="dropdown")
    #         submitted = st.form_submit_button("Save")

    #         if submitted:
    #             if selected_items:
    #                 for item in selected_items:
    #                     # ✅ Only add if not already saved
    #                     if not any(r["Selected Item"] == item for r in st.session_state["results"]):
    #                         st.session_state["results"].append(
    #                             {"Selected Item": item, "Option Chosen": dropdown_value}
    #                         )
    #                         st.session_state["disabled_items"].add(item)
    #                 st.success("✅ Saved Successfully!")
    #             else:
    #                 st.warning("⚠️ Please select at least one item.")

    # # --- After Save: show editable table with delete icons ---
    # st.markdown("<hr style='border:1px solid red'>", unsafe_allow_html=True)  # red line
    # # --- Header Section ---
    # if st.session_state["results"]:
    #     st.write("##### Review / Edit")
    #     # Convert session_state results to DataFrame
    #     result_df = pd.DataFrame(st.session_state["results"])

    #     # Display each row with delete button
    #     for idx, row in result_df.iterrows():
    #         # Create columns dynamically: one column per value + 1 for delete button
    #         col_widths = [3]*len(row) + [1]  # last column is for delete button
    #         cols = st.columns(col_widths)

    #         # Write values in the first N columns
    #         for i, value in enumerate(row):
    #             cols[i].write(value)

    #         # Delete button in the last column
    #         if cols[-1].button("🗑️", key=f"delete_{idx}"):
    #             removed_item = st.session_state["results"].pop(idx)["Selected Item"]
    #             st.session_state["disabled_items"].discard(removed_item)
    #             st.rerun()

    #     # Optionally rename columns for display
    #     result_df.rename(columns={'Selected Item': 'Model Input Parameter', 
    #                             'Option Chosen': 'Units'}, inplace=True)
    #     st.write(result_df)

    #     st.write(total_cooling)
    #     st.write(total_heating)
    #     st.write(fan_control)
    #     st.write(sv_a_zone_df['SUPPLY-FLOW(CFM)'].sum())
    #     st.write(sv_a_zone_df)
    #     st.write(sv_a_df)
    #     total_outside_air = pd.to_numeric(sv_a_zone_df['OUTISIDE-AIR-FLOW(CFM)'], errors='coerce').sum()
    #     st.write(f"{total_outside_air:.2f}")

