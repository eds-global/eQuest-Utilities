def perging_data_const(data):
    start_marker = "Materials / Layers / Constructions"
    end_marker = "Glass Types"
    delete_marker = "= CONSTRUCTION"

    # Finding start and end indices for the first range
    start_index = None
    end_index = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i + 3
        if end_marker in line:
            end_index = i - 3
            break

    # Storing values occurring before delete_marker within the first range
    values_before_delete_marker = []
    if start_index is not None and end_index is not None:
        for i in range(start_index, end_index):
            if delete_marker in data[i]:
                # Find the value before "="
                value = data[i].split("=")[0].strip()
                if value != "":
                    values_before_delete_marker.append(value)

    # Finding start and end indices for the second range
    start_marker1 = "TITLE"
    end_marker1 = "THE END"

    start_index1 = None
    end_index1 = None

    for i, line in enumerate(data):
        if start_marker1 in line:
            start_index1 = i + 1
        if end_marker1 in line:
            end_index1 = i - 1
            break

    # Iterate through values and delete content if value occurs only once in the second range
    if start_index1 is not None and end_index1 is not None:
        for value in set(values_before_delete_marker):
            # Count occurrences of the value before delete_marker
            count = 0
            for i in range(start_index1, end_index1+1):
                if i < len(data) and value in data[i]:  # Check index range
                    count += 1
                    if count > 1:
                        break
            if count == 1:
                for i in range(start_index, end_index):
                    if delete_marker in data[i] and data[i].split("=")[0].strip() == value:
                        # Find the next line containing ".."
                        next_line_index = i
                        while next_line_index < len(data) and ".." not in data[next_line_index]:  # Check index range
                            next_line_index += 1

                        # Delete lines from current line to next line containing ".."
                        del data[i:next_line_index+1]
    return data


def perging_data_layer(data):
    start_marker = "Materials / Layers / Constructions"
    end_marker = "Glass Types"
    delete_marker = "= LAYERS"

    # Finding start and end indices for the first range
    start_index = None
    end_index = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i + 3
        if end_marker in line:
            end_index = i - 3
            break

    # Storing values occurring before delete_marker within the first range
    values_before_delete_marker = []
    if start_index is not None and end_index is not None:
        for i in range(start_index, end_index):
            if delete_marker in data[i]:
                # Find the value before "="
                value = data[i].split("=")[0].strip()
                if value != "":
                    values_before_delete_marker.append(value)

    # Finding start and end indices for the second range
    start_marker1 = "TITLE"
    end_marker1 = "THE END"

    start_index1 = None
    end_index1 = None

    for i, line in enumerate(data):
        if start_marker1 in line:
            start_index1 = i + 1
        if end_marker1 in line:
            end_index1 = i - 1
            break

    # Iterate through values and delete content if value occurs only once in the second range
    if start_index1 is not None and end_index1 is not None:
        for value in set(values_before_delete_marker):
            # Count occurrences of the value before delete_marker
            count = 0
            for i in range(start_index1, end_index1+1):
                if i < len(data) and value in data[i]:  # Check index range
                    count += 1
                    if count > 1:
                        break
            if count == 1:
                for i in range(start_index, end_index):
                    if delete_marker in data[i] and data[i].split("=")[0].strip() == value:
                        # Find the next line containing ".."
                        next_line_index = i
                        while next_line_index < len(data) and ".." not in data[next_line_index]:  # Check index range
                            next_line_index += 1

                        # Delete lines from current line to next line containing ".."
                        del data[i:next_line_index+1]
    return data

def perging_data_material(data):
    start_marker = "Materials / Layers / Constructions"
    end_marker = "Glass Types"
    delete_marker = "= MATERIAL"

    # Finding start and end indices for the first range
    start_index = None
    end_index = None

    for i, line in enumerate(data):
        if start_marker in line:
            start_index = i + 3
        if end_marker in line:
            end_index = i - 3
            break

    # Storing values occurring before delete_marker within the first range
    values_before_delete_marker = []
    if start_index is not None and end_index is not None:
        for i in range(start_index, end_index):
            if delete_marker in data[i]:
                # Find the value before "="
                value = data[i].split("=")[0].strip()
                if value != "":
                    values_before_delete_marker.append(value)

    # Finding start and end indices for the second range
    start_marker1 = "TITLE"
    end_marker1 = "THE END"

    start_index1 = None
    end_index1 = None

    for i, line in enumerate(data):
        if start_marker1 in line:
            start_index1 = i + 1
        if end_marker1 in line:
            end_index1 = i - 1
            break

    # Iterate through values and delete content if value occurs only once in the second range
    if start_index1 is not None and end_index1 is not None:
        for value in set(values_before_delete_marker):
            # Count occurrences of the value before delete_marker
            count = 0
            for i in range(start_index1, end_index1+1):
                if i < len(data) and value in data[i]:  # Check index range
                    count += 1
                    if count > 1:
                        break
            if count == 1:
                for i in range(start_index, end_index):
                    if delete_marker in data[i] and data[i].split("=")[0].strip() == value:
                        # Find the next line containing ".."
                        next_line_index = i
                        while next_line_index < len(data) and ".." not in data[next_line_index]:  # Check index range
                            next_line_index += 1

                        # Delete lines from current line to next line containing ".."
                        del data[i:next_line_index+1]
    return data