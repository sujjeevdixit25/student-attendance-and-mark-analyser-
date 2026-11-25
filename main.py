"""Start the student attendance and performance report."""

from attendance import load_attendance, summarize_attendance
from performance import load_marks, summarize_performance
from proxycatcher import find_attendance_anomalies, conflicting_attendance_keys
from student_records import load_students


# Change these two numbers if your instructor wants different thresholds.
MINIMUM_ATTENDANCE_PERCENT = 75
WEAK_SUBJECT_PERCENT = 60


def display_percent(percent):
    """Turn a number into a percentage for the report."""
    if percent is None:
        return "Unavailable"
    return "{:.1f}%".format(percent)


def make_report(students, attendance_rows, marks_rows):
    """Build the report using the other four project modules."""
    flags = find_attendance_anomalies(attendance_rows)
    conflict_keys = conflicting_attendance_keys(flags)
    attendance_summary = summarize_attendance(
        attendance_rows,
        MINIMUM_ATTENDANCE_PERCENT,
        conflict_keys,
    )
    subject_summary, overall_summary = summarize_performance(
        marks_rows,
        WEAK_SUBJECT_PERCENT,
    )

    lines = []
    lines.append("SMART STUDENT PERFORMANCE & ATTENDANCE ANALYZER")
    lines.append("Decision-support report: indicators need faculty review.")
    lines.append("")

    if len(students) == 0:
        lines.append("No valid student records were loaded.")

    for student_id in sorted(students.keys()):
        student = students[student_id]
        lines.append(student["name"] + " (" + student_id + ") - Section " + student["section"])

        found_attendance = False
        for key in sorted(attendance_summary.keys()):
            if key[0] == student_id:
                found_attendance = True
                result = attendance_summary[key]
                status = "OK"
                if result["shortage"]:
                    status = "SHORTAGE ALERT"
                line = "  Attendance / " + key[1] + ": " + display_percent(result["percent"])
                line = line + " (" + str(result["attended"]) + "/" + str(result["held"]) + " sessions) - " + status
                lines.append(line)

        if not found_attendance:
            lines.append("  Attendance: no clear session records available.")

        found_marks = False
        for key in sorted(subject_summary.keys()):
            if key[0] == student_id:
                found_marks = True
                result = subject_summary[key]
                line = "  Marks / " + key[1] + ": " + str(result["marks"]) + "/" + str(result["maximum_marks"])
                line = line + " (" + display_percent(result["percent"]) + ")"
                if result["weak"]:
                    line = line + " - SUPPORT INDICATOR"
                lines.append(line)

        if not found_marks:
            lines.append("  Performance: no valid marks available.")

        if student_id in overall_summary:
            result = overall_summary[student_id]
            lines.append("  Overall marks: " + display_percent(result["percent"]))
        else:
            lines.append("  Overall marks: Unavailable")

        lines.append("")

    lines.append("PROXYCATCHER REVIEW FLAGS")
    if len(flags) == 0:
        lines.append("  No duplicate session keys found.")
    else:
        for flag in flags:
            row_numbers = []
            for row_number in flag["row_numbers"]:
                row_numbers.append(str(row_number))
            rows_text = ", ".join(row_numbers)
            line = "  " + flag["student_id"] + " / " + flag["subject"] + " / session " + flag["session_id"]
            line = line + ": " + flag["reason"]
            line = line + " [attendance.csv rows " + rows_text + "]"
            lines.append(line)

    lines.append("")
    lines.append("A flag is a reason to check the source record, not proof of proxy attendance or misconduct.")
    lines.append("Conflicting sessions are left out of attendance percentages until reviewed.")

    report = "\n".join(lines)
    return report


def run():
    """Load the sample CSV files, check the data, and print a report."""
    students, student_errors = load_students("data/students.csv")
    attendance_rows, attendance_errors = load_attendance("data/attendance.csv", students)
    marks_rows, marks_errors = load_marks("data/marks.csv", students)

    report = make_report(
        students,
        attendance_rows,
        marks_rows,
    )

    print(report)

    errors = student_errors + attendance_errors + marks_errors
    if len(errors) > 0:
        print("\nDATA CHECK MESSAGES")
        for error in errors:
            print("  - " + error)

    return report, errors


if __name__ == "__main__":
    run()
