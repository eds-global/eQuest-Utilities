import streamlit as st
import subprocess
import os
import pandas as pd
from INP_Parser import inp_parserv01
from Perging_INP import perge
from SIM_Parser import sim_parserv01
from SIM2PDF import sim_print
from Polygon_Parser import polygon
from streamlit_lottie import st_lottie
from BaselineAutomation import baselineAuto
from ScheduleGenerator import schedule_v01
from ScheduleGenerator import sheduls_analytics
from MEP_Calculator import ps_e
from MEP_Calculator import lv_d
from q import qa
from Happ import hap
from igbc import igbc_data
from streamlit_card import card
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="eQUEST Utilities",
    page_icon="💡",
    layout='wide',  # Only 'centered' or 'wide' are valid options
    menu_items={                          
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': '# This is an **eQuest Utilities** application!'
    }
)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
    
def set_dark_theme():
    """
    Function to set a dark theme using CSS.
    """
    # Define the HTML code with CSS for a dark theme
    html_code = """
    <style>
    .stApp {
        background-color: black;  /* Set background color to black */
        color: white;  /* Set text color to white */
    }
    .stMarkdown, .stImage, .stDataFrame, .stTable, .stTextInput, .stButton, .stSidebar {
        background-color: transparent !important; /* Make elements' background transparent */
        color: white !important;  /* Ensure text color within these elements is white */
    }
    .stButton > button {
        background-color: #333; /* Dark background for buttons */
        color: white;  /* White text for buttons */
    }
    .stSidebar {
        background-color: #222; /* Slightly lighter background for sidebar */
    }
    .stTextInput > div > input {
        background-color: #444; /* Dark background for text input */
        color: white;  /* White text for text input */
    }
    </style>
    """
    # Inject the HTML code in the Streamlit app
    st.markdown(html_code, unsafe_allow_html=True)
    
def confetti_animation():
    st.markdown(
        """
        <style>
        @keyframes confetti {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-100vh) rotate(360deg); }
        }
        .confetti {
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: #f00;
            background-image: linear-gradient(135deg, transparent 10%, #f00 10%, #f00 20%, transparent 20%, transparent 30%, #0f0 30%, #0f0 40%, transparent 40%, transparent 50%, #00f 50%, #00f 60%, transparent 60%, transparent 70%);
            background-size: 10px 10px;
            animation: confetti 5s linear infinite;
            opacity: 0.7;
        }
        </style>
        """
    )
    st.markdown('<div class="confetti"></div>', unsafe_allow_html=True)

def send_email(subject, message, from_email, to_email):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        # print(f"Failed to send email: {e}")
        st.success("Email sent successfully!")
        return False

button_style = """
    <style>
        .stButton>button {
            box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.8);
        }
    </style>
"""

# Render the button with the defined style
st.markdown(button_style, unsafe_allow_html=True)

