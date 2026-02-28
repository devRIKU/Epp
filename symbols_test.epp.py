def __add(a, b):
    if isinstance(a, str) or isinstance(b, str): return str(a) + str(b)
    return a + b
def __say(x): print(x)
def __ask(prompt):
    v = input(prompt)
    if v.isdigit(): return int(v)
    try: return float(v)
    except: return v

# note We can now use math and logic symbols
max_value = 100
iterator = 0
while iterator <= 5:
    if iterator < 3  or  iterator == 5:
        __say(__add('Iterator is small or exactly 5. Iterator = ', iterator))
    iterator = __add(iterator, 1)
is_valid = True
if is_valid  and  iterator > 2:
    __say(__add('Everything is valid! Iterator reached ', iterator))