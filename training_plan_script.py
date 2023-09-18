
import pandas as pd
from datetime import datetime, timedelta, time
import pytz

# Function to generate weekly training plan based on week number
def generate_weekly_plan(week_num, start_date):
    week_data = []
    
    # Define daily increments based on week number
    run_increment = 1 if week_num % 4 != 0 else 0
    bike_increment = 3 if week_num % 4 != 0 else 0
    
    # Define starting values for running and biking
    run_start = 6
    bike_start = 13
    
    for i in range(7):
        day = {}
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime('%A')
        
        day['Date'] = current_date.strftime('%Y-%m-%d')
        day['Day'] = day_name
        
        # Assign AM workouts
        if day_name in ['Monday', 'Thursday']:
            day['AM'] = "Resistance"
        else:
            day['AM'] = ""
        
        # Assign PM workouts
        if day_name == 'Monday':
            day['PM'] = 'Floor Hockey'
        elif day_name == 'Tuesday':
            day['PM'] = f"Run {run_start + (week_num - 1) * run_increment} km (easy)"
        elif day_name == 'Wednesday':
            day['PM'] = f"Bike {bike_start + (week_num - 1) * bike_increment} km (Z2)"
        elif day_name == 'Thursday':
            day['PM'] = f"Tempo Run {run_start + (week_num - 1) * run_increment} km"
        elif day_name == 'Friday':
            day['PM'] = f"Run {run_start + (week_num - 1) * run_increment} km (recovery)"
        elif day_name == 'Saturday':
            day['PM'] = f"Bike {bike_start + 5 + (week_num - 1) * bike_increment} km (Z2)"
        elif day_name == 'Sunday':
            if week_num % 4 == 0:  # Recovery week
                day['PM'] = "Rest"
            else:
                day['PM'] = f"Bike {bike_start + (week_num - 1) * bike_increment} km (intervals)"
        
        week_data.append(day)
    
    return week_data

# Helper function to format datetime for ICS
def format_datetime_ics(dt):
    return dt.strftime('%Y%m%dT%H%M%SZ')

def generate_ics_content(df_12weeks, pst):
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ChatGPT//Training Plan//EN\n"
    
    # Create events for the calendar
    for index, row in df_12weeks.iterrows():
        date = row['Date']
        day = row['Day']
        am_workout = row['AM']
        pm_workout = row['PM']

        if am_workout:
            start_time = time(7, 0) if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] else time(9, 0)
            dtstart = pst.localize(datetime.strptime(date, '%Y-%m-%d').combine(datetime.strptime(date, '%Y-%m-%d'), start_time)).astimezone(pytz.utc)
            dtend = dtstart + timedelta(hours=1)

            ics_content += f"\nBEGIN:VEVENT\nDTSTART:{format_datetime_ics(dtstart)}\nDTEND:{format_datetime_ics(dtend)}\nSUMMARY:AM Workout: {am_workout}\nEND:VEVENT\n"

        if pm_workout:
            start_time = time(18, 0) if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] else time(9, 0)
            dtstart = pst.localize(datetime.strptime(date, '%Y-%m-%d').combine(datetime.strptime(date, '%Y-%m-%d'), start_time)).astimezone(pytz.utc)
            dtend = dtstart + timedelta(hours=1)

            ics_content += f"\nBEGIN:VEVENT\nDTSTART:{format_datetime_ics(dtstart)}\nDTEND:{format_datetime_ics(dtend)}\nSUMMARY:PM Workout: {pm_workout}\nEND:VEVENT\n"

    ics_content += "END:VCALENDAR"
    return ics_content

# Main script to regenerate the 12-week plan and save it as an .ics file
if __name__ == "__main__":
    start_date = datetime(2023, 9, 18)
    all_weeks = []

    for i in range(12):
        week_data = generate_weekly_plan(i+1, start_date)
        all_weeks.append(week_data)
        start_date += timedelta(weeks=1)

    # Constructing the dataframe for the 12 weeks
    df_12weeks = pd.concat([pd.DataFrame(week) for week in all_weeks], ignore_index=True)
    
    # Timezone
    pst = pytz.timezone('US/Pacific')
    
    # Generate .ics content
    ics_content = generate_ics_content(df_12weeks, pst)

    # Save to an .ics file
    with open("training_plan_manual.ics", "w") as f:
        f.write(ics_content)

    print("ICS file generated as 'training_plan_manual.ics'")
