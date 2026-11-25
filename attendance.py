"""Check attendance records and calculate attendance percentages."""

from student_records import read_csv


def load_attendance(filename, students):
    """Load valid attendance rows from a CSV file."""
    rows, errors = read_csv(filename, ["student_id", "subject", "session_id", "status"])
    attendance = []

    for row in rows:
        student_id = row["student_id"].strip()
        subject = row["subject"].strip()
        session_id = row["session_id"].strip()
        status = row["status"].strip().lower()
        row_number = row["row_number"]

        if student_id == "" or subject == "" or session_id == "":
            errors.append(filename + " row " + str(row_number) + " is missing a required value")
        elif student_id not in students:
            errors.append(filename + " row " + str(row_number) + " has an unknown student ID")
        elif status != "present" and status != "absent":
            errors.append(filename + " row " + str(row_number) + " status must be Present or Absent")
        else:
            attendance.append({
                "student_id": student_id,
                "subject": subject,
                "session_id": session_id,
                "status": status,
                "row_number": row_number,
            })

    return attendance, errors


def summarize_attendance(rows, minimum_percent=75, excluded_keys=None):
    """Count attended and held sessions and calculate the percentage."""
    if excluded_keys is None:
        excluded_keys = []

    totals = {}
    used_sessions = []

    for row in rows:
        session_key = (row["student_id"], row["subject"], row["session_id"])
        student_subject = (row["student_id"], row["subject"])

        if session_key in excluded_keys or session_key in used_sessions:
            continue

        used_sessions.append(session_key)

        if student_subject not in totals:
            totals[student_subject] = [0, 0]

        totals[student_subject][1] = totals[student_subject][1] + 1
        if row["status"] == "present":
            totals[student_subject][0] = totals[student_subject][0] + 1

    summaries = {}

    for student_subject in totals:
        attended = totals[student_subject][0]
        held = totals[student_subject][1]

        if held == 0:
            percent = None
        else:
            percent = attended / held * 100

        shortage = False
        if percent is not None and percent < minimum_percent:
            shortage = True

        summaries[student_subject] = {
            "attended": attended,
            "held": held,
            "percent": percent,
            "shortage": shortage,
        }

    return summaries
