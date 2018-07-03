try:
    from . import generic as g
except BaseException:
    import generic as g


class CreationTest(g.unittest.TestCase):

    def setUp(self):
        # we support two interfaces to triangle:
        # pip install meshpy
        # pip install triangle
        engines = []
        try:
            import meshpy
            engines.append('meshpy')
        except ImportError:
            g.log.error("no meshpy: skipping")

        try:
            from triangle import triangulate
            engines.append('triangle')
        except ImportError:
            g.log.error('no triangle: skipping')

        self.engines = engines

    def test_soup(self):
        count = 100
        mesh = g.trimesh.creation.random_soup(face_count=count)
        self.assertTrue(len(mesh.faces) == count)
        self.assertTrue(len(mesh.face_adjacency) == 0)
        self.assertTrue(len(mesh.split(only_watertight=True)) == 0)
        self.assertTrue(len(mesh.split(only_watertight=False)) == count)

    def test_uv(self):
        sphere = g.trimesh.creation.uv_sphere()
        self.assertTrue(sphere.is_watertight)
        self.assertTrue(sphere.is_winding_consistent)

    def test_path_sweep(self):

        if len(self.engines) == 0:
            return

        # Create base polygon
        vec = g.np.array([0, 1]) * 0.2
        n_comps = 100
        angle = g.np.pi * 2.0 / n_comps
        rotmat = g.np.array([
            [g.np.cos(angle), -g.np.sin(angle)],
            [g.np.sin(angle), g.np.cos(angle)]])
        perim = []
        for i in range(n_comps):
            perim.append(vec)
            vec = g.np.dot(rotmat, vec)
        poly = g.Polygon(perim)

        # Create 3D path
        angles = g.np.linspace(0, 8 * g.np.pi, 1000)
        x = angles / 10.0
        y = g.np.cos(angles)
        z = g.np.sin(angles)
        path = g.np.c_[x, y, z]

        # Extrude
        mesh = g.trimesh.creation.sweep_polygon(poly, path)
        self.assertTrue(mesh.is_volume)

    def test_triangulate(self):
        """
        test triangulate using meshpy and triangle
        """
        # circles
        bigger = g.Point([10, 0]).buffer(1.0)
        smaller = g.Point([10, 0]).buffer(.25)

        # circle with hole in center
        donut = bigger.difference(smaller)

        # make sure we have nonzero data
        assert bigger.area > 1.0
        # make sure difference did what we think it should
        assert g.np.isclose(donut.area,
                            bigger.area - smaller.area)

        times = {}
        iterations = 50
        # get a polygon to benchmark times with including interiors
        bench = g.get_mesh('2D/wrench.dxf').polygons_full[0]
        # check triangulation of both meshpy and triangle engine
        # including an example that has interiors
        for engine in self.engines:
            # make sure all our polygons triangulate resonably
            for poly in [bigger, smaller, donut, bench]:
                v, f = g.trimesh.creation.triangulate_polygon(
                    poly, engine=engine)
                assert g.trimesh.util.is_shape(v, (-1, 2))
                assert v.dtype.kind == 'f'
                assert g.trimesh.util.is_shape(f, (-1, 3))
                assert f.dtype.kind == 'i'
                tri = g.trimesh.util.three_dimensionalize(v)[1][f]
                area = g.trimesh.triangles.area(tri).sum()
                assert g.np.isclose(area, poly.area)

            try:
                # do a quick benchmark per engine
                # in general triangle appears to be 2x faster than meshpy
                times[engine] = min(
                    g.timeit.repeat('t(p, engine=e)',
                                    repeat=3,
                                    number=iterations,
                                    globals={'t': g.trimesh.creation.triangulate_polygon,
                                             'p': bench,
                                             'e': engine})) / iterations
            except BaseException:
                g.log.error('failed to benchmark triangle', exc_info=True)
        g.log.warning('benchmarked triangle interfaces: {}'.format(str(times)))

if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
