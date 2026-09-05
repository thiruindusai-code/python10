from day_19 import check_progress, patients
with open('report.txt', 'w')as file:
    for patient in patients:
        result = check_progress(patient['exercises'])

        message = f"{patient['name']} - {patient['exercises']} - exercise - {result}"

        file.write(message + '\n')
with open('report.txt', 'r')as file:
    print(file.read())
