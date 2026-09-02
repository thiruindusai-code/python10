'''line = 'sai,12'

parts = line.split(',')

name = parts[0]
exercises = int(parts[1])

patients = {
    'name': name,
    'exercises': exercises
}

print(patients)'''

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
