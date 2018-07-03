try:
    from . import generic as g
except BaseException:
    import generic as g


class SectionTest(g.unittest.TestCase):

    def test_section(self):
        mesh = g.get_mesh('featuretype.STL')
        # this hits many edge cases
        step = .125
        z_levels = g.np.arange(start=mesh.bounds[0][2],
                               stop=mesh.bounds[1][2] + 2 * step,
                               step=step)
        sections = [None] * len(z_levels)

        for index, z in enumerate(z_levels):
            plane_origin = [0, 0, z]
            plane_normal = [0, 0, 1]

            section = mesh.section(plane_origin=plane_origin,
                                   plane_normal=plane_normal)
            if section is None:
                # section will return None if the plane doesn't
                # intersect the mesh
                assert z > (mesh.bounds[1][2] -
                            g.trimesh.constants.tol.merge)
                continue

            planar, to_3D = section.to_planar()
            assert planar.is_closed
            assert (len(planar.polygons_full) > 0)
            sections[index] = planar

        # try getting the sections as Path2D through
        # the multiplane method
        paths = mesh.section_multiplane(plane_origin=[0, 0, 0],
                                        plane_normal=[0, 0, 1],
                                        heights=z_levels)

        # call the multiplane method directly
        lines, faces, T = g.trimesh.intersections.mesh_multiplane(
            mesh=mesh,
            plane_origin=[0, 0, 0],
            plane_normal=[0, 0, 1],
            heights=z_levels)

        # make sure various methods return the same results
        for index in range(len(z_levels)):
            if sections[index] is None:
                assert len(lines[index]) == 0
                continue
            rc = g.trimesh.load_path(lines[index])
            assert g.np.isclose(rc.area, sections[index].area)
            assert g.np.isclose(rc.area, paths[index].area)


class PlaneLine(g.unittest.TestCase):

    def test_planes(self):
        count = 10
        z = g.np.linspace(-1, 1, count)

        plane_origins = g.np.column_stack((
            g.np.random.random((count, 2)), z))
        plane_normals = g.np.tile([0, 0, -1], (count, 1))

        line_origins = g.np.tile([0, 0, 0], (count, 1))
        line_directions = g.np.random.random((count, 3))

        i, valid = g.trimesh.intersections.planes_lines(
            plane_origins=plane_origins,
            plane_normals=plane_normals,
            line_origins=line_origins,
            line_directions=line_directions)
        assert valid.all()
        assert (g.np.abs(i[:, 2] - z) < g.tol.merge).all()


if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
