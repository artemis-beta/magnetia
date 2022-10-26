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
import matplotlib.pyplot as plt
import matplotlib.patches as mpp
import typing
import scipy.constants as sp_const
import magnetia.types as mg_types

CHARGE_VISUAL_RADIUS: int = 0.4


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


def electric_field_lines(
    electric_charges: typing.List[PointCharge],
    n_lines_per_charge: int = 20,
    length: int = 20,
) -> None:
    """Plot field lines for a given set of electric charges

    Parameters
    ----------
    electric_charges : typing.List[PointCharge]
        list of charges defining the electric field
    n_lines_per_charge : int, optional
        number of lines to plot per charge, by default 20
    length : int, optional
        length of each electric field line, by default 20
    """

    # initialise a set of axes on which to plot the charges and field lines
    _, axes = plt.subplots()
    axes.set_aspect(1)

    for electric_charge in electric_charges:
        # Only plot field lines from positive charges
        if electric_charge.charge > 0:
            continue

        # Create a field line from each starting point, these being spaced
        # evenly across the angle 2pi
        for line_start in get_line_start_points(electric_charge, n_lines_per_charge):
            _field_line: typing.List[mg_types.Float64_3DVector] = numpy.array(
                [line_start]
            )
            for _ in range(length):

                # Obtain the force at the given point and then find the unit vector
                _force_vector: mg_types.Float64_3DVector = coulomb_force(
                    electric_charges, _field_line[-1]
                )
                _unit_vec: mg_types.Float64_3DVector = (
                    _force_vector / numpy.linalg.norm(_force_vector)
                )

                # Append the next point in the field line taken to be the current
                # point plus an interval of the unit vector
                _field_line = numpy.append(
                    _field_line,
                    (_field_line[-1] + _unit_vec)[numpy.newaxis, ...],
                    axis=0,
                )

            axes.plot(_field_line[:, 0], _field_line[:, 1], color="k")

    axes.set_xlabel("x")
    axes.set_ylabel("y")

    # Plot the charges displaying also their magnitude
    for charge in electric_charges:
        axes.add_patch(
            mpp.Circle(
                (charge.position[0], charge.position[1]),
                radius=CHARGE_VISUAL_RADIUS,
                color="r",
            )
        )

        axes.text(
            charge.position[0],
            charge.position[1],
            charge.charge,
            color="k",
            verticalalignment="bottom",
            horizontalalignment="left",
        )

    axes.relim()
    axes.autoscale_view()
    plt.show()


if __name__ in "__main__":
    _charges: typing.List[PointCharge] = [
        PointCharge(numpy.array([-10, 0, 0]), 1),
        PointCharge(numpy.array([5, 0, 0]), -1),
        PointCharge(numpy.array([3, 10, 0]), -1),
        PointCharge(numpy.array([0, 8, 0]), 1),
    ]
    electric_field_lines(_charges)
