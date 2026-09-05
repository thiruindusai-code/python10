import csv

with open('patient.txt', 'r') as file:
    reader = csv.reader(file)
patients = []

for row in reader:
    name = row[0]
    exercises = int(row[1])

    patients = {
        'name': name,
        'exercises': exercises
    }

    patients.append(patients)

print(patients)
