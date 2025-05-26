import streamlit as st
import subprocess
import os
import pandas as pd
from streamlit_card import card
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tempfile
from src import ps_e, bepu, lv_d, lighting

st.set_page_config(
    page_title="MEP Calculator",
    page_icon="♻️",
    layout='wide'
)

button_style = """
    <style>
        .stButton>button {
            box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.8);
        }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)
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
        
    logo_image_path = "images/energy.jpeg"
    _, col2, col3 = st.columns([1, 1, 0.5])
    with col2:
        st.markdown("<h1 class='heading-with-shadow'>MEP Calculator</h1>", unsafe_allow_html=True)
    with col3:
        st.image("images/EDSlogo.jpg", width=120)

    st.markdown("""
        <style>
        .stButton button {
            height: 30px;
            width: 265px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="border: 2px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9;">
        <h4 style="color: red;">♻️ MEP Calculator</h4>
        <p>The <b>MEP Calculator</b> is a tool designed to support energy-efficient building projects, including LEED-certified initiatives. It helps update and analyze MEP performance values using simulation files.</p>
        <p><b>Purpose:</b> Evaluate performance outputs such as <b>Lighting</b>, <b>Shading & Fenestration</b>, and <b>Energy End-Use</b> metrics.</p>
        <p><b>Note:</b> For <span style="color:blue;"><b>Performance Outputs</b></span>, upload exactly <b>4 Baseline SIM files</b> (rotations: 0°, 90°, 180°, 270°) and <b>1 Proposed SIM file</b>.<br>
        Other analysis options (e.g., Lighting, Shading & Fenestration) may require fewer files.</p>
    </div>
    """, unsafe_allow_html=True)
    
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

    csv_file = r'tables/MEP Calculator.csv'
    df = pd.read_csv(csv_file)

    st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
    st.markdown("""<h6 style="color:red;">🔴 Select Calculator Type</h6>""", unsafe_allow_html=True)
    analysis_option = st.radio("Choose the type of analysis to perform:", 
                            ("Performance Outputs", "Shading and Fenestration", "Lighting"))

    if uploaded_proposed_file is not None and uploaded_0_degree is not None:
        if analysis_option == "Performance Outputs":
            if uploaded_90_degree is not None and uploaded_180_degree is not None and uploaded_270_degree is not None:
                if st.button("Process Performance Outputs"):
                    st.markdown(
                        """
                        <div style='background-color:#fff3cd;padding:10px;border-left:6px solid #ffecb5;'>
                            <strong>Disclaimer:</strong> Currently, only <strong>electricity</strong> outputs are processed.<br>
                            Units used are <strong>kWh</strong> (Consumption) and <strong>kW</strong> (Demand).
                        </div><br>
                        """,
                        unsafe_allow_html=True
                    )
                    ps_e.get_END_USE_Proposed(df, uploaded_0_degree, uploaded_90_degree, uploaded_180_degree, uploaded_270_degree, uploaded_proposed_file)
            else:
                st.info("Please upload all 4 rotation SIM files for Performance Outputs.")

        elif analysis_option == "Shading and Fenestration":
            if st.button("Process Shading and Fenestration"):
                lv_d.generateFenestration(uploaded_0_degree, uploaded_proposed_file)

        elif analysis_option == "Lighting":
            if uploaded_0_degree is not None:
                uploaded_INP_file = st.file_uploader("Upload a INP file", type=["inp"], accept_multiple_files=False)
                if st.button("Process Lighting"):
                    lighting.generateLighting(uploaded_0_degree, uploaded_proposed_file, uploaded_INP_file)
            else:
                st.info("Please upload the Baseline SIM file for Lighting analysis.")
    else:
        st.info("Please upload at least the 0° and Proposed SIM files to proceed.")

if __name__ == "__main__":
    main()

st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
    .social-media {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .social-media a {
        margin: 0 10px;
        text-decoration: none;
        color: blue;
    }
    .social-media i {
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <div class="social-media" style="margin-top: 10px;">
        <p>@2024. All Rights Reserved</p>
        <a href="https://twitter.com/edsglobal?lang=en" target="_blank"><i class="fab fa-twitter"></i></a>
        <a href="https://www.facebook.com/Environmental.Design.Solutions/" target="_blank"><i class="fab fa-facebook"></i></a>
        <a href="https://www.instagram.com/eds_global/?hl=en" target="_blank"><i class="fab fa-instagram"></i></a>
        <a href="https://www.linkedin.com/company/environmental-design-solutions/" target="_blank"><i class="fab fa-linkedin"></i></a>
    </div>
    """,
    unsafe_allow_html=True
)