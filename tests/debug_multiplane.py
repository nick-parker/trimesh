try:
    from . import generic as g
except BaseException:
    import generic as g
from math import sqrt

if __name__ == '__main__':
    mesh = g.get_mesh('featuretype.STL')

    paths = mesh.section_multiplane([0, 0, 0], [0, sqrt(2)/2, sqrt(2)/2], [1, 2, 3])