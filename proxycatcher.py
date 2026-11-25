"""Find repeated attendance session records for faculty review."""


def find_attendance_anomalies(rows):
    """Return duplicate session keys, their reasons, and CSV row numbers."""
    flags = []
    checked_keys = []

    for row in rows:
        key = (row["student_id"], row["subject"], row["session_id"])

        if key in checked_keys:
            continue

        matching_rows = []
        for other_row in rows:
            other_key = (other_row["student_id"], other_row["subject"], other_row["session_id"])
            if key == other_key:
                matching_rows.append(other_row)

        checked_keys.append(key)

        if len(matching_rows) > 1:
            row_numbers = []
            first_status = matching_rows[0]["status"]
            conflict = False

            for matching_row in matching_rows:
                row_numbers.append(matching_row["row_number"])
                if matching_row["status"] != first_status:
                    conflict = True

            reason = "duplicate session entry appears " + str(len(matching_rows)) + " times"
            if conflict:
                reason = reason + "; attendance statuses conflict"

            flags.append({
                "student_id": key[0],
                "subject": key[1],
                "session_id": key[2],
                "row_numbers": row_numbers,
                "reason": reason,
                "conflict": conflict,
            })

    return flags


def conflicting_attendance_keys(flags):
    """Return duplicate keys with conflicting statuses."""
    keys = []

    for flag in flags:
        if flag["conflict"]:
            key = (flag["student_id"], flag["subject"], flag["session_id"])
            keys.append(key)

    return keys
