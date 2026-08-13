'''list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for list in list:
    if list % 2 == 0:
        print(list)


list = [1, 1, 2, 2, 3, 4, 5, 5]
list = set(list)
print(list)


tup = (1, 2, 3, 4)
tup = list(tup)
tup.append(5)
print(tup)'''


'''list1 = [1, 2, 3]
list2 = [2, 4, 5]
list1 = set(list1)
list2 = set(list2)
print(list1 & list2)'''


'''name = ('sai', 'thiru', 'indu')
name = sorted(name, reverse=True)
print(name)


vowels = ('a', 'e', 'i', 'o', 'u')

charecter = input("enter a charecter ")
if charecter in vowels:
    print('is a vowel')
else:
    print('its not a vowel')'''


'''numbers = [1, 2, 3, 4, 5, 6, 7]
print(max(numbers))
print(min(numbers))'''

'''list1 = [1, 2, 3]
list2 = [1, 4, 2]
list3 = list1 + list2
list3 = set(list3)
print(list3)'''

'''student = [
    {'name':  'sai', 'marks': 80},
    {'name': 'thiru', 'marks': 70},
    {'name': 'indu', 'marks': 100}
]

for students in student:
    if students['marks'] > 80:
        print(students)'''


'''sentence = 'apple banana mango grapes apple'
words = sentence.split()
words = list(words)
print(words[3])'''


'''print(words)
print(len(words))
a = sentence.capitalize()
print(a)

print(words[3])'''


students = [
    {'name': 'sai', 'grade': 10},
    {'name': 'thiru', 'grade': 10},
    {'name': 'indu', 'grade': 12}
]

count = 0
for student in students:
    if student['grade'] == 10:
        count = count+1

print(count)
