from pyqcy import *


class Arithmetic(TestCase):

    @qc
    def addition_actually_works(
        x=int_(min=0), y=int_(min=0)
    ):
        the_sum = x + y
        assert the_sum >= x and the_sum >= y
