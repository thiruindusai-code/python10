def check_progress(exercises):
    if exercises >= 0 and exercises <= 4:
        return 'keep going'
    elif exercises >= 5 and exercises <= 9:
        return 'almost there'
    elif exercises >= 10:
        return 'goal reached'
    else:
        return 'please enter a positive number '


patients = []

with open('patient.txt', 'r') as file:
    for line in file:
        line = line.strip()

        parts = line.split(',')

        name = parts[0]
        exercises = int(parts[1])

        patient = {
            'name': name,
            'exercises': exercises
        }

        patients.append(patient)

print(patients)


for patient in patients:
    result = check_progress(patient['exercises'])
    print(patient['name'], result)
