# Student Performance and Attendance Analyzer

This is a basic Python project for keeping track of student attendance and marks. It reads the information from CSV files and prints a report in the terminal.

## What it does

- Shows attendance percentages and alerts when attendance is below 75%.
- Shows marks by subject and an overall percentage.
- Marks subjects below 60% for extra support.
- Points out repeated attendance records so a teacher can check them.

The repeated-record warning does not prove that anyone had proxy attendance. A teacher needs to check the records.

## Run the project

1. Install Python and open this folder in VS Code.
2. In VS Code, choose **Terminal → New Terminal**.
3. Type:

   ```text
   python main.py
   ```

   If that does not work on Windows, try `py main.py`.

The project uses Python's built-in features, so no extra packages are needed.

## Change the sample data

The CSV files are in the `data` folder:

- `students.csv` has student IDs, names, and sections.
- `attendance.csv` has student IDs, subjects, session IDs, and Present/Absent status.
- `marks.csv` has student IDs, subjects, marks, and maximum marks.

Keep the column headings in the files when adding records.
