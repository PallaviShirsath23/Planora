from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.secret_key = "planora_secret_key"

# Path to store schedules
SCHEDULES_FOLDER = os.path.join(app.root_path, 'schedules')
if not os.path.exists(SCHEDULES_FOLDER):
    os.makedirs(SCHEDULES_FOLDER)

# Default schedule with breaks and meals
DEFAULT_BREAKS = {
    "breakfast": {"start": "08:00", "duration": 30},
    "lunch": {"start": "13:00", "duration": 60},
    "dinner": {"start": "19:00", "duration": 60},
    "short_breaks": [
        {"start": "10:30", "duration": 15},
        {"start": "15:30", "duration": 15},
        {"start": "17:30", "duration": 15}
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fixed-tasks', methods=['GET', 'POST'])
def fixed_tasks():
    if request.method == 'POST':
        # Process fixed tasks from form
        fixed_tasks = []
        task_names = request.form.getlist('task_name')
        task_hours = request.form.getlist('task_hours')
        
        for i in range(len(task_names)):
            if task_names[i] and task_hours[i]:
                fixed_tasks.append({
                    'name': task_names[i],
                    'hours': float(task_hours[i])
                })
        
        # Save fixed tasks to session
        with open(os.path.join(SCHEDULES_FOLDER, 'fixed_tasks.json'), 'w') as f:
            json.dump(fixed_tasks, f)
        
        return redirect(url_for('variable_tasks'))
    
    return render_template('fixed_tasks.html')

@app.route('/variable-tasks', methods=['GET', 'POST'])
def variable_tasks():
    if request.method == 'POST':
        # Process variable tasks from form
        variable_tasks = []
        task_names = request.form.getlist('task_name')
        task_dates = request.form.getlist('task_date')
        task_times = request.form.getlist('task_time')
        task_durations = request.form.getlist('task_duration')
        
        for i in range(len(task_names)):
            if task_names[i] and task_dates[i] and task_durations[i]:
                variable_tasks.append({
                    'name': task_names[i],
                    'date': task_dates[i],
                    'time': task_times[i] if task_times[i] else None,
                    'duration': float(task_durations[i])
                })
        
        # Save variable tasks
        with open(os.path.join(SCHEDULES_FOLDER, 'variable_tasks.json'), 'w') as f:
            json.dump(variable_tasks, f)
        
        return redirect(url_for('preferences'))
    
    return render_template('variable_tasks.html')

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        # Process user preferences
        preferences = {
            'day_start': request.form.get('day_start', '07:00'),
            'day_end': request.form.get('day_end', '22:00'),
            'breaks': {
                'breakfast': {
                    'start': request.form.get('breakfast_time', '08:00'),
                    'duration': int(request.form.get('breakfast_duration', 30))
                },
                'lunch': {
                    'start': request.form.get('lunch_time', '13:00'),
                    'duration': int(request.form.get('lunch_duration', 60))
                },
                'dinner': {
                    'start': request.form.get('dinner_time', '19:00'),
                    'duration': int(request.form.get('dinner_duration', 60))
                }
            }
        }
        
        # Save preferences
        with open(os.path.join(SCHEDULES_FOLDER, 'preferences.json'), 'w') as f:
            json.dump(preferences, f)
        
        return redirect(url_for('generate_schedule'))
    
    return render_template('preferences.html')

@app.route('/generate-schedule')
def generate_schedule():
    # Load all saved data
    try:
        with open(os.path.join(SCHEDULES_FOLDER, 'fixed_tasks.json'), 'r') as f:
            fixed_tasks = json.load(f)
        
        with open(os.path.join(SCHEDULES_FOLDER, 'variable_tasks.json'), 'r') as f:
            variable_tasks = json.load(f)
        
        with open(os.path.join(SCHEDULES_FOLDER, 'preferences.json'), 'r') as f:
            preferences = json.load(f)
    except FileNotFoundError:
        flash("Missing data. Please complete all previous steps.")
        return redirect(url_for('index'))
    
    # Generate schedule logic
    schedule = generate_optimized_schedule(fixed_tasks, variable_tasks, preferences)
    
    return render_template('schedule.html', schedule=schedule)

def generate_optimized_schedule(fixed_tasks, variable_tasks, preferences):
    """
    Algorithm to generate an optimized schedule based on:
    - Fixed tasks (e.g., 6 hours of study daily)
    - Variable tasks (e.g., classes, submissions with specific times)
    - User preferences (day start/end times, meal times)
    
    Returns a dictionary with dates as keys and daily schedules as values
    """
    schedule = {}
    
    # Get date range from variable tasks
    dates = set()
    for task in variable_tasks:
        dates.add(task['date'])
    
    # Add today if no dates
    if not dates:
        today = datetime.now().strftime('%Y-%m-%d')
        dates.add(today)
    
    # Sort dates
    dates = sorted(list(dates))
    
    # Process each date
    for date_str in dates:
        # Parse user preferences
        day_start = datetime.strptime(preferences['day_start'], '%H:%M').time()
        day_end = datetime.strptime(preferences['day_end'], '%H:%M').time()
        
        # Initialize time blocks for the day
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_start_dt = datetime.combine(date_obj, day_start)
        day_end_dt = datetime.combine(date_obj, day_end)
        
        # Set up breaks and meals
        break_times = []
        
        # Add meals
        for meal, details in preferences['breaks'].items():
            meal_time = datetime.strptime(details['start'], '%H:%M').time()
            meal_dt = datetime.combine(date_obj, meal_time)
            break_times.append({
                'start': meal_dt,
                'end': meal_dt + timedelta(minutes=details['duration']),
                'name': meal.capitalize()
            })
        
        # TODO: Add short breaks every 2 hours
        
        # Get variable tasks for this date
        day_variable_tasks = []
        for task in variable_tasks:
            if task['date'] == date_str:
                task_dict = {
                    'name': task['name'],
                    'duration': task['duration'] * 60  # convert to minutes
                }
                
                if task['time']:
                    task_time = datetime.strptime(task['time'], '%H:%M').time()
                    task_dict['start'] = datetime.combine(date_obj, task_time)
                    task_dict['end'] = task_dict['start'] + timedelta(minutes=task_dict['duration'])
                    task_dict['fixed_time'] = True
                else:
                    task_dict['fixed_time'] = False
                
                day_variable_tasks.append(task_dict)
        
        # Get available time slots
        available_slots = get_available_time_slots(day_start_dt, day_end_dt, 
                                                  break_times, day_variable_tasks)
        
        # Distribute fixed tasks across available slots
        daily_schedule = schedule_fixed_tasks(fixed_tasks, available_slots, 
                                             day_variable_tasks, break_times)
        
        schedule[date_str] = daily_schedule
    
    return schedule

def get_available_time_slots(day_start, day_end, break_times, fixed_time_tasks):
    """
    Calculate available time slots after accounting for breaks and fixed-time tasks
    """
    # Sort breaks and fixed time tasks
    all_blocked_times = break_times + [t for t in fixed_time_tasks if t.get('fixed_time', False)]
    all_blocked_times.sort(key=lambda x: x['start'])
    
    # Initialize available slots with the full day
    available_slots = [{'start': day_start, 'end': day_end}]
    
    # Remove blocked times from available slots
    for blocked in all_blocked_times:
        new_available_slots = []
        for slot in available_slots:
            # If blocked time is outside current slot, keep slot unchanged
            if blocked['end'] <= slot['start'] or blocked['start'] >= slot['end']:
                new_available_slots.append(slot)
            # If blocked time splits the slot
            elif blocked['start'] > slot['start'] and blocked['end'] < slot['end']:
                new_available_slots.append({'start': slot['start'], 'end': blocked['start']})
                new_available_slots.append({'start': blocked['end'], 'end': slot['end']})
            # If blocked time overlaps with start of slot
            elif blocked['start'] <= slot['start'] and blocked['end'] > slot['start']:
                if blocked['end'] < slot['end']:
                    new_available_slots.append({'start': blocked['end'], 'end': slot['end']})
            # If blocked time overlaps with end of slot
            elif blocked['start'] < slot['end'] and blocked['end'] >= slot['end']:
                if blocked['start'] > slot['start']:
                    new_available_slots.append({'start': slot['start'], 'end': blocked['start']})
        
        available_slots = new_available_slots
    
    return available_slots

def schedule_fixed_tasks(fixed_tasks, available_slots, variable_tasks, break_times):
    """
    Distribute fixed tasks (like study hours) across available time slots
    """
    daily_schedule = []
    
    # Add all breaks and fixed-time variable tasks to the schedule
    daily_schedule.extend(break_times)
    daily_schedule.extend([t for t in variable_tasks if t.get('fixed_time', False)])
    
    # Sort available slots by start time
    available_slots.sort(key=lambda x: x['start'])
    
    # Calculate total available minutes
    total_available_minutes = sum((slot['end'] - slot['start']).total_seconds() / 60 for slot in available_slots)
    
    # Calculate total fixed task minutes
    total_fixed_task_minutes = sum(task['hours'] * 60 for task in fixed_tasks)
    
    # Check if there's enough time
    if total_fixed_task_minutes > total_available_minutes:
        # Not enough time, scale down proportionally
        scale_factor = total_available_minutes / total_fixed_task_minutes
        for task in fixed_tasks:
            task['adjusted_minutes'] = task['hours'] * 60 * scale_factor
    else:
        for task in fixed_tasks:
            task['adjusted_minutes'] = task['hours'] * 60
    
    # Allocate fixed tasks to available slots
    current_task_index = 0
    current_task_minutes_left = fixed_tasks[0]['adjusted_minutes'] if fixed_tasks else 0
    current_task_name = fixed_tasks[0]['name'] if fixed_tasks else ""
    
    for slot in available_slots:
        slot_minutes = (slot['end'] - slot['start']).total_seconds() / 60
        
        while slot_minutes > 0 and current_task_index < len(fixed_tasks):
            if current_task_minutes_left <= slot_minutes:
                # We can fit the entire remaining task in this slot
                task_end_time = slot['start'] + timedelta(minutes=current_task_minutes_left)
                
                daily_schedule.append({
                    'name': current_task_name,
                    'start': slot['start'],
                    'end': task_end_time,
                    'type': 'fixed'
                })
                
                # Update slot start time and remaining minutes
                slot['start'] = task_end_time
                slot_minutes -= current_task_minutes_left
                
                # Move to next task
                current_task_index += 1
                if current_task_index < len(fixed_tasks):
                    current_task_minutes_left = fixed_tasks[current_task_index]['adjusted_minutes']
                    current_task_name = fixed_tasks[current_task_index]['name']
                else:
                    # No more tasks to schedule
                    break
            else:
                # The task doesn't fit entirely in this slot
                daily_schedule.append({
                    'name': current_task_name,
                    'start': slot['start'],
                    'end': slot['end'],
                    'type': 'fixed'
                })
                
                # Update remaining task minutes
                current_task_minutes_left -= slot_minutes
                slot_minutes = 0
    
    # Add variable tasks that don't have fixed times
    flexible_tasks = [t for t in variable_tasks if not t.get('fixed_time', False)]
    
    # TODO: Implement logic to schedule flexible variable tasks
    
    # Sort the final schedule by start time
    daily_schedule.sort(key=lambda x: x['start'])
    
    return daily_schedule

if __name__ == '__main__':
    app.run(debug=True)