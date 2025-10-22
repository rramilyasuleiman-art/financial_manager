def compose(*funcs):
    def inner(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return inner

def pipe(x, *funcs):
    for f in funcs:
        x = f(x)
    return x
