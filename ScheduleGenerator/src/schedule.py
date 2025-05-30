import pandas as pd
import streamlit as st
from io import StringIO

# Function to replace consecutive duplicates with &D
def replace_consecutive_duplicates(values):
    result = []
    previous_value = None
    for value in values:
        if value == previous_value:
            result.append('&D')
        else:
            result.append(value)
        previous_value = value
    return result

# Helper function to format lines with a maximum width and indentation
def format_line(text, max_width=80, indent=0):
    lines = []
    while len(text) > max_width:
        split_point = text.rfind(',', 0, max_width)
        if split_point == -1:
            split_point = text.rfind(' ', 0, max_width)
            if split_point == -1:
                split_point = max_width
        lines.append(text[:split_point + 1])
        text = ' ' * indent + text[split_point + 1:].lstrip()
    lines.append(text)
    return '\n'.join(lines)

# Main function to generate the schedule INP file
def getScheduleINP(data):
    output_content = StringIO(newline='\r\n')  # Use CRLF for Windows line endings
    try:
        # Store index or markers to capture range of values
        idx1 = idx2 = idx3 = idx4 = None

        for index, row in data.iterrows():
            if row[0] == 'Hour':
                idx1 = index
            elif row[0] == 'Day' and idx1 is not None and idx2 is None:
                idx2 = index
            elif row[0] == 'Month' and idx2 is not None and idx3 is None:
                idx3 = index + 1
            elif row[0] == 'Annual Schedule' and idx1 is not None and idx2 is not None and idx3 is None:
                idx4 = index - 1

            if idx1 is not None and idx2 is not None and idx3 is not None:
                break

        # Creating a new section called Day schedules
        output_content.write("$ ---------------------------------------------------------\n")
        output_content.write("$              Day Schedules\n")
        output_content.write("$ ---------------------------------------------------------\n\n")

        # Extracting the 'Hour' row values from 2nd to 25th column
        hour_values = data.loc[data.iloc[:, 0] == 'Hour'].iloc[0, 1:25].tolist()
        formatted_hour_values = ', '.join(map(str, hour_values))
        type_value = data.iloc[0, 1].upper()

        for index, row in data.iterrows():
            if row[0] == 'Week Schedule' or row[0] == 'Rows can be added to add more weekly schedule':
                break
            if index > idx1:
                schedule_name = row[0]
                row_values = row[1:25].tolist()
                row_values = replace_consecutive_duplicates(row_values)
                formatted_values = ', '.join(str(value) for value in row_values if pd.notnull(value))

                output_content.write(format_line(f'"{schedule_name}" = DAY-SCHEDULE-PD\n'))
                output_content.write(format_line(f"   TYPE             = {type_value}\n"))
                output_content.write(format_line(f"   VALUES           = ( {formatted_values} )\n"))
                output_content.write(format_line("   ..\n"))
                output_content.write(format_line(""))

        # Creating a new section called week schedules after completion of Day Schedule
        output_content.write("\n$ ---------------------------------------------------------\n")
        output_content.write("$              Week Schedules\n")
        output_content.write("$ ---------------------------------------------------------\n\n")

        day_values = data.loc[data.iloc[:, 0] == 'Day'].iloc[0, 1:11].tolist()
        formatted_day_values = ', '.join(map(str, day_values))

        for index, row in data.iterrows():
            if row[0] == 'Annual Schedule':
                break
            if index > idx2 and index < idx4:
                schedule_name = row[0]
                row_values = row[1:11].tolist()
                row_values = replace_consecutive_duplicates(row_values)
                formatted_day = ', '.join(f'"{value}"' if value != '&D' else value for value in row_values if pd.notnull(value))
                output_content.write(format_line(f'"{schedule_name}" = WEEK-SCHEDULE-PD\n'))
                output_content.write(format_line(f"   TYPE             = {type_value}\n"))
                output_content.write(format_line(f"   DAY-SCHEDULES    = ( {formatted_day} )\n"))
                output_content.write(format_line("   ..\n"))
                output_content.write(format_line(""))

        # Creating a new section called Annual schedules after completion of Week Schedule
        output_content.write("\n$ ---------------------------------------------------------\n")
        output_content.write("$              Annual Schedules\n")
        output_content.write("$ ---------------------------------------------------------\n\n")

        month_indexes = data.index[data.iloc[:, 0] == 'Month'].tolist()

        for i, month_row_index in enumerate(month_indexes):
            month_values = data.iloc[month_row_index, 1:25].tolist()
            formatted_values1 = ', '.join([str(x) for x in month_values if pd.notnull(x) and x != 'Columns can be added here till 8760'])

            day_row_index = month_row_index + 1
            day_values = data.iloc[day_row_index, 1:25].tolist()
            formatted_values2 = ', '.join(map(str, filter(pd.notnull, day_values)))

            if day_row_index + 1 < len(data):
                for schedule_row_index in range(day_row_index + 1, len(data)):
                    schedule_name = data.iloc[schedule_row_index, 0]

                    if isinstance(schedule_name, str) and schedule_name.lower() in ["month", "day"]:
                        break

                    row_values = data.iloc[schedule_row_index, 1:25].tolist()
                    formatted_days = ', '.join(f'"{value}"' for value in row_values if pd.notnull(value))

                    output_content.write(format_line(f'"{schedule_name}" = SCHEDULE-PD\n'))
                    output_content.write(format_line(f"   TYPE             = {type_value}\n"))
                    output_content.write(format_line(f"   MONTH            = ( {formatted_values1} )\n"))
                    output_content.write(format_line(f"   DAY              = ( {formatted_values2} )\n"))
                    output_content.write(format_line(f"   WEEK-SCHEDULES   = ( {formatted_days} )\n"))
                    output_content.write(format_line("   ..\n"))
                    output_content.write(format_line(""))

        # Prepare the download button in Streamlit
        st.success("INP Generated Successfully")
        st.download_button(
            label="Download New INP File",
            data=output_content.getvalue(),
            file_name="Schedule.inp",
            mime="text/plain",
        )

    except Exception as e:
        st.error(f"An error occurred while creating the new file: {e}")



