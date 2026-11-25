"""Beginner-friendly standard-library tests for the analyzer's core rules."""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from attendance import load_attendance, summarize_attendance
from performance import load_marks, summarize_performance
from proxycatcher import find_attendance_anomalies, conflicting_attendance_keys
from student_records import load_students


class AnalyzerTests(unittest.TestCase):
    def test_attendance_percent_and_shortage(self):
        rows = [
            {"student_id": "S1", "subject": "Math", "session_id": "M1", "status": "present"},
            {"student_id": "S1", "subject": "Math", "session_id": "M2", "status": "absent"},
        ]
        result = summarize_attendance(rows, minimum_percent=75)[("S1", "Math")]
        self.assertEqual(result["percent"], 50)
        self.assertTrue(result["shortage"])

    def test_duplicate_and_conflicting_rows_include_source_references(self):
        rows = [
            {"student_id": "S1", "subject": "Math", "session_id": "M1", "status": "present", "row_number": 2},
            {"student_id": "S1", "subject": "Math", "session_id": "M1", "status": "absent", "row_number": 3},
        ]
        flags = find_attendance_anomalies(rows)
        self.assertEqual(flags[0]["row_numbers"], [2, 3])
        self.assertIn("statuses conflict", flags[0]["reason"])
        self.assertEqual(len(conflicting_attendance_keys(flags)), 1)
        summary = summarize_attendance(rows, excluded_keys=conflicting_attendance_keys(flags))
        self.assertEqual(summary, {})

    def test_zero_sessions_is_unavailable_without_division_error(self):
        self.assertEqual(summarize_attendance([]), {})

    def test_invalid_attendance_row_is_reported_and_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attendance.csv"
            path.write_text("student_id,subject,session_id,status\nS1,Math,,Present\n", encoding="utf-8")
            rows, errors = load_attendance(path, {"S1": {"student_id": "S1"}})
        self.assertEqual(rows, [])
        self.assertTrue(any("missing a required value" in error for error in errors))

    def test_invalid_attendance_status_is_reported_and_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attendance.csv"
            path.write_text("student_id,subject,session_id,status\nS1,Math,M1,Unknown\n", encoding="utf-8")
            rows, errors = load_attendance(path, {"S1": {"student_id": "S1"}})
        self.assertEqual(rows, [])
        self.assertTrue(any("Present or Absent" in error for error in errors))

    def test_marks_summaries_and_weak_subject(self):
        rows = [
            {"student_id": "S1", "subject": "Math", "marks": 50, "maximum_marks": 100},
            {"student_id": "S1", "subject": "Python", "marks": 80, "maximum_marks": 100},
        ]
        subjects, overall = summarize_performance(rows)
        self.assertTrue(subjects[("S1", "Math")]["weak"])
        self.assertEqual(overall["S1"]["percent"], 65)

    def test_bad_or_zero_mark_maximum_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "marks.csv"
            path.write_text("student_id,subject,marks,maximum_marks\nS1,Math,10,0\n", encoding="utf-8")
            rows, errors = load_marks(path, {"S1": {"student_id": "S1"}})
        self.assertEqual(rows, [])
        self.assertTrue(any("maximum_marks" in error for error in errors))

    def test_nan_marks_are_outside_the_allowed_range(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "marks.csv"
            path.write_text("student_id,subject,marks,maximum_marks\nS1,Math,nan,100\n", encoding="utf-8")
            rows, errors = load_marks(path, {"S1": {"student_id": "S1"}})
        self.assertEqual(rows, [])
        self.assertTrue(any("maximum_marks" in error for error in errors))

    def test_duplicate_student_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "students.csv"
            path.write_text("student_id,name,section\nS1,A,C\nS1,B,C\n", encoding="utf-8")
            students, errors = load_students(path)
        self.assertEqual(students["S1"]["name"], "A")
        self.assertTrue(any("duplicate student_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
