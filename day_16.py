while True:
    filename = input('enter a file name ').strip()

    try:
        with open(filename, 'r')as file:
            data = file.read()

            print(data)
            break
    except FileNotFoundError:
        print('your file has not been found. The file name you have entered is ' + filename)