# import os
# import pandas as pd
# import streamlit as st
# import io

# # Function to replace consecutive duplicates with &D
# def replace_consecutive_duplicates(values):
#     result = []
#     previous_value = None
#     for value in values:
#         if value == previous_value:
#             result.append('&D')
#         else:
#             result.append(value)
#         previous_value = value
#     return result

# #  Helper function to format lines with a maximum width and indentation
# def format_line(text, max_width=80, indent=0):
#     lines = []
#     while len(text) > max_width:
#         split_point = text.rfind(',', 0, max_width)
#         if split_point == -1:
#             split_point = text.rfind(' ', 0, max_width)
#             if split_point == -1:
#                 split_point = max_width
#         lines.append(text[:split_point + 1])
#         text = ' ' * indent + text[split_point + 1:].lstrip()
#     lines.append(text)
#     return '\n'.join(lines)

# def getScheduleINP(data):
#     file_name = f"Schedule.inp"
    
#     # Use StringIO to create an in-memory text stream
#     output = io.StringIO()

#     # Write to the in-memory file with Windows line endings
#     def write_line(line):
#         output.write(line + '\r\n')
    
#     idx1, idx2, idx3, idx4 = None, None, None, None
#     for index, row in data.iterrows():
#         if row[0] == 'Hour':
#             idx1 = index
#         elif row[0] == 'Day' and idx1 is not None and idx2 is None:
#             idx2 = index
#         elif row[0] == 'Month' and idx2 is not None and idx3 is None:
#             idx3 = index + 1  # Adjust index as needed
#         elif row[0] == 'Annual Schedule' and idx1 is not None and idx2 is not None and idx3 is None:
#             idx4 = index - 1  # Adjust index as needed
        
#         if idx1 is not None and idx2 is not None and idx3 is not None:
#             break

#     # write_line("INPUT ..")
#     # write_line("")
#     # write_line("$ ---------------------------------------------------------")
#     # write_line("$              Abort, Diagnostics")
#     # write_line("$ ---------------------------------------------------------")

#     # Creating a new section called Day schedules
#     # write_line("")
#     write_line("$ ---------------------------------------------------------")
#     write_line("$              Day Schedules")
#     write_line("$ ---------------------------------------------------------")
#     write_line("")

#     # Extracting the 'Hour' row values from 2nd to 25th column
#     hour_values = data.loc[data.iloc[:, 0] == 'Hour'].iloc[0, 1:25].tolist()
#     formatted_hour_values = ', '.join(map(str, hour_values))
#     type_value = data.iloc[0, 1].upper()

