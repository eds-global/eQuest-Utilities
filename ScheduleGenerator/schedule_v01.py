import pandas as pd
import streamlit as st
from ScheduleGenerator.src import schedule
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np

def get_file_extension(uploaded_file):
    return uploaded_file.name.split('.')[-1]

def get_schedule(uploaded_file):
    try:
        if uploaded_file is not None:
            file_extension = get_file_extension(uploaded_file)
            if file_extension == 'csv':
                schedules = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
            elif file_extension == 'xlsx':
                schedules = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a CSV or XLSX file.")
                return
            count = 1
            # Iterate through the first column and count occurrences of "Schedule Name"
            for index, value in schedules.iloc[:, 0].items():
                if value == 'Schedule Name':
                    count += 1
            if count == 1:
                schedule.getScheduleINP(schedules)
            else:
                # Convert columns to the first row
                schedules.loc[-1] = schedules.columns
                schedules.index = schedules.index + 1
                schedules = schedules.sort_index()

                # Find the index of the last occurrence of 'Hour' in the first column
                last_hour_index = schedules[schedules['Schedule Name'] == 'Month'].index[-1]
                last_most_df = schedules.iloc[last_hour_index:]

                first_df = schedules.iloc[0:6]
                data = [
                    ["Rows can be added to add more weekly schedule"] + [None]*24,
                    ["Week Schedule"] + [None]*24,
                    ["Names"] + [None]*24,
                    ["Day", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Holidays", "Heating Design Day", "Cooling Design Day"] + [None]*14
                ]
                mid_df = pd.DataFrame(data)
                # Extract column names from df1
                column_names = schedules.columns
                # Assign column names of df1 to df2
                mid_df.columns = column_names

                data1 = [
                    ["Rows can be added to add more weekly schedule"] + [None]*24,
                    ["Annual Schedule"] + [None]*24,
                    ["Name"] + [None]*24,
                ]

                last_df = pd.DataFrame(data1)
                # Extract column names from df1
                column_names = schedules.columns
                # Assign column names of df1 to df2
                last_df.columns = column_names

                schedules = schedules.drop(schedules.index[:5])
                # List of values to be removed
                values_to_remove = [
                    "Rows can be added to add more weekly schedule",
                    "Schedule Type:",
                    "Day Schedule",
                    "Week Schedule",
                    "Names",
                    "Name",
                    "Schedule Name",
                    np.nan  # This handles NaN and empty values
                ]
                # Filter out rows with specified values in the first or second column
                schedules = schedules[~schedules.iloc[:, 0].isin(values_to_remove) & ~schedules.iloc[:, 1].isin(values_to_remove)]
                # Find indices of 'Hour' and 'Day'-'Monday' pairs
                hour_indices = schedules[schedules["Schedule Name"] == "Hour"].index.tolist()
                day_monday_indices = schedules[(schedules["Schedule Name"] == "Day") & (schedules.iloc[:, 1] == "Monday")].index.tolist()

                # Initialize a list to store the new DataFrame rows
                new_rows = []

                # Iterate through each pair of 'Day' and 'Monday' indices
                for day_index in day_monday_indices:
                    # Find the last 'Hour' index before the current 'Day'-'Monday' pair
                    hour_index = max([idx for idx in hour_indices if idx < day_index], default=-1)
                    
                    if hour_index != -1:
                        # Extract rows between 'Hour' and ('Day' and 'Monday')
                        sub_df = schedules.loc[hour_index+1:day_index]
                        
                        # Add 'Day' and 'Monday' to each row
                        for _, sub_row in sub_df.iterrows():
                            new_row = sub_row.to_dict()
                            new_row["Day"] = schedules.at[day_index, "Schedule Name"]
                            new_rows.append(new_row)

                # Create the new DataFrame
                df_hr = pd.DataFrame(new_rows)

                # Ensure 'Schedule Name', 'Arena Occup Ann Sch', and other columns are in the desired order
                column_order = ["Schedule Name"] + [col for col in schedules.columns if col not in ["Schedule Name"]]
                df_hr = df_hr[column_order]
                df_hr = df_hr[~df_hr['Schedule Name'].str.contains('Day')]

                # Find indices of 'month' and 'Day'-'Monday' pairs
                day_monday_indices = schedules[(schedules["Schedule Name"] == "Day") & (schedules.iloc[:, 1] == "Monday")].index.tolist()
                month_indices = schedules[schedules["Schedule Name"] == "Month"].index.tolist()

                # Initialize a list to store the new DataFrame rows
                new_rows = []

                # Iterate through each pair of 'Day' and 'Monday' indices
                for month_index in month_indices:
                    # Find the last 'Month' index before the current 'Day'-'Monday' pair
                    day_index = max([idx for idx in day_monday_indices if idx < month_index], default=-1)
                    
                    if day_index != -1:
                        # Extract rows between 'Hour' and ('Day' and 'Monday')
                        sub_df = schedules.loc[day_index+1:month_index]
                        
                        # Add 'Day' and 'Monday' to each row
                        for _, sub_row in sub_df.iterrows():
                            new_row = sub_row.to_dict()
                            new_row["Month"] = schedules.at[month_index, "Schedule Name"]
                            new_rows.append(new_row)

                # Create the new DataFrame
                df_day = pd.DataFrame(new_rows)

                # Ensure 'Schedule Name', 'Arena Occup Ann Sch', and other columns are in the desired order
                column_order = ["Schedule Name"] + [col for col in schedules.columns if col not in ["Schedule Name"]]
                df_day = df_day[column_order]
                df_day = df_day[~df_day['Schedule Name'].str.contains('Month')]

                # Find indices of 'month' and 'hour'
                month_indices = schedules[schedules["Schedule Name"] == "Month"].index.tolist()
                hour_indices = schedules[schedules["Schedule Name"] == "Hour"].index.tolist()

                # Initialize a list to store the new DataFrame rows
                new_rows = []

                # Iterate through each pair of 'Day' and 'Monday' indices
                for hour_index in hour_indices:
                    # Find the last 'Month' index before the current 'Day'-'Monday' pair
                    month_index = max([idx for idx in month_indices if idx < hour_index], default=-1)
                    
                    if month_index != -1:
                        # Extract rows between 'Hour' and ('Day' and 'Monday')
                        sub_df = schedules.loc[month_index:hour_index]
                        
                        # Add 'Day' and 'Monday' to each row
                        for _, sub_row in sub_df.iterrows():
                            new_row = sub_row.to_dict()
                            new_row["Hour"] = schedules.at[hour_index, "Schedule Name"]
                            new_rows.append(new_row)

                # Create the new DataFrame
                df_month = pd.DataFrame(new_rows)

                # Ensure 'Schedule Name', 'Arena Occup Ann Sch', and other columns are in the desired order
                column_order = ["Schedule Name"] + [col for col in schedules.columns if col not in ["Schedule Name"]]
                df_month = df_month[column_order]
                df_month = df_month[~df_month['Schedule Name'].str.contains('Hour')]

                new_df = pd.concat([first_df, df_hr, mid_df, df_day, last_df, df_month], ignore_index=True, axis=0)

                schedules_df = pd.concat([new_df, last_most_df], ignore_index=False, axis=0)
                schedules_df = schedules_df.iloc[1:]
                # Resetting the index
                schedules_df.reset_index(drop=True, inplace=True)
                schedule.getScheduleINP(schedules_df)
        else:
            st.info("Please upload a file to view Analytics.")
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        
def plot_chart(df, hour_column, value_column):
    # Create a bar chart
    fig, ax = plt.subplots(figsize=(8, 4))  # Adjust size as needed
    ax.bar(df[hour_column], df[value_column], color='blue')

    # Set the labels and title
    ax.set_xlabel('Hour')
    ax.set_ylabel('Fraction')
    ax.set_title(f'{value_column}')

    # Ensure all x-axis values from 1 to 24 are visible
    ax.set_xticks(range(1, 25))

    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=45)

    # Adjust layout
    plt.tight_layout()

    return fig

