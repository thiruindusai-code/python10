import csv

total_exercises = 0
patient_count = 0
with open('patient.csv', 'r') as file:
    reader = csv.DictReader(file)

    for patient in reader:
        total_exercises += int(patient['exercises'])
        patient_count += 1

average = total_exercises/patient_count


print(f"average is {average}")
print(f"total exercises are {total_exercises}")
print(f"patient count is {patient_count}")
