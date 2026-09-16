class Student:
    def __init__(self, name, age, height):
        self.name = name
        self.age = age
        self.height = height

    def introduce(self):
        print(
            f"my name is {self.name}, my age is {self.age}, and my height is {self.height:.2f}.")


student1 = Student('Sai', 14, 5.6)
student2 = Student('Thiru', 45, 5.10)

student1.introduce()
student2.introduce()
