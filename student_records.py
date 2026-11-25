"""Read student information from a CSV file."""

import csv


def read_csv(filename, required_columns):
    """Read rows from a CSV file and check that it has the needed columns."""
    rows = []
    errors = []

    try:
        file = open(filename, "r", encoding="utf-8-sig", newline="")
    except OSError:
        return rows, ["Could not open " + filename]

    with file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            return rows, [filename + " is missing its header row"]

        for column in required_columns:
            if column not in reader.fieldnames:
                errors.append(filename + " is missing the column " + column)

        if errors:
            return rows, errors

        row_number = 1
        for row in reader:
            row_number += 1

            if None in row:
                errors.append(filename + " row " + str(row_number) + " has too many values")
                continue

            missing_value = False
            for column in required_columns:
                if row.get(column) is None:
                    missing_value = True

            if missing_value:
                errors.append(filename + " row " + str(row_number) + " is incomplete")
                continue

            row["row_number"] = row_number
            rows.append(row)

    return rows, errors


def load_students(filename):
    """Load student profiles and skip rows with missing or repeated IDs."""
    rows, errors = read_csv(filename, ["student_id", "name", "section"])
    students = {}

    for row in rows:
        student_id = row["student_id"].strip()
        name = row["name"].strip()
        section = row["section"].strip()
        row_number = row["row_number"]

        if student_id == "" or name == "" or section == "":
            errors.append(filename + " row " + str(row_number) + " has a blank student field")
        elif student_id in students:
            errors.append(filename + " row " + str(row_number) + " repeats student ID " + student_id)
        else:
            students[student_id] = {"name": name, "section": section}

    return students, errors
