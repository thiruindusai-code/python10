import csv

with open('patient.txt', 'r') as file:
    reader = csv.DictReader(file)

    for patient in reader:
        name = patient['name']
        exercises = int(patient['exercises'])

        print(name)
        print(exercises)
