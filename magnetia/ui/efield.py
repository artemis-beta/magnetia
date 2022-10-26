"""
Bokeh Server

Launches a Bokeh Server application for demonstrating the effect of charge position
on electric field lines. The app contains sliders for adjusting the x, y coordinates
of charges
"""

__author__ = "Kristian Zarebski"
__date__ = "2022-10-26"
__license__ = "MIT"

import typing
import numpy
from bokeh.layouts import column
import bokeh.models
from bokeh.plotting import figure, curdoc

import magnetia.physics.field_lines as mg_fl

N_CHARGES: int = 3
N_FIELD_LINES_PER_CHARGE: int = 20
FIELD_LINE_LENGTH: int = 10


def launch_application(*args) -> None:
    """Launches the Bokeh Application

    Creates a figure and plot objects to be displayed, and assembles slider widgets for adjusting the
    X, Y coordinates of the charges shown
    """
    # Create a new Bokeh Figure
    _figure = figure(x_range=(-15, 15), y_range=(-15, 15))

    # Retrieve the coordinates of all electric charges as a single dictionary
    # this can then be used to plot the charges
    def get_plot_coordinates(
        charges: typing.List[mg_fl.PointCharge],
    ) -> typing.Dict[str, typing.List[int]]:
        return {
            "x": [q.position[0] for q in charges],
            "y": [q.position[1] for q in charges],
        }

    # Initialise the charge list spacing them evenly to start
    _charges: typing.List[mg_fl.PointCharge] = [
        mg_fl.PointCharge(
            numpy.array([-10 + i * 2, -10 + i * 2, 0]), -1 if i % 2 == 0 else 1
        )
        for i in range(N_CHARGES)
    ]

    # Retrieve the coordinates for plotting the initial state
    _charge_coords: typing.Dict[str, typing.List[int]] = get_plot_coordinates(_charges)

    # Plot the charges as a scatter graph
    _charge_args = {"size": 15, "fill_color": "red"} | _charge_coords
    _charge_plot = _figure.scatter(**_charge_args)

    # Create the field line plot objects
    _field_line_plots = [
        _figure.line() for _ in range(N_FIELD_LINES_PER_CHARGE * N_CHARGES)
    ]

    # Retruevt the data sources so they can be updated within the callback
    _fl_data_sources = [lp.data_source for lp in _field_line_plots]

    # Create the initial field lines and plot these
    _field_lines = mg_fl.field_lines_from_charges(
        _charges, N_FIELD_LINES_PER_CHARGE, FIELD_LINE_LENGTH
    )

    for i, field_line in enumerate(_field_lines):
        _fl_data_sources[i].data = {"x": field_line[:, 0], "y": field_line[:, 1]}

    # Create the slider widgets for adjusting the X, Y coordinates
    # of each electric charge independently
    _sliders: typing.List[bokeh.models.Slider] = [
        bokeh.models.Slider(
            start=-10,
            end=10,
            value=_charge_coords["x" if i % 2 == 0 else "y"][i // 2],
            step=1,
            title=f"Q{i//2} {'x' if i % 2 == 0 else 'y'}",
        )
        for i in range(N_CHARGES * 2)
    ]

    # Create the callback function for replotting after charge position has been updated
    def _gen_callback(index: int) -> typing.Callable:
        def _slider_callback(_, new, *args):
            _charges[index // 2].position[index % 2] = new
            _field_lines = mg_fl.field_lines_from_charges(
                _charges, N_FIELD_LINES_PER_CHARGE, FIELD_LINE_LENGTH
            )

            for i, field_line in enumerate(_field_lines):
                _fl_data_sources[i].data = {
                    "x": field_line[:, 0],
                    "y": field_line[:, 1],
                }
            _charge_plot.data_source.data = get_plot_coordinates(_charges)

        return _slider_callback

    # Assign the sliders to the update of position for each of the charges
    for i, slider in enumerate(_sliders):
        slider.on_change("value", _gen_callback(i))

    # Add all objects to the application
    curdoc().add_root(column(*_sliders, _figure))

launch_application()
