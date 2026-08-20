# day 1
'''patient_tracking = int(input('what is the number of exersize you completed? ')
                       )


def check_progress(patient_tracking):
    if 0 <= patient_tracking <= 4:
        print('keep going')
    elif patient_tracking >= 5 and patient_tracking <= 9:
        print('good progress')
    elif patient_tracking >= 10:
        print('goal reached')
    else:
        print('please enter positive number')


check_progress(patient_tracking)'''

# day2


'''def check_progress(exercises):
    if exercises >= 0 and exercises <= 4:
        return 'keep going'
    elif exercises >= 5 and exercises <= 9:
        return 'almost there'
    elif exercises >= 10:
        return 'goal reached'
    else:
        return 'enter a positive number'


message = check_progress(11)
print(message)'''


# day 3

'''age = int(input('what is your age '))
if age >= 18:
    print('eligible for drivers licence')
else:
    print('not eligible for drivers licence')'''


'''def check_progress(exersices):
    if exersices >= 0 and exersices <= 4:
        return 'keep going'
    elif exersices >= 5 and exersices <= 9:
        return 'almost there'
    elif exersices >= 10:
        return 'goal reached'
    else:
        return 'please enter a positive number'


exersices = int(input('how many exercises have you completed '))
message = check_progress(exersices)
print(message)'''

# day4

'''total = 0
num = [3, 6, 9]

for number in num:
    total += number

average = total // len(num)
print(average)'''

# day 4

'''exercises = [3, 6, 9, 4, 8]
total = 0
for exercise in exercises:
    total += exercise
average = total // len(exercises)
print(average)'''

# day 5

students = [
    {'name': 'sai', 'age': 14, 'classification': 'robotics'},
    {'name': 'aaron', 'age': 15, 'classification': 'tsa'},
    {'name': 'akhil', 'age': 13, 'classification': 'deca'}
]

for student in students:
    print(student['name'], student['classification'])
