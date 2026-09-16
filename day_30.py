class Patient:
    def __init__(self, name, exercises):
        self.name = name
        self.exercises = exercises

    def check_progress(self):
        if self.exercises < 0:
            return 'This is not a positive number'
        elif self.exercises <= 4:
            return 'Keep going'
        elif self.exercises <= 9:
            return 'almost there'
        else:
            return 'Goal reached'

    def show_status(self):
        result = self.check_progress()
        print(f"{self.name} has completed {self.exercises} exercises. - {result}")


patients = [
    Patient('sai', 3),
    Patient('Thiru', 6),
    Patient('Indu', 12)
]

patients.append(Patient("aaron", -4))

for patient in patients:
    patient.show_status()
