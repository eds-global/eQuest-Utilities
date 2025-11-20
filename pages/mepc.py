import streamlit as st
from MEP_Calculator import loads, ps_e, lv_d
import pandas as pd

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
    summary_df, sv_a_df, sv_a_zone_df, sv_a_df_p = loads.getProcessLoads(db, sim_file_proposed_for_use1, sim_file_for_use1)
    
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
    st.markdown("""<br><br><br>""", unsafe_allow_html=True)
    st.markdown(
        '<h5 style="color:red;">Air-Side HVAC</h5>',
        unsafe_allow_html=True
    )

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

    # st.write(sv_a_df)
    # st.write(sv_a_df_p)
    # st.write(sv_a_zone_df)

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
    # # Loop through Baseline columns
    # for i in range(1, num_cols + 1):
    #     sys_val = df.at[2, f"Baseline - {i}"]   # <-- row 2, change index if needed

    #     if isinstance(sys_val, str) and sys_val.startswith("Sys"):
    #         system_no = int(sys_val.replace("Sys", ""))   # extract number
    #         fanc = "Variable Speed" if 5 <= system_no <= 8 else "Constant Speed"
    #     else:
    #         fanc = ""

    #     df.at[fan_control_row, f"Baseline - {i}"] = fanc

    # # Loop through Proposed columns
    # for i in range(1, num_cols_p + 1):
    #     sys_val = df.at[2, f"Proposed - {i}"]

    #     if isinstance(sys_val, str) and sys_val.startswith("Sys"):
    #         system_no = int(sys_val.replace("Sys", "")) 
    #         fanc = "Variable Speed" if 5 <= system_no <= 8 else "Constant Speed"
    #     else:
    #         fanc = ""

    #     df.at[fan_control_row, f"Proposed - {i}"] = fanc

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

    # Data editor
    edited_df = st.data_editor(
        df_filtered,
        hide_index=True,
        use_container_width=True,
        key="editor_no_sum"  # Unique key prevents duplicate ID issue
    )

    # -------------------------
    # Section 8 - Water-Side HVAC
    # -------------------------




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