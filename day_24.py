import csv

name = input("Enter patient name: ").strip().title()
exercises = int(input("Enter number of exercises: ")).lower()

patient = {
    "name": name,
    "exercise": exercises
}

fieldnames = ["name", "exercise"]

with open("patient.csv", "a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writerow(patient)
