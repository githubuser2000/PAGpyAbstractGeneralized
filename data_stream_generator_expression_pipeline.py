source = range(10)
stream = (x * x for x in source if x % 2 == 0)

for x in stream:
    print(x)
