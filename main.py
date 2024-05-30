import streamlit as st
import tempfile
from INP_Parser import inp_parserv01
from Perging_INP import perge
from SIM_Parser import sim_parserv01
from SIM2PDF import sim_print
from BaselineAutomation import baselineAuto

def main():
    st.set_page_config(page_title="eQuest Utilities", page_icon="💡")

    # Add custom CSS to set the background color and hide Streamlit branding elements
    st.markdown(
        """
        <style>
        body {
            background-color: #f0f2f6;  /* Set your desired background color here */
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

    # Header section with logo and title
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("EDSlogo.png", width=120)  # Replace with the path to your logo file
    with col2:
        st.markdown("<h1 style='text-align: left;'>eQuest Utilities</h1>", unsafe_allow_html=True)

    # Navigation bar with buttons below the header
    st.markdown("---")
    col3, col4, col5, col6 = st.columns([1, 1, 1, 1])
    with col3:
        if st.button("About eQuest"):
            st.session_state.script_choice = "about"
    with col4:
        if st.button("INP Parser"):
            st.session_state.script_choice = "INP Parser"
    with col5:
        if st.button("Purging INP"):
            st.session_state.script_choice = "Purging INP"
    with col6:
        if st.button("SIM Parser"):
            st.session_state.script_choice = "SIM Parser"
    
    col7, col8 = st.columns([1, 1])
    with col7:
        if st.button("SIM to PDF"):
            st.session_state.script_choice = "SIM to PDF"
    with col8:
        if st.button("Baseline Automation"):
            st.session_state.script_choice = "baselineAutomation"

    # Based on the user selection, display appropriate input fields and run the script
    if st.session_state.script_choice == "about":
        st.markdown("""
        ### Welcome to eQuest Utilities

        eQuest Utilities is a comprehensive suite of tools designed to help you work with eQuest more efficiently. 
        Our utilities include:

        - **INP Parser:** A tool to parse INP files and extract meaningful data.
        - **Purging INP:** A utility to update and clean your INP files.
        - **SIM Parser:** A parser for SIM files to streamline your simulation data processing.
        - **SIM to PDF Converter:** Easily convert your SIM files into PDF format for better sharing and documentation.

        Navigate through the tools using the buttons above to get started. Each tool is designed to simplify 
        specific tasks related to eQuest project management. We hope these utilities make your workflow smoother 
        and more productive.
        """)

    elif st.session_state.script_choice == "INP Parser":
        st.header("INP Parser")
        uploaded_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Run INP Parser"):
                inp_parserv01.main(uploaded_file)

    elif st.session_state.script_choice == "Purging INP":
        st.header("Purging INP")
        uploaded_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Run INP Purging"):
                perge.main(uploaded_file)

    elif st.session_state.script_choice == "SIM Parser":
        st.header("SIM Parser")
        uploaded_file = st.file_uploader("Upload a SIM file", type="sim", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Run SIM Parser"):
                sim_parserv01.main(uploaded_file)

    elif st.session_state.script_choice == "SIM to PDF":
        st.header("SIM to PDF Converter")
        st.success("Will be updated soon")
        # uploaded_file = st.file_uploader("Upload a SIM file", type="sim", accept_multiple_files=False)
        
        # if uploaded_file is not None:
        #     if st.button("Convert to PDF"):
        #         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        #             sim_print.main(uploaded_file, tmp_file.name)
        #             st.download_button("Download PDF", data=tmp_file.name, file_name="converted.pdf")

    elif st.session_state.script_choice == "baselineAutomation":
        st.header("Baseline Automation")
        uploaded_inp_file = st.file_uploader("Upload an INP file", type="inp", accept_multiple_files=False)
        uploaded_sim_file = st.file_uploader("Upload a SIM file", type="sim", accept_multiple_files=False)
        input_climate = st.selectbox("Enter the Climate Zone", options=[1, 2, 3, 4, 5, 6, 7, 8])
        input_building_type = st.selectbox("Enter the Building Type (0 - Resdential), (1 - Non-Residential)", options=[0, 1])
        input_area = st.number_input("Enter area", min_value=0.0, step=0.1)
        number_floor = st.number_input("Enter floor number", min_value=0, step=1)
        heat_type = st.selectbox("Enter Heating Type", options=[0, 1])

        if uploaded_inp_file and uploaded_sim_file:
            if st.button("Run Baseline Automation"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp_inp_file, \
                     tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp_out_file:

                    # Read and write the uploaded INP and SIM files to temporary files
                    inp_content = uploaded_inp_file.read().decode('utf-8')
                    sim_content = uploaded_sim_file.read().decode('utf-8')
                    
                    tmp_inp_file.write(inp_content.encode('utf-8'))
                    tmp_inp_file.flush()
                    
                    tmp_out_file.close()  # Close the output file to pass its name

                    # Run baseline automation
                    baselineAuto.main(
                        tmp_inp_file.name,
                        sim_content,
                        input_climate,
                        input_building_type,
                        input_area,
                        number_floor,
                        heat_type,
                        tmp_out_file.name
                    )

                    # Provide download button for the updated INP file
                    st.download_button("Download Updated INP File", data=open(tmp_out_file.name, 'rb').read(), file_name="updated_baseline.inp")

if __name__ == "__main__":
    main()
