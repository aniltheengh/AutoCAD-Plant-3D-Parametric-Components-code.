"""Offline parameter and geometry-call checks using only Python's standard library.

The recorder below records the requested cylinders, transformations, booleans,
and ports. It does NOT implement Autodesk's geometry kernel or registration.
Passing these tests does not establish Plant 3D compatibility, solid validity,
catalog insertion, connected routing, or isometric output. Test those in Plant 3D.
"""

import inspect
import math
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "CustomScripts"
COMPONENT_NAMES = ("AT_CYLINDER", "AT_SPACER", "AT_FLANGE", "AT_BLIND_FLANGE",
                   "AT_UBAND", "AT_UBOLT", "AT_REDUCER", "AT_ELBOW90",
                   "AT_TEE", "AT_CAP", "AT_GROOVED_COUPLING", "AT_PIPE_SHOE")


class SessionRecorder:
    def __init__(self):
        self.cylinders = []
        self.objects = []
        self.ports = []
        self.events = []

    def setPoint(self, position, direction):
        self.ports.append((tuple(position), tuple(direction)))


class PrimitiveRecorder:
    """Record requests only; no topology, solid generation, or CAD validation."""

    def __init__(self, session):
        self.session = session
        self.origin = (0.0, 0.0, 0.0)
        self.axis = (0.0, 0.0, 1.0)
        self.cutters = []
        self.joined = []
        self.erased = False
        session.objects.append(self)

    def rotateY(self, degrees):
        radians = math.radians(degrees)
        c, s = math.cos(radians), math.sin(radians)

        def rotate(vector):
            x, y, z = vector
            return (c * x + s * z, y, -s * x + c * z)

        self.origin = rotate(self.origin)
        self.axis = rotate(self.axis)
        return self

    def rotateZ(self, degrees):
        radians = math.radians(degrees)
        c, s = math.cos(radians), math.sin(radians)

        def rotate(vector):
            x, y, z = vector
            return (c * x - s * y, s * x + c * y, z)

        self.origin = rotate(self.origin)
        self.axis = rotate(self.axis)
        return self

    def translate(self, vector):
        self.origin = tuple(a + b for a, b in zip(self.origin, vector))
        return self

    def subtractFrom(self, cutter):
        self.cutters.append(cutter)
        self.session.events.append(("subtract", self, cutter))
        return self

    def erase(self):
        self.erased = True
        self.session.events.append(("erase", self))

    def uniteWith(self, other):
        self.joined.append(other)
        self.session.events.append(("unite", self, other))
        return self


class CylinderRecorder(PrimitiveRecorder):
    def __init__(self, session, R, H, O):
        super().__init__(session)
        self.radius, self.length, self.bore_radius = R, H, O
        session.cylinders.append(self)


class BoxRecorder(PrimitiveRecorder):
    def __init__(self, session, L, W, H):
        super().__init__(session)
        self.spans = (H, L, W)


class TorusRecorder(PrimitiveRecorder):
    def __init__(self, session, R1, R2):
        super().__init__(session)
        self.bend_radius, self.tube_radius = R1, R2


class ConeRecorder(PrimitiveRecorder):
    def __init__(self, session, R1, R2, H, E):
        super().__init__(session)
        self.radii, self.length, self.eccentricity = (R1, R2), H, E


class EllipsoidHeadRecorder(PrimitiveRecorder):
    def __init__(self, session, R):
        super().__init__(session)
        # Documented 2:1 head: semi-axes R and R/2, base point at bottom centre.
        self.radius, self.height = R, R / 2.0


def load_component(name):
    """Execute one real source file with isolated recording API replacements."""
    package = types.ModuleType("varmain")
    package.__path__ = []
    primitives = types.ModuleType("varmain.primitiv")
    primitives.CYLINDER = CylinderRecorder
    primitives.BOX = BoxRecorder
    primitives.TORUS = TorusRecorder
    primitives.CONE = ConeRecorder
    primitives.ELLIPSOIDHEAD2 = EllipsoidHeadRecorder
    custom = types.ModuleType("varmain.custom")
    custom.LENGTH, custom.LENGTH0, custom.ENUM = "LENGTH", "LENGTH0", "ENUM"

    def activate(**metadata):
        def decorate(function):
            function.metadata = metadata
            return function
        return decorate

    def group(*args, **kwargs):
        return lambda function: function

    def param(**metadata):
        def decorate(function):
            function.parameters = getattr(function, "parameters", []) + [metadata]
            return function
        return decorate

    def enum(value, label):
        def decorate(function):
            function.enum_values = getattr(function, "enum_values", []) + [value]
            return function
        return decorate

    custom.activate, custom.group = activate, group
    custom.param, custom.enum = param, enum
    source = SCRIPT_DIR / (name + ".py")
    namespace = {"__name__": name, "__file__": str(source)}
    with patch.dict(sys.modules, {
        "varmain": package,
        "varmain.primitiv": primitives,
        "varmain.custom": custom,
    }):
        exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), namespace)
    return namespace[name]


class ComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.functions = {
            name: load_component(name)
            for name in COMPONENT_NAMES
        }

    def run_component(self, name, **parameters):
        session = SessionRecorder()
        self.functions[name](session, **parameters)
        return session

    def assert_vector_close(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            self.assertAlmostEqual(a, b, places=10)

    def assert_rejected_without_geometry(self, name, **parameters):
        session = SessionRecorder()
        with self.assertRaises(ValueError):
            self.functions[name](session, **parameters)
        self.assertEqual(session.objects, [])
        self.assertEqual(session.ports, [])

    def test_each_script_has_matching_entry_point_and_dimension_metadata(self):
        self.assertEqual({p.stem for p in SCRIPT_DIR.glob("*.py")}, set(self.functions))
        for name, function in self.functions.items():
            with self.subTest(component=name):
                self.assertEqual(function.__name__, name)
                dimensions = set(inspect.signature(function).parameters) - {"s", "kw"}
                declared = set()
                for metadata in function.parameters:
                    declared.update(k for k, v in metadata.items() if v in ("LENGTH", "LENGTH0", "ENUM"))
                self.assertEqual(declared, dimensions)
                self.assertEqual(function.metadata["LengthUnit"], "mm")

    def test_metadata_port_counts_match_created_points(self):
        for name, function in self.functions.items():
            with self.subTest(component=name):
                session = self.run_component(name)
                self.assertEqual(len(session.ports), int(function.metadata["Ports"]))

    def test_cylinder_default_dimensions_and_orientation(self):
        session = self.run_component("AT_CYLINDER")
        self.assertEqual(len(session.cylinders), 1)
        body = session.cylinders[0]
        self.assertEqual((2 * body.radius, body.length, body.bore_radius), (100, 300, 0))
        self.assert_vector_close(body.origin, (0, 0, 0))
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0))])

    def test_cylinder_fractional_dimensions_do_not_truncate(self):
        body = self.run_component("AT_CYLINDER", D=7.5, L=12.25).cylinders[0]
        self.assertEqual(body.radius, 3.75)
        self.assertEqual(body.length, 12.25)

    def test_spacer_bore_is_a_radius_and_wall_is_six_mm(self):
        body = self.run_component("AT_SPACER").cylinders[0]
        self.assertAlmostEqual(2 * body.bore_radius, 102.3)
        self.assertAlmostEqual(2 * body.radius, 114.3)
        self.assertAlmostEqual(body.radius - body.bore_radius, 6.0)
        self.assert_vector_close(body.axis, (1, 0, 0))

    def test_spacer_custom_dimensions_and_ports(self):
        session = self.run_component("AT_SPACER", OD=80, ID=60, L=50)
        body = session.cylinders[0]
        self.assertEqual((body.radius, body.bore_radius, body.length), (40, 30, 50))
        self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0)), ((50, 0, 0), (1, 0, 0))])

    def test_flange_annulus_and_face_ports(self):
        session = self.run_component("AT_FLANGE")
        body = session.cylinders[0]
        self.assertEqual((body.radius, body.bore_radius, body.length), (90, 45, 20))
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0)), ((20, 0, 0), (1, 0, 0))])

    def test_flange_four_hole_pattern_starts_at_positive_y(self):
        session = self.run_component("AT_FLANGE")
        cutters = session.cylinders[0].cutters
        self.assertEqual(len(cutters), 4)
        expected_centres = [(70, 0), (0, 70), (-70, 0), (0, -70)]
        for cutter, yz in zip(cutters, expected_centres):
            self.assert_vector_close(cutter.origin[1:], yz)
            self.assertEqual(cutter.radius, 9)

    def test_flange_cutters_pass_through_both_faces(self):
        for thickness in (0.5, 20, 1000):
            with self.subTest(thickness=thickness):
                body = self.run_component("AT_FLANGE", T=thickness).cylinders[0]
                for cutter in body.cutters:
                    self.assert_vector_close(cutter.axis, (1, 0, 0))
                    self.assertEqual(cutter.bore_radius, 0)
                    self.assertLess(cutter.origin[0], 0)
                    self.assertGreater(cutter.origin[0] + cutter.length, thickness)

    def test_flange_erases_each_cutter_after_subtraction_and_keeps_body(self):
        session = self.run_component("AT_FLANGE")
        body = session.cylinders[0]
        self.assertFalse(body.erased)
        self.assertEqual(len(session.cylinders), 5)
        self.assertEqual(len(session.events), 8)
        for index, cutter in enumerate(body.cutters):
            self.assertTrue(cutter.erased)
            self.assertEqual(session.events[2 * index], ("subtract", body, cutter))
            self.assertEqual(session.events[2 * index + 1], ("erase", cutter))

    def test_all_supported_hole_counts_have_separated_regular_patterns(self):
        self.assertEqual(set(self.functions["AT_FLANGE"].enum_values), {4, 8, 12, 16})
        for count in (4, 8, 12, 16):
            with self.subTest(count=count):
                body = self.run_component("AT_FLANGE", N=count).cylinders[0]
                self.assertEqual(len(body.cutters), count)
                centres = [c.origin[1:] for c in body.cutters]
                distances = []
                for index, cutter in enumerate(body.cutters):
                    centre_radius = math.hypot(*centres[index])
                    self.assertAlmostEqual(centre_radius, 70)
                    self.assertGreater(centre_radius - cutter.radius, body.bore_radius)
                    self.assertLess(centre_radius + cutter.radius, body.radius)
                    distances.append(math.dist(centres[index], centres[(index + 1) % count]))
                    for other in body.cutters[index + 1:]:
                        self.assertGreater(math.dist(cutter.origin[1:], other.origin[1:]),
                                           cutter.radius + other.radius)
                self.assertLess(max(distances) - min(distances), 1e-10)

    def test_custom_eight_hole_example(self):
        session = self.run_component("AT_FLANGE", OD=220, ID=110, T=25,
                                     BCD=175, HD=18, N=8)
        body = session.cylinders[0]
        self.assertEqual((body.radius, body.bore_radius, body.length), (110, 55, 25))
        self.assertEqual(len(body.cutters), 8)
        self.assertAlmostEqual(math.hypot(*body.cutters[3].origin[1:]), 87.5)
        self.assertEqual(session.ports[-1][0], (25, 0, 0))

    def test_nonpositive_dimensions_rejected_before_geometry(self):
        for name, function in self.functions.items():
            zero_allowed = {k for metadata in function.parameters
                            for k, v in metadata.items() if v == "LENGTH0"}
            for dimension in inspect.signature(function).parameters:
                if dimension in ("s", "kw", "N"):
                    continue
                for value in ((-1,) if dimension in zero_allowed else (0, -1)):
                    with self.subTest(component=name, dimension=dimension, value=value):
                        self.assert_rejected_without_geometry(name, **{dimension: value})

    def test_nonfinite_dimensions_rejected_before_geometry(self):
        for name, function in self.functions.items():
            for dimension in inspect.signature(function).parameters:
                if dimension in ("s", "kw", "N"):
                    continue
                for value in (float("nan"), float("inf"), -float("inf")):
                    with self.subTest(component=name, dimension=dimension, value=value):
                        self.assert_rejected_without_geometry(name, **{dimension: value})

    def test_nonnumeric_dimensions_rejected_before_geometry(self):
        for name in self.functions:
            dimension = next(k for k in inspect.signature(self.functions[name]).parameters
                             if k not in ("s", "kw"))
            for value in (None, "not a dimension", object()):
                with self.subTest(component=name, value=value):
                    self.assert_rejected_without_geometry(name, **{dimension: value})

    def test_impossible_bores_rejected(self):
        for name in ("AT_SPACER", "AT_FLANGE"):
            for bore in (100, 101):
                with self.subTest(component=name, bore=bore):
                    self.assert_rejected_without_geometry(name, OD=100, ID=bore)

    def test_holes_touching_or_breaking_into_bore_rejected(self):
        for bolt_circle in (108, 107):
            with self.subTest(bolt_circle=bolt_circle):
                self.assert_rejected_without_geometry("AT_FLANGE", ID=90, HD=18,
                                                      BCD=bolt_circle)

    def test_holes_touching_or_breaking_outer_edge_rejected(self):
        for bolt_circle in (162, 163):
            with self.subTest(bolt_circle=bolt_circle):
                self.assert_rejected_without_geometry("AT_FLANGE", OD=180, HD=18,
                                                      BCD=bolt_circle)

    def test_adjacent_holes_touching_or_overlapping_rejected(self):
        # Four centres at (50,0), (0,50), ... have separation sqrt(5000).
        # Both radii clear the bore and outside edge, isolating this constraint.
        for diameter in (math.sqrt(5000), 72):
            with self.subTest(hole_diameter=diameter):
                self.assert_rejected_without_geometry("AT_FLANGE", OD=200, ID=10,
                                                      BCD=100, HD=diameter, N=4)
        self.assert_rejected_without_geometry("AT_FLANGE", OD=200, ID=80,
                                              BCD=140, HD=28, N=16)

    def test_unsupported_or_fractional_hole_counts_rejected(self):
        for count in (0, -4, 3, 6, 4.5, 32, float("nan"), float("inf"), "four"):
            with self.subTest(count=count):
                self.assert_rejected_without_geometry("AT_FLANGE", N=count)

    def test_uband_crown_inside_clearance_and_width(self):
        body = self.run_component("AT_UBAND").objects[0]
        self.assertIsInstance(body, CylinderRecorder)
        self.assertAlmostEqual(body.bore_radius - 114.3 / 2, 1.0)
        self.assertAlmostEqual(body.radius - body.bore_radius, 6.0)
        self.assertEqual(body.length, 30.0)
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assertEqual(body.origin, (-15, 0, 0))
        cut = body.cutters[0]
        self.assertEqual(cut.origin[2] + cut.spans[2] / 2, 0)
        self.assertLess(cut.origin[2] - cut.spans[2] / 2, -body.radius)

    def test_uband_legs_touch_crown_and_feet_overlap_legs(self):
        body = self.run_component("AT_UBAND").objects[0]
        self.assertEqual(len(body.joined), 4)
        for leg, foot in (body.joined[:2], body.joined[2:]):
            self.assertEqual(leg.origin[2] + leg.spans[2] / 2, 0)
            self.assertEqual(leg.origin[2] - leg.spans[2] / 2, -75)
            self.assertEqual(foot.origin[2] - foot.spans[2] / 2, -75)
            self.assertEqual(foot.origin[2] + foot.spans[2] / 2, -69)
            self.assertAlmostEqual(abs(leg.origin[1]) - leg.spans[1] / 2, body.bore_radius)
            # Intersection in Y has positive width, not an unattached foot.
            overlap = min(leg.origin[1] + leg.spans[1] / 2, foot.origin[1] + foot.spans[1] / 2) - max(leg.origin[1] - leg.spans[1] / 2, foot.origin[1] - foot.spans[1] / 2)
            self.assertAlmostEqual(overlap, 6)

    def test_uband_mounting_holes_are_centred_in_free_foot_area(self):
        body = self.run_component("AT_UBAND").objects[0]
        holes = body.cutters[1:]
        self.assertEqual(len(holes), 2)
        for hole in holes:
            self.assertEqual(hole.origin[0], 0)
            self.assertAlmostEqual(abs(hole.origin[1]), body.radius + 35 / 2)
            self.assertLess(abs(hole.origin[0]) + hole.radius, 30 / 2)
            self.assertGreater(abs(hole.origin[1]) - hole.radius, body.radius)
            self.assertLess(abs(hole.origin[1]) + hole.radius, body.radius + 35)
            self.assertLess(hole.origin[2], -75)
            self.assertGreater(hole.origin[2] + hole.length, -69)

    def test_uband_bad_foot_dimensions_rejected(self):
        for parameters in ({"H": 6}, {"H": 5}, {"HD": 30}, {"F": 11}, {"C": -0.1}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_UBAND", **parameters)

    def test_clamps_allow_zero_clearance_and_custom_sizes(self):
        for name in ("AT_UBAND", "AT_UBOLT"):
            session = self.run_component(name, PD=60.3, C=0, H=80)
            body = session.objects[0]
            inner = body.bore_radius if name == "AT_UBAND" else body.bend_radius - body.tube_radius
            self.assertAlmostEqual(inner, 60.3 / 2)
            self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0))])

    def test_ubolt_radius_fit_and_tangent_leg_alignment(self):
        body = self.run_component("AT_UBOLT").objects[0]
        self.assertIsInstance(body, TorusRecorder)
        self.assertAlmostEqual(body.bend_radius - body.tube_radius, 114.3 / 2 + 1)
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assertEqual(len(body.joined), 2)
        for leg in body.joined:
            self.assertAlmostEqual(abs(leg.origin[1]), body.bend_radius)
            self.assertEqual(leg.radius, body.tube_radius)
            self.assertEqual(leg.origin[2], -100)
            self.assertEqual(leg.origin[2] + leg.length, 0)
            self.assert_vector_close(leg.axis, (0, 0, 1))

    def test_reducer_bore_extrapolation_preserves_end_dimensions(self):
        session = self.run_component("AT_REDUCER")
        body = session.objects[0]
        bore = body.cutters[0]
        self.assertEqual(body.radii, (168.3 / 2, 114.3 / 2))
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assertLess(bore.origin[0], 0)
        self.assertGreater(bore.origin[0] + bore.length, 150)
        for x, diameter in ((0, 154.1), (150, 102.3)):
            fraction = (x - bore.origin[0]) / bore.length
            radius = bore.radii[0] + fraction * (bore.radii[1] - bore.radii[0])
            self.assertAlmostEqual(2 * radius, diameter)
        self.assertEqual(session.ports[-1], ((150, 0, 0), (1, 0, 0)))

    def test_reducer_rejects_reversed_sizes_and_zero_walls(self):
        for parameters in ({"OD1": 114.3}, {"OD2": 180}, {"ID1": 100}, {"ID2": 154.1}, {"ID1": 168.3}, {"ID2": 114.3}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_REDUCER", **parameters)

    def test_reducer_thin_small_end_keeps_cutter_radii_positive(self):
        body = self.run_component("AT_REDUCER", OD1=100, ID1=90, OD2=1, ID2=0.01, L=0.5).objects[0]
        self.assertTrue(all(r > 0 for r in body.cutters[0].radii))

    def test_elbow_hollow_section_and_quadrant_cutters(self):
        body = self.run_component("AT_ELBOW90").objects[0]
        bore, cut_x, cut_y = body.cutters
        self.assertEqual(body.bend_radius, 152.4)
        self.assertEqual(body.tube_radius, 114.3 / 2)
        self.assertEqual(bore.bend_radius, body.bend_radius)
        self.assertEqual(bore.tube_radius, 102.3 / 2)
        self.assertEqual(cut_x.origin[0] + cut_x.spans[0] / 2, 0)
        self.assertEqual(cut_y.origin[1] + cut_y.spans[1] / 2, 0)
        self.assertEqual(body.origin, (0, -152.4, 0))

    def test_elbow_ports_follow_outward_tangents(self):
        ports = self.run_component("AT_ELBOW90", BR=200).ports
        centre = (0, -200, 0)
        self.assertEqual(ports, [((0, 0, 0), (-1, 0, 0)), ((200, -200, 0), (0, -1, 0))])
        for point, direction in ports:
            radius = tuple(p - c for p, c in zip(point, centre))
            self.assertAlmostEqual(sum(r * d for r, d in zip(radius, direction)), 0)
            self.assertAlmostEqual(math.dist(point, centre), 200)

    def test_elbow_rejects_degenerate_or_self_intersecting_section(self):
        for parameters in ({"ID": 114.3}, {"BR": 114.3 / 2}, {"BR": 20}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_ELBOW90", **parameters)

    def test_blind_flange_is_solid_with_one_reference_point(self):
        for count in (4, 8, 12, 16):
            session = self.run_component("AT_BLIND_FLANGE", N=count)
            body = session.objects[0]
            self.assertEqual(body.bore_radius, 0)
            self.assertEqual(len(body.cutters), count)
            self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0))])

    def test_blind_flange_rejects_invalid_patterns(self):
        for parameters in ({"N": 6}, {"N": 4.5}, {"BCD": 162}, {"HD": 28, "N": 16}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_BLIND_FLANGE", **parameters)

    def test_tee_run_and_branch_meet_at_origin_with_three_ports(self):
        session = self.run_component("AT_TEE")
        body = session.objects[0]
        self.assertEqual((body.radius, body.length), (114.3 / 2, 210))
        self.assert_vector_close(body.origin, (-105, 0, 0))
        self.assert_vector_close(body.axis, (1, 0, 0))
        branch = body.joined[0]
        self.assertEqual((branch.radius, branch.length), (114.3 / 2, 105))
        self.assert_vector_close(branch.origin, (0, 0, 0))
        self.assert_vector_close(branch.axis, (0, 1, 0))
        self.assertEqual(session.ports, [((-105, 0, 0), (-1, 0, 0)),
                                         ((105, 0, 0), (1, 0, 0)),
                                         ((0, 105, 0), (0, 1, 0))])

    def test_tee_bores_open_through_all_three_ends(self):
        body = self.run_component("AT_TEE", OD2=60.3, ID2=52.3, M=95).objects[0]
        run_bore, branch_bore = body.cutters
        self.assertEqual(run_bore.radius, 102.3 / 2)
        self.assertLess(run_bore.origin[0], -105)
        self.assertGreater(run_bore.origin[0] + run_bore.length, 105)
        self.assertEqual(branch_bore.radius, 52.3 / 2)
        self.assert_vector_close(branch_bore.origin, (0, 0, 0))
        self.assert_vector_close(branch_bore.axis, (0, 1, 0))
        self.assertGreater(branch_bore.length, 95)
        self.assertEqual(body.joined[0].radius, 60.3 / 2)

    def test_tee_rejects_oversized_branch_and_short_ends(self):
        for parameters in ({"ID1": 114.3}, {"ID2": 114.3}, {"OD2": 120},
                           {"OD2": 80, "ID2": 70, "ID1": 60},
                           {"C": 114.3 / 2}, {"M": 114.3 / 2}, {"M": 50}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_TEE", **parameters)

    def test_cap_skirt_and_head_join_and_crown_is_at_l(self):
        body = self.run_component("AT_CAP").objects[0]
        head = body.joined[0]
        self.assertIsInstance(head, EllipsoidHeadRecorder)
        self.assertEqual((body.radius, head.radius), (114.3 / 2, 114.3 / 2))
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assert_vector_close(head.axis, (1, 0, 0))
        self.assertAlmostEqual(body.origin[0] + body.length, head.origin[0])
        self.assertAlmostEqual(head.origin[0] + head.height, 64)

    def test_cap_cavity_is_open_and_walls_match_wt(self):
        session = self.run_component("AT_CAP")
        body = session.objects[0]
        cavity = body.cutters[0]
        inner_head = cavity.joined[0]
        self.assertAlmostEqual(body.radius - cavity.radius, 6)
        self.assertEqual(inner_head.radius, cavity.radius)
        self.assertLess(cavity.origin[0], 0)
        self.assertAlmostEqual(cavity.origin[0] + cavity.length, inner_head.origin[0])
        self.assertAlmostEqual(64 - (inner_head.origin[0] + inner_head.height), 6)
        self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0))])

    def test_cap_rejects_no_bore_or_too_short_length(self):
        for parameters in ({"WT": 114.3 / 2}, {"L": 31}, {"OD": 100, "WT": 10, "L": 30}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_CAP", **parameters)
        cavity = self.run_component("AT_CAP", OD=100, WT=10, L=31).objects[0].cutters[0]
        self.assertGreater(cavity.origin[0] + cavity.length, 0)

    def test_coupling_ports_straddle_the_pipe_end_gap(self):
        session = self.run_component("AT_GROOVED_COUPLING")
        self.assertEqual(session.ports, [((28.5, 0, 0), (-1, 0, 0)),
                                         ((31.5, 0, 0), (1, 0, 0))])
        session = self.run_component("AT_GROOVED_COUPLING", HL=80, G=6)
        self.assertEqual([p[0][0] for p in session.ports], [37, 43])

    def test_coupling_housing_bore_fits_pipe_and_passes_through(self):
        body = self.run_component("AT_GROOVED_COUPLING").objects[0]
        bore = body.cutters[0]
        self.assertEqual((body.radius, body.length, body.bore_radius), (75, 60, 0))
        self.assert_vector_close(body.axis, (1, 0, 0))
        self.assertEqual(bore.radius, 114.3 / 2)
        self.assertLess(bore.origin[0], 0)
        self.assertGreater(bore.origin[0] + bore.length, 60)

    def test_coupling_pads_start_on_housing_chord(self):
        body = self.run_component("AT_GROOVED_COUPLING").objects[0]
        self.assertEqual(len(body.joined), 2)
        for pad in body.joined:
            self.assertIsInstance(pad, BoxRecorder)
            length, depth, height = pad.spans
            self.assertEqual((pad.origin[0], length, height), (30, 60, 40))
            inner = abs(pad.origin[1]) - depth / 2
            self.assertAlmostEqual(abs(pad.origin[1]) + depth / 2, 105)
            # The pad's inner top/bottom edges lie on the housing surface.
            self.assertAlmostEqual(math.hypot(inner, height / 2), 75)
        self.assertEqual(sorted(math.copysign(1, p.origin[1]) for p in body.joined), [-1, 1])

    def test_coupling_bolt_holes_cross_pads_outside_housing(self):
        body = self.run_component("AT_GROOVED_COUPLING").objects[0]
        holes = body.cutters[1:]
        self.assertEqual(len(holes), 2)
        for hole in holes:
            self.assert_vector_close(hole.axis, (0, 0, 1))
            self.assertEqual(hole.origin[0], 30)
            self.assertGreater(abs(hole.origin[1]) - hole.radius, 75)
            self.assertLess(abs(hole.origin[1]) + hole.radius, 105)
            self.assertLess(hole.origin[2], -20)
            self.assertGreater(hole.origin[2] + hole.length, 20)

    def test_coupling_rejects_impossible_housing_pads_and_gap(self):
        for parameters in ({"PD": 150}, {"HD": 114.3}, {"PH": 150}, {"BH": 30},
                           {"BH": 65, "P": 80}, {"G": 60}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_GROOVED_COUPLING", **parameters)

    def test_shoe_web_reaches_pipe_centre_and_is_cut_to_pipe(self):
        session = self.run_component("AT_PIPE_SHOE")
        web = session.objects[0]
        self.assertIsInstance(web, BoxRecorder)
        self.assertEqual(web.spans, (200, 10, 100))
        self.assertEqual(web.origin[2] + web.spans[2] / 2, 0)
        self.assertEqual(web.origin[2] - web.spans[2] / 2, -100)
        pipe = web.cutters[0]
        self.assertEqual(pipe.radius, 114.3 / 2)
        self.assert_vector_close(pipe.axis, (1, 0, 0))
        self.assertLess(pipe.origin[0], -100)
        self.assertGreater(pipe.origin[0] + pipe.length, 100)
        self.assertEqual(session.ports, [((0, 0, 0), (-1, 0, 0))])

    def test_shoe_base_plate_sits_below_pipe_at_depth_h(self):
        for size, depth in ((114.3, 100), (60.3, 80)):
            with self.subTest(pipe=size):
                web = self.run_component("AT_PIPE_SHOE", PD=size, H=depth).objects[0]
                base = web.joined[0]
                self.assertEqual(base.spans, (200, 120, 10))
                self.assertEqual(base.origin[2] - base.spans[2] / 2, -depth)
                self.assertLess(base.origin[2] + base.spans[2] / 2, -size / 2)

    def test_shoe_rejects_base_in_pipe_and_oversized_web(self):
        for parameters in ({"PD": 100, "T": 10, "H": 60}, {"H": 60}, {"W": 10},
                           {"T": 120, "W": 130, "H": 300}):
            with self.subTest(parameters=parameters):
                self.assert_rejected_without_geometry("AT_PIPE_SHOE", **parameters)

    def test_new_components_erase_all_temporary_objects(self):
        for name in COMPONENT_NAMES[3:]:
            session = self.run_component(name)
            with self.subTest(component=name):
                self.assertFalse(session.objects[0].erased)
                self.assertTrue(all(obj.erased for obj in session.objects[1:]))


if __name__ == "__main__":
    unittest.main()
