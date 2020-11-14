def compose(func_1, func_2, unpack=False):
    """
    compose(func_1, func_2, unpack=False) -> function

    The function returned by compose is a composition of func_1 and func_2.
    That is, compose(func_1, func_2)(5) == func_1(func_2(5))
    """
    if not callable(func_1):
        raise TypeError("First argument to compose must be callable")
    if not callable(func_2):
        raise TypeError("Second argument to compose must be callable")

    if unpack:
        def composition(*args, **kwargs):
            return func_1(*func_2(*args, **kwargs))
    else:
        def composition(*args, **kwargs):
            return func_1(func_2(*args, **kwargs))
    return composition
