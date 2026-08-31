def get_exercises():
    while True:
        try:
            exercises = int(input('how many exercises did you do '))
            return exercises
        except ValueError:
            print('please enter a number')


name = input('Enter your name: ')
exercises = get_exercises()
print(name, 'you did', exercises, 'exercises')

patients = []
patient = {
    'name': name,
    'exercises': exercises
}

patients.append(patient)
print(patients)


# patients = []
# again = 'no'
#     name = input('what is your name ')
#     exercises = int(input('how many exercises did you do '))

#     patient = {
#         'name': name,# while again != 'yes':

#         'exercises': exercises
#     }
#     patients.append(patient)
#     again = input('are you done? Type yes to stop')
# print(patients)
