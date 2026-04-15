import os
import re
import streamlit as st
import tempfile
from BaselineAutomation.src import update_MLC, insertConst, insertGlass, wwr, updateHVAC, HVAC_sys, perging, CLM_delete, update_lpd, updateFreshAir, aa, freshAir

def getInp(input_inp_path, sim_file_path, input_climate, input_building_type, input_area, number_floor, heat_type):

    if input_inp_path is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(input_inp_path.getbuffer())
            temp_file_path = temp_file.name
        inp_path = temp_file_path

    if sim_file_path is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(sim_file_path.getbuffer())
            temp_file_path = temp_file.name
        sim_path = temp_file_path

    # Convert inputs to appropriate types
    input_climate = int(input_climate)
    input_building_type = int(input_building_type)
    input_area = float(input_area)
    number_floor = int(number_floor)
    heat_type = int(heat_type)

    if input_climate < 1 or input_climate > 8 or input_building_type > 1 or input_building_type < 0:
        st.error("Error: Climate input or Building type is Wrong!\n")
        return

    # Get climate and system paths
    climate_path = update_MLC.get_climate_path(input_climate, input_building_type)
    system_path = update_MLC.get_system_path(input_building_type, heat_type, input_area, number_floor)

    # Create placeholder just once at the start
    message_placeholder = st.empty()
    all_msgs = []
    
    # Convert paths to absolute paths
    climate_path = os.path.abspath(climate_path)
    system_path = os.path.abspath(system_path)

    # Extract just the filenames
    climate_file = os.path.basename(climate_path)
    system_file = os.path.basename(system_path)

    # Inline display
    all_msgs.append(f"<span style='color:blue;'>📁 Climate INP:</span> {climate_file}")
    all_msgs.append(f"<span style='color:blue;'>📁 System Data:</span> {system_file}")

    message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)
    inp_path = inp_path.replace('\n', '\r\n')
    
    if os.path.isfile(inp_path):
        ###################################################### FRESH AIR ##################################################
        zone_space_df = aa.zoneSpace(inp_path)
        modify_dataframe = updateFreshAir.updateBCVentilation(zone_space_df, inp_path, sim_path)
        modify_freshAi = freshAir.updateFresh(modify_dataframe, inp_path)
        modify_freshAir = freshAir.remove_OAs(modify_freshAi)
        all_msgs.append("<span style='color:green;'>✅ Fresh Air Updated</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        ######################################################## MLC INSERTION #############################################
        mat_data = update_MLC.insert_material_data(climate_path, modify_freshAir)
        all_msgs.append("<span style='color:green;'>✅ Inserted Material Data</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        lyr_data = update_MLC.insert_layers_data(climate_path, mat_data)
        all_msgs.append("<span style='color:green;'>✅ Inserted Layer Data</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        const_data = update_MLC.insert_const_data(climate_path, lyr_data)
        all_msgs.append("<span style='color:green;'>✅ Construction Data Inserted</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        ######################################################## W,R,U Updated ##############################################
        update_ConstName = insertConst.update_external_wall_roof_undergrnd(const_data)
        all_msgs.append("<span style='color:green;'>✅ Construction names updated</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        ######################################################## GLASS INSERTION #############################################
        updateGlass = insertGlass.update_glass(climate_path, update_ConstName)
        all_msgs.append("<span style='color:green;'>✅ Inserted Glass Data</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        updateGlassType = insertGlass.update_glass_type(climate_path, updateGlass)
        all_msgs.append("<span style='color:green;'>✅ Glass-Type Data Updated</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        ######################################################## WWR #########################################################
        updateWWR = wwr.UpdateWWR(sim_path, updateGlassType)
        all_msgs.append("<span style='color:green;'>✅ Updated WWR > 0.4</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        ######################################################## HVAC #########################################################
        modifyHVAC = updateHVAC.HVAC_Modification(updateWWR)
        all_msgs.append("<span style='color:green;'>✅ HVAC Updated</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        hvac_sys = HVAC_sys.systems(modifyHVAC, system_path)
        all_msgs.append("<span style='color:green;'>✅ HVAC Data Replaced</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        value = system_path.split(".inp")[0][-1]
        if value in ['1', '2', '3', '4']:
            update_zone = HVAC_sys.modify_conditioned(hvac_sys, system_path)
            all_msgs.append("<span style='color:green;'>✅ Conditioned Zone Updated</span>")
        else:
            update_zone = HVAC_sys.modify_floor(hvac_sys, system_path)
            all_msgs.append("<span style='color:green;'>✅ Floor Updated</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        ######################################################### LPD #########################################################
        modify_lpd = update_lpd.updateLPD(update_zone, sim_path)
        all_msgs.append("<span style='color:green;'>✅ LPD Updated</span>")
        all_msgs.append("<span style='color:green;'>✅ Fresh Air Updated!!</span>")
        message_placeholder.markdown(" &nbsp; | &nbsp; ".join(all_msgs), unsafe_allow_html=True)

        # ######################################################### FRESH AIR ###################################################
        # zone_space_df = aa.zoneSpace(input_inp_path)
        # modify_dataframe = updateFreshAir.updateBCVentilation(zone_space_df, modify_lpd, input_sim_path)
        # modify_freshAir = freshAir.updateFresh(modify_dataframe, modify_lpd)

        # ######################################################### FRESH AIR ###################################################
        # modify_freshAir = updateFreshAir.updateBCVentilation(modify_lpd, sim_path)
        # st.success("FreshAir Updated!!\n")

        ###################################################### PURGING #######################################################
        ##### Removing unique value from data or purging ######
        # perge_data_annual = perging.perging_data_annual(modify_lpd)
        # perge_data_weekly = perging.perging_data_weekly(perge_data_annual)
        # perge_data_day = perging.perging_data_day(perge_data_weekly)
        # construction_delete = CLM_delete.perging_data_const(perge_data_day)
        # layers_delete = CLM_delete.perging_data_layer(construction_delete)
        # material_delete = CLM_delete.perging_data_material(layers_delete)
         
        directory_path, filename = os.path.split(inp_path)
        new_filename = re.sub(r'\.inp?$', '_Baseline_Automation.inp', filename, flags=re.IGNORECASE)
        input_inp_ = input_inp_path.name.split('.')[0]
        
        # Write modified inp file 
        with open(new_filename, 'w', newline = '\r\n') as file:
            file.writelines(modify_lpd)

        with open(new_filename, 'rb') as f:
            st.download_button(
                label="Download Updated INP",
                data=f,
                file_name=f"{os.path.basename(input_inp_)}_Baseline_Automation.inp",
            )

if __name__ == "__main__":
    # You can add code here to accept input from the command line if desired
    pass
