def test(*args):
    testlist = args

    for arg in args:
        print(arg)

num = 1

test('i', 'like', num, 'pie')