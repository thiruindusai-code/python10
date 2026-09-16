import csv

patient = [
    {
        'name': 'sai',
        'exercise': 12
    }, {
        'name': 'thiru',
        'exercise': 22
    }, {
        'name': 'indu',
        'exercise': 21
    }
]

fieldnames = ['name', 'exercise']

with open('patient.csv', 'w', newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(patient)
