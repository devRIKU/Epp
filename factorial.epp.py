def __add(a, b):
    if isinstance(a, str) or isinstance(b, str): return str(a) + str(b)
    return a + b
def __say(x): print(x)
def __ask(prompt):
    v = input(prompt)
    if v.isdigit(): return int(v)
    try: return float(v)
    except: return v

def factorial(n):
    if n <= 1:
        return 1
    smaller = n - 1
    sub_result = factorial(smaller)
    return n * sub_result
answer = factorial(5)
__say(__add('Factorial of 5 is ', answer))