"""
Test file with code smells for demonstration
"""


class SmellyClass:
    """A class with various code smells"""

    def __init__(self):
        self.attr1 = None
        self.attr2 = None
        self.attr3 = None
        self.attr4 = None
        self.attr5 = None
        self.attr6 = None
        self.attr7 = None
        self.attr8 = None
        self.attr9 = None
        self.attr10 = None
        self.attr11 = None  # Large class smell

    def method_with_too_many_params(self, a, b, c, d, e, f, g):
        """Method with too many parameters"""
        return a + b + c + d + e + f + g

    def long_method(self):
        """A very long method with many statements"""
        x = 1
        y = 2
        z = 3
        a = 4
        b = 5
        c = 6
        d = 7
        e = 8
        f = 9
        g = 10
        h = 11
        i = 12
        j = 13
        k = 14
        l_value = 15
        m = 16
        n = 17
        o = 18
        p = 19
        q = 20
        r = 21
        s = 22
        t = 23
        u = 24
        v = 25
        return (
            x
            + y
            + z
            + a
            + b
            + c
            + d
            + e
            + f
            + g
            + h
            + i
            + j
            + k
            + l_value
            + m
            + n
            + o
            + p
            + q
            + r
            + s
            + t
            + u
            + v
        )

    def complex_conditional(self, a, b, c, d, e):
        """Method with complex conditional"""
        if a and b and c and d and e:
            return True
        return False

    def nested_blocks(self):
        """Method with deeply nested blocks"""
        for i in range(10):
            if i > 5:
                for j in range(5):
                    if j > 2:
                        for k in range(3):
                            if k > 1:
                                print(i, j, k)


def duplicate_code():
    """Function with duplicate code"""
    print("This is a duplicate line")
    print("This is a duplicate line")
    print("This is a duplicate line")
    print("This is a duplicate line")


def another_duplicate():
    """Another function with duplicate code"""
    print("This is a duplicate line")
    print("This is a duplicate line")
    print("This is a duplicate line")
    print("This is a duplicate line")
