from pyqcy import *


@qc
def addition_on_ints(x=int, y=int):
    assert isinstance(x + y, int)


if __name__ == '__main__':
    main()