#     # Iterate through the rows of the data
#     for index, row in data.iterrows():
#         if row[0] == 'Week Schedule' or row[0] == 'Rows can be added to add more weekly schedule':
#             break
#         if index > idx1:
#             schedule_name = row[0]
#             # Extract values from 2nd to 25th column for the current row
#             row_values = row[1:25].tolist()
#             # Replace consecutive duplicates with &D
#             row_values = replace_consecutive_duplicates(row_values)
#             formatted_values = ', '.join(str(value) for value in row_values if pd.notnull(value))
#             # Write to the file
#             write_line(format_line(f'"{schedule_name}" = DAY-SCHEDULE-PD'))
#             write_line(format_line(f"   TYPE             = {type_value}"))
#             write_line(format_line(f"   VALUES           = ( {formatted_values} )"))
#             write_line(format_line("   .."))
#             # write_line("")

#     # Creating a new section called week schedules after completion of Day Schedule
#     write_line("")
#     write_line("$ ---------------------------------------------------------")
#     write_line("$              Week Schedules")
#     write_line("$ ---------------------------------------------------------")
#     write_line("")

#     # Extracting the 'Hour' row values from 2nd to 25th column
#     day_values = data.loc[data.iloc[:, 0] == 'Day'].iloc[0, 1:11].tolist()
#     formatted_day_values = ', '.join(map(str, day_values))
    
#     for index, row in data.iterrows():
#         if row[0] == 'Annual Schedule': # need to ask this
#             break
#         if index > idx2 and index < idx4:
#             schedule_name = row[0]
#             # Extract values from 2nd to 11th column for the current row
#             row_values = row[1:11].tolist()
#             row_values = replace_consecutive_duplicates(row_values)
#             formatted_day = ', '.join(f'"{value}"' if value != '&D' else value for value in row_values if pd.notnull(value))

#             write_line(format_line(f'"{schedule_name}" = WEEK-SCHEDULE-PD'))
#             write_line(format_line(f"   TYPE             = {type_value}"))
#             write_line(format_line(f"   DAY-SCHEDULES    = ( {formatted_day} )"))
#             write_line(format_line("   .."))
#             # write_line("")

#     # Creating a new section called Annual schedules after completion of Week Schedule
#     write_line("")
#     write_line("$ ---------------------------------------------------------")
#     write_line("$              Annual Schedules")
#     write_line("$ ---------------------------------------------------------")
#     write_line("")

#     # Find all the indexes of 'Month' and 'Day' rows
#     month_indexes = data.index[data.iloc[:, 0] == 'Month'].tolist()
    
#     for i, month_row_index in enumerate(month_indexes):
#         # Extract values for formatted_values1 from 'Month' row
#         month_values = data.iloc[month_row_index, 1:13].tolist()
#         formatted_values1 = ', '.join([str(x) for x in month_values if pd.notnull(x) and x != 'Columns can be added here till 8760'])

#         # Extract values for formatted_values2 from 'Day' row
#         day_row_index = month_row_index + 1
#         day_values = data.iloc[day_row_index, 1:13].tolist()
#         formatted_values2 = ', '.join(map(str, filter(pd.notnull, day_values)))

#         # Extract schedule values for each schedule block
#         if day_row_index + 1 < len(data):
#             for schedule_row_index in range(day_row_index + 1, len(data)):
#                 schedule_name = data.iloc[schedule_row_index, 0]
                
#                 if schedule_name.lower() in ["month", "day"]:
#                     break
                
#                 row_values = data.iloc[schedule_row_index, 1:13].tolist()
#                 formatted_days = ', '.join(f'"{value}"' for value in row_values if pd.notnull(value))
                
#                 write_line(format_line(f'"{schedule_name}" = SCHEDULE-PD'))
#                 write_line(format_line(f"   TYPE             = {type_value}"))
#                 write_line(format_line(f"   MONTH            = ( {formatted_values1} )"))
#                 write_line(format_line(f"   DAY              = ( {formatted_values2} )"))
#                 write_line(format_line(f"   WEEK-SCHEDULES   = ( {formatted_days} )"))
#                 write_line(format_line("   .."))
#                 # write_line(format_line(""))
    
#     # write_line("")
#     # write_line("")
#     # write_line("$ ---------------------------------------------------------")
#     # write_line("$              THE END")
#     # write_line("$ ---------------------------------------------------------")
#     # write_line("")
#     # write_line("END ..")
#     # write_line("COMPUTE ..")
#     # write_line("STOP ..")

#     # Get the content of the in-memory text stream
#     inp_content = output.getvalue()
    
#     # Close the StringIO object
#     output.close()

#     st.success("INP Generated Successfully!")
#     st.download_button(
#         label="Download INP File",
#         data=inp_content,
#         file_name=file_name,
#         mime="text/plain"
#     )
