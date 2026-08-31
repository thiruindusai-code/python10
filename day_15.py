filename = input('enter the file name to read ').strip()

try:
    with open(filename, 'r') as file:
        data = file.read()
        print(data)
except FileNotFoundError:
    print('enter file name correctly please. the file name you have entered is ', filename)
