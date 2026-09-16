import csv


def calculate_average(total_exercises, patient_count):
    if patient_count == 0:
        return 0

    average = total_exercises/patient_count
    return average


def get_totals():
    total_exercises = 0
    patient_count = 0

    with open('patient.csv', 'r') as file:
        reader = csv.DictReader(file)

        for patient in reader:
            total_exercises += int(patient['exercises'])
            patient_count += 1

    return total_exercises, patient_count


total_exercises, patient_count = get_totals()

average = calculate_average(total_exercises, patient_count)

print(total_exercises)
print(patient_count)
print(average)
