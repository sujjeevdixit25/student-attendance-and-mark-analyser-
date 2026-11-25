"""Check marks records and calculate simple performance summaries."""

from student_records import read_csv


def load_marks(filename, students):
    """Load marks rows with numbers inside the allowed range."""
    rows, errors = read_csv(filename, ["student_id", "subject", "marks", "maximum_marks"])
    marks_rows = []

    for row in rows:
        student_id = row["student_id"].strip()
        subject = row["subject"].strip()
        row_number = row["row_number"]

        try:
            marks = float(row["marks"])
            maximum_marks = float(row["maximum_marks"])
        except ValueError:
            errors.append(filename + " row " + str(row_number) + " marks must be numbers")
            continue

        if student_id == "" or subject == "":
            errors.append(filename + " row " + str(row_number) + " is missing a required value")
        elif student_id not in students:
            errors.append(filename + " row " + str(row_number) + " has an unknown student ID")
        elif maximum_marks <= 0 or not (0 <= marks <= maximum_marks):
            errors.append(filename + " row " + str(row_number) + " marks must be from 0 to maximum_marks")
        else:
            marks_rows.append({
                "student_id": student_id,
                "subject": subject,
                "marks": marks,
                "maximum_marks": maximum_marks,
            })

    return marks_rows, errors


def summarize_performance(rows, weak_threshold=60):
    """Calculate subject percentages and each student's overall percentage."""
    subject_totals = {}
    overall_totals = {}

    for row in rows:
        student_id = row["student_id"]
        subject = row["subject"]
        subject_key = (student_id, subject)

        if subject_key not in subject_totals:
            subject_totals[subject_key] = [0, 0]

        if student_id not in overall_totals:
            overall_totals[student_id] = [0, 0]

        subject_totals[subject_key][0] = subject_totals[subject_key][0] + row["marks"]
        subject_totals[subject_key][1] = subject_totals[subject_key][1] + row["maximum_marks"]
        overall_totals[student_id][0] = overall_totals[student_id][0] + row["marks"]
        overall_totals[student_id][1] = overall_totals[student_id][1] + row["maximum_marks"]

    subject_summaries = {}

    for subject_key in subject_totals:
        marks = subject_totals[subject_key][0]
        maximum_marks = subject_totals[subject_key][1]
        percent = marks / maximum_marks * 100

        weak = False
        if percent < weak_threshold:
            weak = True

        subject_summaries[subject_key] = {
            "marks": marks,
            "maximum_marks": maximum_marks,
            "percent": percent,
            "weak": weak,
        }

    overall_summaries = {}

    for student_id in overall_totals:
        marks = overall_totals[student_id][0]
        maximum_marks = overall_totals[student_id][1]
        overall_summaries[student_id] = {
            "marks": marks,
            "maximum_marks": maximum_marks,
            "percent": marks / maximum_marks * 100,
        }

    return subject_summaries, overall_summaries
