import csv


class Patient:
    def __init__(self, name, exercises):
        self.name = name
        self.exercises = exercises


name = input('Enter the patient name: ').strip().title()

while True:
    try:
        exercises = int(input('Enter number of exercises: '))
        break
    except ValueError:
        print('Please try a number value')

patient1 = Patient(name, exercises)

with open('patient.csv', 'a', newline="")as file:
    writer = csv.DictWriter(file, fieldnames=['name', 'exercises'])

    writer.writerow({
        'name': patient1.name,
        'exercises': patient1.exercises

    })
