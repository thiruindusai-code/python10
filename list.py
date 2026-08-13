numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for number in numbers:
    if number % 2 == 0:
        print(number)


numbers = [1, 2, 2, 3, 4, 4, 5]
numbers = set(numbers)
print(numbers)


numbers = (1, 2, 3, 4)
numbers = list(numbers)
numbers.append(5)
print(numbers)


num1 = [1, 2, 3, 4, 5, 5, 6, 5]
num2 = [1, 2, 4, 5, 12, 4, 7]
num1 = set(num1)
num2 = set(num2)
print(num1 ^ num2)

students = ("Sai", "Indu", "Thiru", "Aaron")
students = sorted(students)
for student in students:
    print(student)




vowels = {"a", "e", "i", "o", "u"}
character = input("Enter a character: ")
if character in vowels:
    print("Vowel")
else:
    print("Not a vowel")


numbers = [25, 10, 45, 5, 30]
print("Largest:", max(numbers))
print("Smallest:", min(numbers))


students = [
    {"name": "Sai", "marks": 85},
    {"name": "Indu", "marks": 75},
    {"name": "Thiru", "marks": 92}
]
for student in students:
    if student["marks"] > 80:
        print(student["name"])
