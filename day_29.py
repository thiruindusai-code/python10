class Patient:
    def __init__(self, name, exercises):
        self.name = name
        self.exercises = exercises

    def check_progress(self):
        if self.exercises <= 4:
            return 'keep going'
        elif self.exercises <= 9:
            return 'almost there'
        else:
            return 'goal reached'

    def show_status(self):
        result = self.check_progress()
        print(f"{self.name} has completed {self.exercises} - {result}")


patient1 = Patient('Sai', 3)
patient2 = Patient('Thiru', 6)
patient3 = Patient('Indu', 10)
patient1.show_status()
patient2.show_status()
patient3.show_status()
