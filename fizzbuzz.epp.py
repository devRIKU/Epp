def __add(a, b):
    if isinstance(a, str) or isinstance(b, str): return str(a) + str(b)
    return a + b
def __say(x): print(x)
def __ask(prompt):
    v = input(prompt)
    if v.isdigit(): return int(v)
    try: return float(v)
    except: return v

number = 1
while number <= 15:
    if number % 15 == 0:
        __say('FizzBuzz.')
    elif number % 3 == 0:
        __say('Fizz.')
    elif number % 5 == 0:
        __say('Buzz.')
    else:
        __say(number)
    number = __add(number, 1)