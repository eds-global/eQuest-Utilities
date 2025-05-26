import os
import pandas as pd
from igbc.src import igbc_parser
import streamlit as st
import tempfile
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

def getINPSimFiles(input_simp_path, input_simb_path):
    if input_simp_path is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(input_simp_path.getbuffer())
            sim_p_path = temp_file.name
    else:
        st.error("Error: No input for simulation P file.")
        return
    
    if input_simb_path is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(input_simb_path.getbuffer())
            sim_b_path = temp_file.name
    else:
        st.error("Error: No input for simulation B file.")
        return
    
    sim_p_path = sim_p_path.replace('\n', '\r\n')
    sim_b_path = sim_b_path.replace('\n', '\r\n')

    get_report1, get_report2 = igbc_parser.get_HVAC_Zone_report(sim_p_path, sim_b_path)
    get_report1 = get_report1.fillna('')
    get_report2 = get_report2.fillna('')
    csv1 = get_report1.to_csv("report1.csv")
    csv2 = get_report2.to_csv("report1.csv")

    if get_report1 is not None:
        st.markdown(f"""<h7 style="color:green;">🏡 Table representing Openable Area to Carpet Area</h7>""", unsafe_allow_html=True)
        st.write(get_report1)
        # Convert DataFrame to CSV string
        csv1 = get_report1.to_csv(index=False)
        st.download_button(
            label="Download Report",
            data=csv1,
            file_name='report1.csv',
            mime='text/csv'
        )
    else:
        st.info("Data Not found for Report 1!")
    
    if get_report2 is not None:
        st.markdown(f"""<h7 style="color:green;">🏡 Table representing Daylight and regularly occupied spaces Meet or Exceed the critaria</h7>""", unsafe_allow_html=True)
        # Apply conditional formatting
        def color_cells(val):
            if val == 'YES':
                return 'background-color: green; color: white'
            elif val == 'NO':
                return 'background-color: red; color: white'
            else:
                return ''
        
        # Apply the style to the last column
        last_col_name = get_report2.columns[-3]
        styled_df = get_report2.style.applymap(color_cells, subset=[last_col_name])
        
        # st.write(get_report2)
        st.dataframe(styled_df)
        # Convert DataFrame to CSV string
        csv2 = get_report2.to_csv(index=False)
        st.download_button(
            label="Download Report",
            data=csv2,
            file_name='report2.csv',
            mime='text/csv'
        )
    else:
        st.info("Data Not found for Report 2!")
