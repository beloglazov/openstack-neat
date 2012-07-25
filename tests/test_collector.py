from pyqcy import *


class Arithmetic(TestCase):

    @qc
    def addition_on_ints(x=int, y=int):
        assert isinstance(x + y, int)

    @qc
    def subtraction_on_ints(x=int, y=int):
        assert isinstance(x - y, int)