def save_chart_as_image(fig, filename):
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

def download_image_as_file(buffer, filename):
    st.markdown(get_image_download_link(buffer, filename), unsafe_allow_html=True)

def get_image_download_link(buffer, filename):
    buffer_str = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:file/png;base64,{buffer_str}" download="{filename}">Download {filename}</a>'
    return href

def combine_images_as_document(image_buffers):
    combined_fig = plt.figure(figsize=(10, 6))
    num_images = len(image_buffers)
    cols = 2
    rows = (num_images + 1) // cols  # Ensure enough rows for all images

    for i, buffer in enumerate(image_buffers):
        image = plt.imread(BytesIO(buffer.getvalue()), format='png')
        combined_fig.add_subplot(rows, cols, i + 1)
        plt.imshow(image)
        plt.axis('off')

    plt.tight_layout()
    combined_buffer = BytesIO()
    combined_fig.savefig(combined_buffer, format='png')
    combined_buffer.seek(0)
    plt.close(combined_fig)
    return combined_buffer

def analytics(uploaded_file):
    try:
        if uploaded_file is not None:
            file_extension = get_file_extension(uploaded_file)
            if file_extension == 'csv':
                data = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
            elif file_extension == 'xlsx':
                data = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a CSV or XLSX file.")
                return

            st.markdown("""
            <h4 style="color:red;">Daily Schedules of 24 hours</h4>
            """, unsafe_allow_html=True)

            # Your data processing code
            data = data.drop([0, 3])
            first_col_name = data.columns[0]
            index_to_drop_from = data[data[first_col_name] == "Rows can be added to add more weekly schedule"].index[0]
            data = data[:index_to_drop_from]

            df_rotated = data.T
            df_rotated.columns = df_rotated.iloc[0]
            df_rotated = df_rotated[1:]
            df_rotated.reset_index(drop=True, inplace=True)
            df_rotated = df_rotated.iloc[:, 2:-2]
            df_rotated = df_rotated.apply(pd.to_numeric)
            hour_column = 'Hour'
            if hour_column not in df_rotated.columns:
                raise ValueError(f"'{hour_column}' column not found in the DataFrame")

            value_columns = df_rotated.columns[df_rotated.columns.get_loc(hour_column) + 1:]

            # Display charts in rows of two
            num_charts = len(value_columns)
            num_cols = 2
            num_rows = (num_charts + 1) // num_cols  # Calculate number of rows needed

            for i, value_column in enumerate(value_columns):
                if i % num_cols == 0:
                    columns = st.columns(num_cols)  # Create columns layout
                fig_chart = plot_chart(df_rotated, hour_column, value_column)
                with columns[i % num_cols]:  # Place chart in the current column
                    st.pyplot(fig_chart)

                    # Add a download button for the plot
                    buffer = BytesIO()
                    fig_chart.savefig(buffer, format='png')
                    buffer.seek(0)
                    st.download_button(
                        # label=f"Download {value_column} chart",
                        label=f"Download",
                        data=buffer,
                        file_name=f"bar_chart_{value_column}.png",
                        mime="image/png"
                    )

        else:
            st.markdown("""
            <h5 style="color:red;">📈 Please upload excel file to View Analytics </h5>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

def analytics1(uploaded_file):
    try:
        if uploaded_file is not None:
            file_extension = get_file_extension(uploaded_file)
            if file_extension == 'csv':
                data = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
            elif file_extension == 'xlsx':
                data = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a CSV or XLSX file.")
                return

            data = data.drop([0, 3])
            first_col_name = data.columns[0]
            index_to_drop_from = data[data[first_col_name] == "Rows can be added to add more weekly schedule"].index[0]
            data = data[:index_to_drop_from]

            df_rotated = data.T
            df_rotated.columns = df_rotated.iloc[0]
            df_rotated = df_rotated[1:]
            df_rotated.reset_index(drop=True, inplace=True)
            df_rotated = df_rotated.iloc[:, 2:-2]
            df_rotated = df_rotated.apply(pd.to_numeric)
            hour_column = 'Hour'
            if hour_column not in df_rotated.columns:
                raise ValueError(f"'{hour_column}' column not found in the DataFrame")

            value_columns = df_rotated.columns[df_rotated.columns.get_loc(hour_column) + 1:]

            # Prepare to combine all images into one document
            image_buffers = []

            # Display charts and collect images
            for value_column in value_columns:
                fig_chart = plot_chart(df_rotated, hour_column, value_column)
                buffer = save_chart_as_image(fig_chart, f"bar_chart_{value_column}.png")
                image_buffers.append(buffer)
                # st.pyplot(fig_chart)
                # plt.close(fig_chart)

            # Combine all images into one document
            combined_buffer = combine_images_as_document(image_buffers)

            # Display download button
            if combined_buffer is not None:
                st.markdown(get_image_download_link(combined_buffer, "combined_document.png"), unsafe_allow_html=True)
            else:
                st.error("Failed to combine images.")
                
    except Exception as e:
        st.write()

if __name__ == "__main__":
    uploaded_file = st.file_uploader("Upload EXCEL file", type=["xlsx"])
    get_schedule(uploaded_file)
    analytics(uploaded_file)
    analytics1(uploaded_file)
