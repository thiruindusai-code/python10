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

age = int(input('what is your age '))
if age >= 18:
    print('eligible for drivers licence')
else:
    print('not eligible for drivers licence')