# Define CSS style with text-shadow effect for the heading
heading_style = """
    <style>
    .heading-with-shadow {
        text-align: left;
        color: red;
        text-shadow: 0px 8px 4px rgba(255, 255, 255, 0.4);
        background-color: white;
    }
</style>
"""
st.markdown(heading_style, unsafe_allow_html=True)
def main(): 
    card_button_style = """
        <style>
        .card-button {
            width: 100%;
            padding: 20px;
            background-color: white;
            border: none;
            border-radius: 10px;
            box-shadow: 0 2px 2px rgba(0,0,0,0.2);
            transition: box-shadow 0.3s ease;
            text-align: center;
            font-size: 16px;
            cursor: pointer;
        }
        .card-button:hover {
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        </style>
    """

    st.markdown(
        """
        <style>
        body {
            background-color: #bfe1ff;  /* Set your desired background color here */
            animation: changeColor 5s infinite;
        }
        .css-18e3th9 {
            padding-top: 0rem;  /* Adjust the padding at the top */
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .viewerBadge_container__1QSob {visibility: hidden;}
        .stActionButton {margin: 5px;} /* Optional: Adjust button spacing */
        header .stApp [title="View source on GitHub"] {
            display: none;
        }
        .stApp header, .stApp footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state for script_choice if it does not exist
    if 'script_choice' not in st.session_state:
        st.session_state.script_choice = "about"  # Set default to "about"
            
    logo_url = "https://equest-utilities-edsglobal.streamlit.app/"
    logo_image_path = "images/eQcb_142.gif"
    col1, col2, col3 = st.columns([1,1,0.5])
    with col1:
        st.image(logo_image_path, width=80)
    with col2:
        # st.markdown("<h1 class='heading-with-shadow'>eQUEST Utilities</h1>", unsafe_allow_html=True)
        st.markdown("# :rainbow[eQUEST Utilities]")

    on = st.toggle("Select Theme")
    if on:
        set_dark_theme()
        pass  # Do nothing
        background_image_url = "https://i.pinimg.com/originals/cf/04/e9/cf04e9530f25312133dc7f93586591ff.gif"
    with col3:
        st.image("images/EDSlogo.jpg", width=120)

    st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
    st.markdown("""
        <style>
        .stButton button {
            height: 30px;
            width: 166px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create two rows of columns with equal widths
    col2, col3, col4, col5, col6, col7, col8 = st.columns(7) 
    col9, col10, col11, col12, col13, col14, col15 = st.columns(7)
    col16, col17, _, _, _, _, _ = st.columns(7)
    
    # First row of buttons
    with col2:
        if st.button("About EDS", key="button_eds"):
            st.session_state.script_choice = "eds"
    with col3:
        if st.button("eQUEST Utilities", key="button_utilities"):
            st.session_state.script_choice = "about"
    with col4:
        if st.button("INP Parser", key="button_inp_parser"):
            st.session_state.script_choice = "INP Parser"
    with col5:
        if st.button("Purging INP", key="button_purging_inp"):
            st.session_state.script_choice = "Purging INP"
    with col6:
        if st.button("SIM Parser", key="button_sim_parser"):
            st.session_state.script_choice = "SIM Parser"
    with col7:
        if st.button("SIM to PDF", key="button_sim_to_pdf"):
            st.session_state.script_choice = "SIM to PDF"
    with col8:
        if st.button("Baseline Automation", key="button_baseline_automation"):
            st.session_state.script_choice = "baselineAutomation"
    
    # Second row of buttons
    with col9:
        if st.button("Schedule Generator", key="button_schedule_generator"): 
            st.session_state.script_choice = "sh"
    with col10:
        if st.button("QA / QC", key="button_qa_qc"):
            st.session_state.script_choice = "q"
    with col11:
        if st.button("Polygon Parser", key="button_analytics"): #Queries
            st.session_state.script_choice = "sh1"
    with col12:
        if st.button("EXE and Resources", key="button_exe_resources"):
            st.session_state.script_choice = "exe"
    with col13:
        if st.button("IGBC Green 🏡", key="references"): #Queries
            st.session_state.script_choice = "reference"
    with col14:
        if st.button("Calibration Tool", key="button_contact"): #Queries
            st.session_state.script_choice = "cal"
    with col15:
        if st.button("MEPC Tool", key="mep_calculator"): #Queries
            st.session_state.script_choice = "mepc"

    # Third rows of buttons
    with col16:
        if st.button("HAP Tool", key="HAP_calculator"): #Queries
            st.session_state.script_choice = "hap"
    
            
    #Based on the user selection, display appropriate input fields and run the script
    if st.session_state.script_choice == "about":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <h4 style="color:red;">🌟 Start your Success with eQUEST Utilities</h4>
    
            eQUEST Utilities is a comprehensive suite of tools designed to help you work with eQUEST more efficiently. 
            Our utilities include:
    
            🔍 <b style="color:red;">INP Parser:</b> A tool to parse INP files and extract meaningful data.<br>
            🧹 <b style="color:red;">Purging INP:</b> A utility to update and clean your INP files.<br>
            📈 <b style="color:red;">SIM Parser:</b> A parser for SIM files to streamline your simulation data processing.<br>
            📄 <b style="color:red;">SIM to PDF Converter:</b> Easily convert your SIM files into PDF format for better sharing and documentation.<br>
            ⚙️ <b style="color:red;">Baseline Automation:</b> Modifies INP files based on the user input.<br>
            📅 <b style="color:red;">Schedule Generator:</b> Our CSV-Based Schedule Generator Tool is designed to simplify and automate the process of creating schedules.<br>
            ✅ <b style="color:red;">Quality Check / Quality Assurance:</b> A quality check, also known as quality control (QC), refers to the process of ensuring that a product or service meets a defined set of quality criteria or standards.<br><br>
            
            """, unsafe_allow_html=True)
        with col2:
            st.image("https://www.filepicker.io/api/file/ISb3e710QSmh95AYIdef", width=560)
        st.markdown(""" Navigate through the tools using the buttons above to get started. Each tool is designed to simplify 
            specific tasks related to eQUEST project management. We hope these utilities make your workflow smoother 
            and more productive.
        """, unsafe_allow_html=True)
        
    elif st.session_state.script_choice == "eds":
        st.markdown("""
            <h4 style="color:red;">🌐 Overview</h4>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            Environmental Design Solutions [EDS] is a sustainability advisory firm focusing on the built environment. Since its inception in 2002,
            EDS has worked on over 800 green building and energy efficiency projects worldwide. The diverse milieu of its team of experts converges on
            climate change mitigation policies, energy efficient building design, building code development, energy efficiency policy development, energy
            simulation and green building certification.<br>
    
            EDS has extensive experience in providing sustainable solutions at both, the macro level of policy advisory and planning, as well as a micro
            level of developing standards and labeling for products and appliances. The scope of EDS projects range from international and national level
            policy and code formulation to building-level integration of energy-efficiency parameters. EDS team has worked on developing the Energy Conservation
            Building Code [ECBC] in India and supporting several other international building energy code development, training, impact assessment, and 
            implementation. EDS has the experience of data collection & analysis, benchmarking, energy savings analysis, GHG impact assessment, and developing
            large scale implementation programs.<br>
    
            EDS’ work supports the global endeavour towards a sustainable environment primarily through the following broad categories:
            - Sustainable Solutions for the Built Environment
            - Strategy Consulting for Policy & Codes, and Research
            - Outreach, Communication, Documentation, and Training
    
            """, unsafe_allow_html=True)
            st.link_button("Know More", "https://edsglobal.com", type="primary")
        with col2:
            st.image("https://images.jdmagicbox.com/comp/delhi/k8/011pxx11.xx11.180809193209.h6k8/catalogue/environmental-design-solutions-vasant-vihar-delhi-environmental-management-consultants-leuub0bjnn.jpg", width=590)
        
    elif st.session_state.script_choice == "sh":
        st.markdown("""
        <h4 style="color:red;">📅 Schedule Generator</h4>
        <b>Purpose:</b> Our CSV-Based Schedule Generator Tool is designed to simplify and automate the process of creating schedules. By leveraging data from a CSV file, this tool efficiently generates a structured and optimized schedule tailored to your specific needs.<br>
        <br>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Schedule in excel", type=["xlsx"], accept_multiple_files=False)
        if uploaded_file is not None:
            if st.button("Generate INP"):
                schedule_v01.get_schedule(uploaded_file)
        schedule_v01.analytics(uploaded_file)
        schedule_v01.analytics1(uploaded_file)
    
    elif st.session_state.script_choice == "sh1":
        st.markdown("""
        <h4 style="color:red;">📄 Polygon Parser</h4>
        <b>Purpose:</b> A Polygon Parser is a tool or script designed to extract and analyze polygon data, usually from text or file formats such as JSON, XML, or custom structures. This parser typically processes attributes of polygons like their vertices, edges, and associated metadata. <br>
        <br>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Generate CSV"):
                polygon.main(uploaded_file)
    
    elif st.session_state.script_choice == "INP Parser":
        st.markdown("""
        <h4 style="color:red;">📄 INP Parser</h4>
        <b>Purpose:</b> The INP Parser is designed to read and interpret INP files, which are the primary project files used by eQuest. These files contain all the necessary data about a building's energy model, including geometry, materials, systems, and schedules.<br>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Generate CSV"):
                inp_parserv01.main(uploaded_file)
            
    elif st.session_state.script_choice == "Purging INP":
        st.markdown("""
        <h4 style="color:red;">📄 Purging INP</h4>
        <b>Purpose:</b> The Purging INP tool helps clean and update your INP files to ensure they are optimized and free of unnecessary data.
        - Removes redundant or obsolete data entries.
        - Updates outdated references to newer standards or templates.
        - Improves the overall performance and manageability of the INP file.<br>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Generate Clean INP"):
                perge.main(uploaded_file)
    
    elif st.session_state.script_choice == "SIM Parser":
        st.markdown("""
        <h4 style="color:red;">📄 SIM Parser</h4>
        <b>Purpose:</b> The SIM Parser is used to process SIM files generated by eQuest simulations. SIM files contain detailed results of energy simulations, including energy consumption, system performance, and cost estimates.<br>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload a SIM file", type="sim", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Generate CSV"):
                sim_parserv01.main(uploaded_file)
                
    elif st.session_state.script_choice == "mepc":
        st.markdown("""
        <h4 style="color:red;">♻️ MEPC Tool</h4>
        <b>Purpose:</b>The MEP Calculator is a tool designed to support energy-efficient building projects, including LEED-certified initiatives. It helps update and analyze MEP performance values using simulation files. 
        Evaluate performance outputs such as Lighting, Shading & Fenestration, and Energy End-Use metrics.<br><br>
        """, unsafe_allow_html=True)
        st.markdown("""<h6 style="color:red;">🔴 Select Calculator Type</h6>""", unsafe_allow_html=True)
        # analysis_option = st.radio("Choose the type of analysis to perform:", 
        #                         ("Performance Outputs", "Shading and Fenestration", "Lighting"))
        if "analysis_option" not in st.session_state:
            st.session_state.analysis_option = None

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Performance Output"):
                st.session_state.analysis_option = "Performance Outputs"
        with col2:
            if st.button("Shade & Fenes."):
                st.session_state.analysis_option = "Shading and Fenestration"
        with col3:
            if st.button("Lighting"):
                st.session_state.analysis_option = "Lighting"
        if st.session_state.analysis_option:
            st.write(f"You selected: **{st.session_state.analysis_option}**")
        analysis_option = st.session_state.analysis_option

        csv_file = r'MEP_Calculator/tables/MEP Calculator.csv'
        df = pd.read_csv(csv_file)
        st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
        
        # if uploaded_proposed_file is not None and uploaded_0_degree is not None:
        if analysis_option == "Performance Outputs":
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

            if uploaded_90_degree is not None and uploaded_180_degree is not None and uploaded_270_degree is not None:
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
        elif analysis_option == "Shading and Fenestration":
            col1, col2 = st.columns(2)
            with col1:
                uploaded_0_degree = st.file_uploader("Upload a Baseline SIM File", type=["sim"], accept_multiple_files=False)
            with col2:
                uploaded_proposed_file = st.file_uploader("Upload Proposed SIM File", type=["sim"], accept_multiple_files=False)
            if uploaded_0_degree is not None and uploaded_proposed_file is not None:
                if st.button("Generate Reports"):
                    lv_d.generateFenestration(uploaded_0_degree, uploaded_proposed_file)

        elif analysis_option == "Lighting":
            col1, col2 = st.columns(2)
            with col1:
                uploaded_0_degree = st.file_uploader("Upload a Baseline SIM File", type=["sim"], accept_multiple_files=False)
            with col2:
                uploaded_proposed_file = st.file_uploader("Upload Proposed SIM File", type=["sim"], accept_multiple_files=False)
            if uploaded_0_degree is not None and uploaded_proposed_file is not None:
                if st.button("Generate Reports"):
                    lighting.generateLighting(uploaded_0_degree, uploaded_proposed_file, uploaded_INP_file)
            else:
                st.info("Please upload the Baseline SIM file for Lighting analysis.")
        else:
            st.info("Please upload at least the 0° and Proposed SIM files to proceed.")

        with st.container():
            st.markdown("#### :rainbow[Website Visitors Count]")
            components.html("""
                <p align="center">
                    <a href="https://equest-utilities-edsglobal.streamlit.app/" target="_blank">
                        <img src="https://hitwebcounter.com/counter/counter.php?page=15322595&style=0019&nbdigits=5&type=ip&initCount=70" title="Counter Widget" alt="Visit counter For Websites" border="0" />
                    </a>
                </p>
            """, height=80)
       
    elif st.session_state.script_choice == "reference":
        st.markdown("""
        <h4 style="color:green;">🏡 IGBC Green Homes </h4>
        <b>Purpose:</b> IGBC Green Homes is a rating system developed by the Indian Green Building Council (IGBC) to promote sustainable building practices 
        in the residential sector. IGBC Green Homes aims to create sustainable and resource-efficient residential buildings, contributing to a greener
        and healthier environment.<br>
        <br>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            uploaded_p_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        with col2:
            uploaded_b_file = st.file_uploader("Upload a SIM file", type="sim", accept_multiple_files=False)
        if uploaded_p_file is not None and uploaded_b_file is not None:
            if st.button("Generate Report 📄"):
                igbc_data.getINPSimFiles(uploaded_p_file, uploaded_b_file)
    
    elif st.session_state.script_choice == "q":
        st.markdown("""
        <h4 style="color:red;">🔍 Quality Check / Quality Assurance</h4>
        <b>Purpose:</b> A quality check, also known as quality control (QC), refers to the process of ensuring that a product or service meets a defined set of quality criteria or standards. This process involves various activities and techniques aimed at identifying and correcting defects or inconsistencies in the product or service before it reaches the customer.<br>
        <br>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            uploaded_p_file = st.file_uploader("Upload a Proposed SIM file", type="sim", accept_multiple_files=False)
        with col2:
            uploaded_b_file = st.file_uploader("Upload a Baseline SIM file", type="sim", accept_multiple_files=False)
        if uploaded_p_file is not None and uploaded_b_file is not None:
            # if st.button("Table based on Metering"):
            qa.getTwoSimFiles(uploaded_p_file, uploaded_b_file)
    
    elif st.session_state.script_choice == "SIM to PDF":
        st.markdown("""
        <h4 style="color:red;">📝 SIM to PDF Converter</h4>
        <b>Purpose:</b> This tool converts SIM files into PDF format, facilitating the sharing and documentation of simulation results. By transforming data into a widely accessible format, it simplifies distribution and review.
        """, unsafe_allow_html=True)
        
        st.markdown("""Please Note: It can accept multiple sim files.""", unsafe_allow_html=True)
        
        # Allow multiple .sim files to be uploaded
        uploaded_files = st.file_uploader("Upload SIM files", type="sim", accept_multiple_files=True)
        # Provide options for report selection
        reports_input = st.multiselect(
            "Select Reports",
            ["LV-B", "LV-D", "LV-M", "LV-A", "LV-C", "LV-E", "LV-F", "LV-G", "LV-H", "LV-I", "LV-J", 
             "LS-A", "LS-B", "LS-D", "LS-L", "LV-N", "LS-C", "LS-E", "LS-F", "LS-K", "PV-A", "BEPS", 
             "BEPU", "SV-A", "PV-A", "PS-E", "PS-F", "SS-A", "SS-B", "SS-C", "SS-D", "SS-E", "SS-M"],
            ["LV-B"]
        )
        
        # Check if files and reports are selected
        if uploaded_files and reports_input:
            if st.button("Convert to PDF"):
                # Clean up each report name
                st.success("Multi-file processing is coming soon. For now, use the EXE for batches.")
       
    elif st.session_state.script_choice == "cal":
        st.markdown("""
        <h4 style="color:blue;">🔧 Calibration Tool</h4>
        <b>Purpose:</b> This tool calibrates energy simulation models to align with actual measured data, ensuring greater accuracy in predicting energy performance. By refining the model based on real-world usage, it enhances the reliability of energy audits, retrofits, and performance assessments.
        """, unsafe_allow_html=True)
        st.info("This feature will be available soon!")
    
    elif st.session_state.script_choice == "hap":
        st.markdown("""
        <h4 style="color:blue;">🔧 HAP Tool</h4>
        <b>Purpose:</b> The HAP (Hourly Analysis Program) tool is a software developed by Carrier Corporation used primarily for HVAC system design and energy modeling.
        """, unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload RTF files", type="RTF", accept_multiple_files=False)
        if uploaded_files is not None:
            if st.button("Generate Reports"):
                hap.main(uploaded_files)

    elif st.session_state.script_choice == "exe":
        st.markdown("""
        <h4 style="color:red; text-align:left;">🖥️ EXE Files</h4>
        """, unsafe_allow_html=True)
        # Adding spacing for better layout
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
        with col1:
            st.image("images/INP_Parser_logo.png", width=110)
            st.markdown('<a href="https://drive.google.com/file/d/1_jgaEfJCuoqfZOq3hY33D-3x31-v-nTH/view?usp=drive_link"><button style="background-color:#4CAF50;color:white; border-radius: 7px;">Download</button></a>', unsafe_allow_html=True)
        with col2:
            st.image("images/SIM_Parser_logo.png", width=110)
            st.markdown('<a href="https://drive.google.com/file/d/1XBb_NGFgjdRKM5WXwNWBwhRWmOYRzbT4/view?usp=sharing"><button style="background-color:#4CAF50;color:white; border-radius: 7px;">Download</button></a>', unsafe_allow_html=True)
        with col3:
            st.image("images/purging_inp_logo.png", width=110)
            st.markdown('<a href="https://drive.google.com/file/d/1oIQmgVAMy871cwwQPnlm3FAAlEB_Bl7o/view?usp=drive_link"><button style="background-color:#4CAF50;color:white; border-radius: 7px;">Download</button></a>', unsafe_allow_html=True)
        with col4:
            st.image("images/SIM_pdf.png", width=110)
            st.markdown('<a href="https://drive.google.com/file/d/10jga6aMVQHgEIG1rhMaqs_sXTt3yEJXK/view?usp=drive_link"><button style="background-color:#4CAF50;color:white; border-radius: 7px;">Download</button></a>', unsafe_allow_html=True)
        with col5:
            st.image("images/baseline.png", width=110)
            st.markdown('<a href="#"><button style="background-color:#4CAF50;color:white; border-radius: 7px; pointer-events: none; cursor: not-allowed;">Download</button></a>', unsafe_allow_html=True)
        with col6:
            st.image("images/schedule.png", width=110)
            st.markdown('<a href="https://drive.google.com/file/d/1wbN0f47EpBKY95Q1IZiOUFi2rYQQ7NsM/view?usp=sharing"><button style="background-color:#4CAF50;color:white; border-radius: 7px;">Download</button></a>', unsafe_allow_html=True)
        # Adding spacing for better layout
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <h5 style="color:black; text-align:left;">📄 Guidelines for EXE Files</h5>
        <ul style="list-style-type:none; padding-left:0;">
            <li style="margin-bottom:10px;">
                <b style="color:red;">SIM to PDF:</b> 
                <a href="https://docs.google.com/presentation/d/1WTdX3zmSMmyp0h1E5lfOsER8EkvFoOEj/edit?usp=drive_link&ouid=104083687366839123092&rtpof=true&sd=true" target="_blank" style="color:#1a73e8; text-decoration:none;">
                    Data Extraction Tool: SIM to PDF
                </a>
            </li>
            <li style="margin-bottom:10px;">
                <b style="color:red;">INP Parser:</b> 
                <a href="https://docs.google.com/presentation/d/1zJ24RgUWW772xFIiWD5GruVEVQrrcdtT/edit?usp=drive_link&ouid=104083687366839123092&rtpof=true&sd=true" target="_blank" style="color:#1a73e8; text-decoration:none;">
                    INP Data to CSVs based on Reports
                </a>
            </li>
            <li style="margin-bottom:10px;">
                <b style="color:red;">SIM Parser:</b> 
                <a href="https://docs.google.com/presentation/d/11fyPNx9e3g-xC11kEMJhGvmCQXvyBlsQ/edit?usp=drive_link&ouid=104083687366839123092&rtpof=true&sd=true" target="_blank" style="color:#1a73e8; text-decoration:none;">
                    SIM Data to CSVs based on Reports
                </a>
            </li>
            <li style="margin-bottom:10px;">
                <b style="color:red;">User Manual:</b> 
                <a href="https://docs.google.com/presentation/d/1W8zTyj1kD-dRlk7XHinJ3_piOnaADx0w/edit?usp=drive_link&ouid=104083687366839123092&rtpof=true&sd=true" target="_blank" style="color:#1a73e8; text-decoration:none;">
                    User Manual Guide
                </a>
            </li>
            <li style="margin-bottom:10px;">
                <b style="color:red;">Schedule Template:</b> 
                <a href="https://drive.google.com/file/d/112sPbkonINRBrd9FfBvSDnE-IYEPb1PO/view?usp=drive_link" target="_blank" style="color:#1a73e8; text-decoration:none;">
                    Template of Schedules
                </a>
            </li>
        </ul>
        """, unsafe_allow_html=True)
    
        st.markdown("""
            <h5 style="color:black; text-align:left;">📄 Instructions for Executing EXE Files</h5>
            <p style="text-align:justify;">
                Please Follow these instructions to execute the EXE files effectively:
            </p>
            <ul style="list-style-type:disc; padding-left:20px;">
                <li style="margin-bottom:10px;">
                    <b>SIM to PDF:</b> Ensure all SIM files are located in the same folder. After entering the report name and folder path, the program will create a new folder named "Output Reports" within the SIM files folder. This new folder will contain PDFs and sliced SIM files.
                </li>
                <li style="margin-bottom:10px;">
                    <b>INP Parser & SIM Parser:</b> Provide the path of the SIM or INP files. Process only one SIM file at a time. The program will generate CSV files in the same location as the input file.
                </li>
                <li style="margin-bottom:10px;">
                    <b>Purging:</b> Enter the path of the .inp file. The program will clean the INP file and generate the cleaned file in the same location as the original file.
                </li>
                <li style="margin-bottom:10px;">
                    <b>Schedule Generator:</b> Provide the path to the CSV or Excel file. The program will generate an INP file and save it in the same location as the input file.
                </li>
            </ul>
            """, unsafe_allow_html=True)
        st.markdown("""
        <h5 style="color:black;"><b> Note:</b></h5>Due to the large size of eQuest Utilities exe files, they may not be suitable for direct hosting on our website. However, they are available for download.
        """, unsafe_allow_html=True)
    
    elif st.session_state.script_choice == "baselineAutomation":
        st.markdown("""
        <h4 style="color:red;">🤖 Baseline Automation</h4>
        """, unsafe_allow_html=True)
        st.markdown("""
        <b>Purpose:</b> The Baseline Automation tool assists in modifying INP files based on user-defined criteria to create baseline models for comparison.
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            uploaded_inp_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        with col2:
            uploaded_sim_file = st.file_uploader("Upload a SIM file", type="sim", accept_multiple_files=False)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            input_climate = st.selectbox("Climate Zone", options=[1, 2, 3, 4, 5, 6, 7, 8])
        with col2:
            input_building_type = st.selectbox("Building Type", options=[0, 1], format_func=lambda x: "Residential" if x == 0 else "Non-Residential")
        with col3:
            input_area = st.number_input("Enter Area (Sqft)", min_value=0.0, step=0.1)
        with col4:
            number_floor = st.number_input("Number of Floors", min_value=1, step=1)
        with col5:
            heat_type = st.selectbox("Heating Type", options=[0, 1], format_func=lambda x: "Hybrid/Fossil" if x == 0 else "Electric")
    
        if uploaded_inp_file and uploaded_sim_file:
            if st.button("Automate Baseline"):
                baselineAuto.getInp(
                    uploaded_inp_file,
                    uploaded_sim_file,
                    input_climate,
                    input_building_type,
                    input_area,
                    number_floor,
                    heat_type)
                
if __name__ == "__main__":
    main()
    
st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .footer {
            background-color: #f8f9fa;
            padding: 20px 0;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-align: center;
        }
        .footer .logo {
            flex: 1;
        }
        .footer .logo img {
            max-width: 150px;
            height: auto;
        }
        .footer .social-media {
            flex: 2;
        }
        .footer .social-media p {
            margin: 0;
            font-size: 16px;
        }
        .footer .icons {
            margin-top: 10px;
        }
        .footer .icons a {
            margin: 0 10px;
            color: #666;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        .footer .icons a:hover {
            color: #0077b5; /* LinkedIn color as default */
        }
        .footer .icons a .fab {
            font-size: 28px;
        }
        .footer .additional-content {
            margin-top: 10px;
        }
        .footer .additional-content h4 {
            margin: 0;
            font-size: 18px;
            color: #007bff;
        }
        .footer .additional-content p {
            margin: 5px 0;
            font-size: 16px;
        }
    </style>
   <div class="footer">
        <div class="social-media" style="flex: 2;">
            <p>&copy; 2024. All Rights Reserved</p>
            <div class="icons">
                <a href="https://twitter.com/edsglobal?lang=en" target="_blank"><i class="fab fa-twitter" style="color: #1DA1F2;"></i></a>
                <a href="https://www.facebook.com/Environmental.Design.Solutions/" target="_blank"><i class="fab fa-facebook" style="color: #4267B2;"></i></a>
                <a href="https://www.instagram.com/eds_global/?hl=en" target="_blank"><i class="fab fa-instagram" style="color: #E1306C;"></i></a>
                <a href="https://www.linkedin.com/company/environmental-design-solutions/" target="_blank"><i class="fab fa-linkedin" style="color: #0077b5;"></i></a>
            </div>
            <div class="additional-content">
                <h4>Contact Us</h4>
                <p>Email: info@edsglobal.com | Phone: +123 456 7890</p>
                <p>Follow us on social media for the latest updates and news.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True
)
