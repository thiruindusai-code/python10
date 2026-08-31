'''name = 'sai rashwanth thiruvenkadam thangaraj indira priyadarshini'
with open('patient.txt', 'w') as file:
    file.write("\naaron"+ name)'''


name = input('enter patient name : ').strip().title()
with open('name.txt', 'a') as file:
    file.write('\nyour name is ' + name)
