import csv


def check_progress(exercises):
    exercises = int(exercises)
    if exercises < 0:
        return 'please enter a positive number'
    elif exercises <= 4:
        return 'keep going'
    elif exercises <= 9:
        return 'almost there'
    else:
        return 'goal reached'


with open('patient.csv', 'r') as file:
    reader = csv.DictReader(file)

    for patient in reader:
        result = check_progress(patient['exercises'])

        print(
            f"{patient['name']} has completed {patient['exercises']} exercises - {result}")


'''def check_progress(patient):

    print(f"{patient['name']} has completed {patient['exercises']} exercises ")


with open('patient.csv', 'r') as file:
    reader = csv.DictReader(file)

    for patient in reader:
        check_progress(patient)'''
