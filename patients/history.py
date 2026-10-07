import csv

patient_name = input("Enter patient name: ").strip().title()

session_count = 0

total_reps = 0

with open("rehab_session.csv", "r") as file:
    reader = csv.DictReader(file)

    for session in reader:
        if session["patient"] == patient_name:
            total_reps += int(session["completed_reps"])
            session_count += 1


print(f"Total sessions: {session_count}")
print(f"Total reps: {total_reps}")

if session_count > 0:
    average_reps = total_reps/session_count
else:
    average_reps = 0
print(f"Average reps: {average_reps}")
