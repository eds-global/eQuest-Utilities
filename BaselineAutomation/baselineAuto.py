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
    
    # Convert paths to absolute paths
    climate_path = os.path.abspath(climate_path)
    system_path = os.path.abspath(system_path)
    st.success(f"Climate INP: {climate_path}")
    st.success(f"System data: {system_path}")
    inp_path = inp_path.replace('\n', '\r\n')
    
    if os.path.isfile(inp_path):
        ###################################################### FRESH AIR ##################################################
        zone_space_df = aa.zoneSpace(inp_path)
        modify_dataframe = updateFreshAir.updateBCVentilation(zone_space_df, inp_path, sim_path)
        modify_freshAi = freshAir.updateFresh(modify_dataframe, inp_path)
        modify_freshAir = freshAir.remove_OAs(modify_freshAi)
        
        ######################################################## MLC INSERTION #############################################
        mat_data = update_MLC.insert_material_data(climate_path, modify_freshAir)
        st.success("Inserted Material Data")
        lyr_data = update_MLC.insert_layers_data(climate_path, mat_data)
        st.success("Inserted Layer Data")
        const_data = update_MLC.insert_const_data(climate_path, lyr_data)
        st.success("Construction Data Inserted")
        
        ######################################################## W,R,U Updated ##############################################
        update_ConstName = insertConst.update_external_wall_roof_undergrnd(const_data)
        st.success("In MLC:- Construction name based on Wall, roof and underground is updated")

        ######################################################## GLASS INSERTION #############################################
        updateGlass = insertGlass.update_glass(climate_path, update_ConstName)
        st.success("Inserted Glass Data")
        updateGlassType = insertGlass.update_glass_type(climate_path, updateGlass)
        st.success("Glass-Type Data is Updated by All Win")

        ######################################################## WWR #########################################################
        updateWWR = wwr.UpdateWWR(sim_path, updateGlassType)
        st.success("Updated WWR if ratio > 0.4")

        # ######################################################## HVAC #########################################################
        modifyHVAC = updateHVAC.HVAC_Modification(updateWWR)
        st.success("HVAC_Updated (All System Deleted)")
        hvac_sys = HVAC_sys.systems(modifyHVAC, system_path)
        st.success("Data Replaces HVAC")
        value = system_path.split(".inp")[0][-1]
        if value in ['1', '2', '3', '4']:
            update_zone = HVAC_sys.modify_conditioned(hvac_sys, system_path)
            st.success("Conditioned_zone updated")
        else:
            update_zone = HVAC_sys.modify_floor(hvac_sys, system_path)
            st.success("Floor updated")
    
        ######################################################### LPD #########################################################
        modify_lpd = update_lpd.updateLPD(update_zone, sim_path)
        st.success("LPD Updated")
        st.success("FreshAir Updated!!")

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
