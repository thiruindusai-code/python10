import csv


class Patient:
    def __init__(self, name, exercises):
        self.name = name
        self.exercises = exercises

    def check_progress(self):
        if self.exercises < 0:
            return 'Please type positive number'
        elif self.exercises <= 4:
            return 'keep going'
        elif self.exercises <= 9:
            return 'almost there'
        else:
            return 'Goal reached'

    def show_status(self):
        result = self.check_progress()
        print(f"{self.name} has done {self.exercises} exercises - {result}")


patients = []
with open('patient.csv', 'r') as file:
    reader = csv.DictReader(file)

    for row in reader:
        name = row['name']
        exercises = int(row['exercises'])

        patient = Patient(name, exercises)

        patients.append(patient)

for patient in patients:
    patient.show_status()
