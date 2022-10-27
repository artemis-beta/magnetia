"""
Electric Field Line Simulation
==============================

A simple simulation to plot the electric field lines created between one or more point charges.

The lines are plotted by calculating coulomb force at various points around each charge and then
propagating outward following the vector.

"""

__author__ = "Kristian Zarebski"
__date__ = "2022-10-25"
__license__ = "MIT"

import dataclasses
import numpy
import typing
import scipy.constants as sp_const
import magnetia.types as mg_types

CHARGE_VISUAL_RADIUS: float = 0.2


@dataclasses.dataclass
class PointCharge:
    """Simple data class holding the properties of a point charge"""

    position: mg_types.Float64_3DVector
    charge: numpy.float64


def coulomb_force(
    electric_charges: typing.List[PointCharge],
    field_position: mg_types.Float64_3DVector,
) -> mg_types.Float64_3DVector:
    """
    Calculate the Coulomb Force due to a set of charges at a position expressed in cartesian coordinates.

    Parameters
    ----------
    electric_charges : typing.List[PointCharge]
        list of charges for which the total force is to be calculated
    field_position : mg_types.Float64_3DVector
        position at which to calculate the force

    Returns
    -------
    mg_types.Float64_3DVector
        Coulomb Force expressed as a vector
    """
    k = numpy.power(4 * sp_const.pi * sp_const.epsilon_0, -1)
    _coulomb_force_vec: mg_types.Float64_3DVector = numpy.zeros(3)

    for charge in electric_charges:
        _distance_vec: mg_types.Float64_3DVector = charge.position - field_position
        if numpy.linalg.norm(_distance_vec) == 0:
            continue
        _unit_vec: mg_types.Float64_3DVector = _distance_vec / numpy.linalg.norm(
            _distance_vec
        )
        _coulomb_force_vec += (
            _unit_vec * k * charge.charge / numpy.dot(_distance_vec, _distance_vec)
        )

    return _coulomb_force_vec


def get_line_start_points(
    electric_charge: PointCharge, n_lines: int
) -> typing.List[mg_types.Float64_3DVector]:
    """Create a list of field line start points for a given point charge.

    Parameters
    ----------
    electric_charge : PointCharge
        electric charge from which to draw field lines from
    n_lines : int
        number of lines to plot for the given charge

    Returns
    -------
    typing.List[mg_types.Float64_3DVector]
        list of cartesian coordinates marking the start positions
    """
    _angle_interval: numpy.float64 = 2 * sp_const.pi / n_lines
    _line_start_points = [
        numpy.array(
            [
                electric_charge.position[0]
                + CHARGE_VISUAL_RADIUS * numpy.sin(i * _angle_interval),
                electric_charge.position[1]
                + CHARGE_VISUAL_RADIUS * numpy.cos(i * _angle_interval),
                0,
            ]
        )
        for i in range(n_lines // 2)
    ]

    _line_start_points += [
        numpy.array(
            [
                electric_charge.position[0]
                - CHARGE_VISUAL_RADIUS * numpy.sin(i * _angle_interval),
                electric_charge.position[1]
                - CHARGE_VISUAL_RADIUS * numpy.cos(i * _angle_interval),
                0,
            ]
        )
        for i in range(n_lines // 2)
    ]

    return _line_start_points


def angle_between_vectors(vector_1: mg_types.Float64_3DVector, vector_2: mg_types.Float64_3DVector) -> numpy.float64:
    return numpy.arccos(numpy.inner(vector_1, vector_2) / (numpy.linalg.norm(vector_1) * numpy.linalg.norm(vector_2)))

def check_if_crosses_charge(
    electric_charges: typing.List[PointCharge],
    old_coordinate: mg_types.Float64_3DVector,
    new_coordinate: mg_types.Float64_3DVector,
    tolerance: numpy.float64 = 5e-2,
) -> bool:
    for electric_charge in electric_charges:
        _new_line_vec: mg_types.Float64_3DVector = new_coordinate - old_coordinate
        _to_charg_vec: mg_types.Float64_3DVector = electric_charge.position - old_coordinate

        _angle: numpy.float64 = angle_between_vectors(_new_line_vec, _to_charg_vec)

        if numpy.any(numpy.isnan(_angle)) or _angle <= tolerance:
            return True
    return False


def create_field_line(
    electric_charges: typing.List[PointCharge],
    line_start: mg_types.Float64_3DVector,
    length: int = 100,
    points_per_unit_vector: int=1,
    approach_tolerance: float=1E-1
) -> mg_types.Float64_3DVectorArray:
    _field_line: typing.List[mg_types.Float64_3DVector] = numpy.array([line_start])

    for i in range(length * points_per_unit_vector):

        # Obtain the force at the given point and then find the unit vector
        _force_vector: mg_types.Float64_3DVector = coulomb_force(
            electric_charges, _field_line[-1]
        )
        _unit_vec: mg_types.Float64_3DVector = _force_vector / numpy.linalg.norm(
            _force_vector
        )

        _new_coord: mg_types.Float64_3DVector = (_field_line[-1] + (1 / points_per_unit_vector) * _unit_vec)[
            numpy.newaxis, ...
        ]

        if check_if_crosses_charge(
            electric_charges, _field_line[-1], _new_coord, approach_tolerance
        ) and i > 1:
            return _field_line

        # Append the next point in the field line taken to be the current
        # point plus an interval of the unit vector
        _field_line = numpy.append(
            _field_line,
            _new_coord,
            axis=0,
        )

    return _field_line


def field_lines_from_charges(
    electric_charges: PointCharge, n_lines_per_charge: int = 20, length: int = 20, points_per_unit_vector: int=1, approach_tolerance: float=1E-1
) -> typing.List[mg_types.Float64_3DVectorArray]:
    _field_lines: typing.List[mg_types.Float64_3DVectorArray] = []

    for electric_charge in electric_charges:
        # Only plot field lines from positive charges
        if electric_charge.charge > 0:
            continue

        # Create a field line from each starting point, these being spaced
        # evenly across the angle 2pi
        for line_start in get_line_start_points(electric_charge, n_lines_per_charge):
            _field_lines.append(create_field_line(electric_charges, line_start, length, points_per_unit_vector, approach_tolerance))

    return _field_lines
