# Planora - Daily Scheduler Application

Planora is a smart daily scheduler application that helps you balance your fixed daily commitments (like study hours) with variable tasks (like classes and submission deadlines).

## Features

- Input fixed daily tasks (e.g., 6 hours of study, 2 hours of practice)
- Add variable tasks with specific dates and times (e.g., classes, submission deadlines)
- Set preferences for day start/end times and meal breaks
- Generate optimized daily schedules that balance all your commitments

## Setup Instructions

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

1. **Step 1**: Enter your fixed daily tasks (tasks you need to do for a fixed amount of time every day)
2. **Step 2**: Add variable tasks with specific dates/times (like classes or submission deadlines)
3. **Step 3**: Set your preferences for day boundaries and meal breaks
4. **Result**: View your optimized daily schedule