try:
    from . import generic as g
except BaseException:
    import generic as g


class PointsTest(g.unittest.TestCase):

    def test_pointcloud(self):
        '''
        Test pointcloud object
        '''
        shape = (100, 3)
        # random points
        points = g.np.random.random(shape)
        # make sure randomness never gives duplicates by offsetting
        points += g.np.arange(shape[0]).reshape((-1, 1))

        # make some duplicate vertices
        points[:10] = points[0]

        # create a pointcloud object
        cloud = g.trimesh.points.PointCloud(points)

        # set some random colors
        cloud.colors = g.np.random.random((shape[0], 4))

        # check shapes of data
        assert cloud.vertices.shape == shape
        assert cloud.extents.shape == (3,)
        assert cloud.bounds.shape == (2, 3)

        # remove the duplicates we created
        cloud.merge_vertices()

        # new shape post- merge
        new_shape = (shape[0] - 9, shape[1])

        # make sure vertices and colors are new shape
        assert cloud.vertices.shape == new_shape
        assert len(cloud.colors) == new_shape[0]

    def test_vertexonly(self):
        """
        Test to make sure we can instantiate a mesh with just vertices
        for some reason
        """

        v = g.np.random.random((1000, 3))
        v[g.np.floor(g.np.random.random(90) * len(v)).astype(int)] = v[0]

        mesh = g.trimesh.Trimesh(v)

        assert len(mesh.vertices) < 950
        assert len(mesh.vertices) > 900

    def test_plane(self):
        # make sure plane fitting works for 2D points in space
        for i in range(10):
            # create a random rotation
            matrix = g.trimesh.transformations.random_rotation_matrix()
            # create some random points in spacd
            p = g.np.random.random((1000, 3))
            # make them all lie on the XY plane so we know
            # the correct normal to check against
            p[:, 2] = 0
            # transform them into random frame
            p = g.trimesh.transform_points(p, matrix)
            # we made the Z values zero before transforming
            # so the true normal should be Z then rotated
            truth = g.trimesh.transform_points([[0, 0, 1]],
                                               matrix,
                                               translate=False)[0]
            # run the plane fit
            C, N = g.trimesh.points.plane_fit(p)

            # sign of normal is arbitrary on fit so check both
            assert g.np.allclose(truth, N) or g.np.allclose(truth, -N)


if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
