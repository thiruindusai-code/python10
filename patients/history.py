import csv

patient_name = input("Enter patient name: ").strip().title()

session_count = 0
total_reps = 0
total_time = 0

patient_sessions = []

with open("rehab_history.csv", "r") as file:
    reader = csv.DictReader(file)

    for session in reader:
        if session["patient"] == patient_name:
            patient_sessions.append(session)

            session_count += 1
            total_reps += int(session["completed_reps"])
            total_time += int(session["time_seconds"])

            print()
            print(f"Date: {session['date']}")
            print(f"Reps: {session['completed_reps']}")
            print(f"Target: {session['target_reps']}")
            print(f"Time: {session['time_seconds']} seconds")


if session_count > 0:
    average_reps = total_reps / session_count
    average_time = total_time / session_count
else:
    average_reps = 0
    average_time = 0


print()
print("----- Progress Summary -----")
print(f"Total sessions: {session_count}")
print(f"Total reps: {total_reps}")
print(f"Average reps: {average_reps}")
print(f"Average time: {average_time} seconds")

if len(patient_sessions) >= 2:

    previous_session = patient_sessions[-2]
    latest_session = patient_sessions[-1]

    previous_reps = int(previous_session["completed_reps"])
    latest_reps = int(latest_session["completed_reps"])

    previous_time = int(previous_session["time_seconds"])
    latest_time = int(latest_session["time_seconds"])

    print()
    print("----- Session Comparison -----")

    if latest_time < previous_time:
        print("Session time decreased")
    elif latest_time > previous_time:
        print("Session time increased")
    else:
        print("Session time stayed the same")

    if latest_reps > previous_reps:
        print("Reps increased")
    elif latest_reps < previous_reps:
        print("Reps decreased")
    else:
        print("Reps stayed the same")
