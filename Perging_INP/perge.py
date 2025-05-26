import os
import streamlit as st
import tempfile
from Perging_INP.src_perge import perging, CLM_delete

def update_inp_file(uploaded_file):
    if uploaded_file is not None:
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the uploaded file temporarily
                inp_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(inp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                inp_path = inp_path.replace('\n', '\r\n')
                # Perform perging operations
                perge_data_annual = perging.perging_data_annual(inp_path)
                perge_data_weekly = perging.perging_data_weekly(perge_data_annual)
                perge_data_day = perging.perging_data_day(perge_data_weekly)
                construction_delete = CLM_delete.perging_data_const(perge_data_day)
                layers_delete = CLM_delete.perging_data_layer(construction_delete)
                material_delete = CLM_delete.perging_data_material(layers_delete)
                
                # Create the updated INP file
                base_name, ext = os.path.splitext(uploaded_file.name)
                updated_file_name = f"{base_name}_updated{ext}"
                updated_file_path = os.path.join(temp_dir, updated_file_name)

                with open(updated_file_path, 'w',newline= '\r\n') as file:
                    file.writelines(material_delete)
                
                # Read the updated file content
                with open(updated_file_path, 'rb') as file:
                    file_content = file.read()

                return file_content, updated_file_name  # Return the file content and name
        except Exception as e:
            st.error(f"An error occurred while updating INP file: {e}")
            return None, None

def main(uploaded_file):
    file_content, updated_file_name = update_inp_file(uploaded_file)
    if file_content and updated_file_name:
        st.success("INP Updated Successfully!")
        # Provide download link for the updated INP file
        st.download_button(
            label="Download Updated INP",
            data=file_content,
            file_name=updated_file_name,
            mime='text/plain'
        )

if __name__ == "__main__":
    uploaded_file = st.file_uploader("Upload your INP file", type=["inp"])
    main(uploaded_file)
