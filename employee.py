class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def introduce(self):
        print(
            f"My name is {self.name} and my monthly salary is {self.salary}.")


employee1 = Employee('Sai', 10000)
employee2 = Employee('thiru', 10001)

employee1.introduce()
employee2.introduce()
