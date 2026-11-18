# Smart CBT Examination System

A beginner-friendly Computer-Based Testing project built using Python.

## Features
- MCQ examination panel
- Countdown timer
- Automatic result calculation
- Results saved in SQLite database
- Performance charts
- Basic rule-based performance estimate
- Download results as CSV

## Requirements
- Python 3.10 or newer
- Internet connection for the first package installation

## Run on Windows

1. Extract this folder.
2. Open PowerShell in this folder.
3. (Recommended) Create a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the project:

   ```powershell
   python -m streamlit run app.py
   ```

You can also double-click `run_project.bat` after installing the requirements.

## Notes
- The first version contains sample Python and SQL questions.
- Change `EXAM_DURATION` near the top of `app.py` to change the exam time.
- Results are stored in `cbt_results.db`, which is created automatically.
- The prediction is a simple educational estimate based on recent scores. It is not a trained AI model.
