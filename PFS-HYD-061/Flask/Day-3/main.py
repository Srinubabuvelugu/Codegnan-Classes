def outer(fun):
    def inner(x, y):
        if y != 0:
            return fun(x, y)
        return "Zerodivision not possiable"
    return inner

@outer
def div(a, b):
    return a / b

print(div(4, 2))
print(div(4, 0))