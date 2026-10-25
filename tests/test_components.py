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


class SessionRecorder:
    def __init__(self):
        self.cylinders = []
        self.ports = []
        self.events = []

    def setPoint(self, position, direction):
        self.ports.append((tuple(position), tuple(direction)))


class CylinderRecorder:
    """A record of primitive arguments, not a simulated solid."""

    def __init__(self, session, R, H, O):
        self.session = session
        self.radius = R
        self.length = H
        self.bore_radius = O
        self.origin = (0.0, 0.0, 0.0)
        self.axis = (0.0, 0.0, 1.0)
        self.cutters = []
        self.erased = False
        session.cylinders.append(self)

    def rotateY(self, degrees):
        radians = math.radians(degrees)
        c, s = math.cos(radians), math.sin(radians)

        def rotate(vector):
            x, y, z = vector
            return (c * x + s * z, y, -s * x + c * z)

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


def load_component(name):
    """Execute one real source file with isolated recording API replacements."""
    package = types.ModuleType("varmain")
    package.__path__ = []
    primitives = types.ModuleType("varmain.primitiv")
    primitives.CYLINDER = CylinderRecorder
    custom = types.ModuleType("varmain.custom")
    custom.LENGTH, custom.ENUM = "LENGTH", "ENUM"

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
            for name in ("AT_CYLINDER", "AT_SPACER", "AT_FLANGE")
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
        self.assertEqual(session.cylinders, [])
        self.assertEqual(session.ports, [])

    def test_each_script_has_matching_entry_point_and_dimension_metadata(self):
        self.assertEqual({p.stem for p in SCRIPT_DIR.glob("*.py")}, set(self.functions))
        for name, function in self.functions.items():
            with self.subTest(component=name):
                self.assertEqual(function.__name__, name)
                dimensions = set(inspect.signature(function).parameters) - {"s", "kw"}
                declared = set()
                for metadata in function.parameters:
                    declared.update(k for k, v in metadata.items() if v in ("LENGTH", "ENUM"))
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
            for dimension in inspect.signature(function).parameters:
                if dimension in ("s", "kw", "N"):
                    continue
                for value in (0, -1):
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
            dimension = "D" if name == "AT_CYLINDER" else "OD"
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


if __name__ == "__main__":
    unittest.main()
