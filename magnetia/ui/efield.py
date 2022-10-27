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
from bokeh.layouts import column, row
import bokeh.models
from bokeh.plotting import figure, curdoc

import magnetia.physics.field_lines as mg_fl

N_CHARGES_INTERVAL: typing.Tuple[int, int] = (2, 8, 1)
FIELD_LINES_PER_CHARGE_INTERVAL: typing.Tuple[int, int] = (6, 40, 2)
N_POINTS_PER_UNIT_VECTOR_INTERVAL: typing.Tuple[int, int] = (1, 10, 1)
FIELD_LINE_LENGTH_INTERVAL: typing.Tuple[int, int] = (10, 100, 10)
APPROACH_TOLERANCE_INTERVAL: typing.Tuple[int, int, int] = (1, 10, 1)


application_data: typing.Dict[str, typing.Any] = {
    "charges": [
        mg_fl.PointCharge(
            numpy.array([-10 + i * 2, -10 + i * 2, 0]), -1 if i % 2 == 0 else 1
        )
        for i in range(N_CHARGES_INTERVAL[1])
    ],
    "charge_position_sliders": {
        "x": [
            bokeh.models.Slider(
                start=-10,
                end=10,
                value=-10 + i * 2,
                step=1,
                title=f"Q{i}x",
            )
            for i in range(N_CHARGES_INTERVAL[1])
        ],
        "y": [
            bokeh.models.Slider(
                start=-10,
                end=10,
                value=-10 + i * 2,
                step=1,
                title=f"Q{i}y",
            )
            for i in range(N_CHARGES_INTERVAL[1])
        ],
    },
    "n_charges_slider": bokeh.models.Slider(
        start=N_CHARGES_INTERVAL[0],
        end=N_CHARGES_INTERVAL[1],
        value=N_CHARGES_INTERVAL[0] + N_CHARGES_INTERVAL[2],
        step=N_CHARGES_INTERVAL[2],
        title="Number of Charges",
    ),
    "n_points_per_unit_vector_slider": bokeh.models.Slider(
        start=N_POINTS_PER_UNIT_VECTOR_INTERVAL[0],
        end=N_POINTS_PER_UNIT_VECTOR_INTERVAL[1],
        value=N_POINTS_PER_UNIT_VECTOR_INTERVAL[0]
        + N_POINTS_PER_UNIT_VECTOR_INTERVAL[2],
        step=N_POINTS_PER_UNIT_VECTOR_INTERVAL[2],
        title="Resolution",
    ),
    "field_lines_per_charge_slider": bokeh.models.Slider(
        start=FIELD_LINES_PER_CHARGE_INTERVAL[0],
        end=FIELD_LINES_PER_CHARGE_INTERVAL[1],
        value=FIELD_LINES_PER_CHARGE_INTERVAL[0] + FIELD_LINES_PER_CHARGE_INTERVAL[2],
        step=FIELD_LINES_PER_CHARGE_INTERVAL[2],
        title="Number of Field Lines per Charge",
    ),
    "field_line_length_slider": bokeh.models.Slider(
        start=FIELD_LINE_LENGTH_INTERVAL[0],
        end=FIELD_LINE_LENGTH_INTERVAL[1],
        value=FIELD_LINE_LENGTH_INTERVAL[0] + FIELD_LINE_LENGTH_INTERVAL[2],
        step=FIELD_LINE_LENGTH_INTERVAL[2],
        title="Field Line Length",
    ),
    "approach_tolerance_slider": bokeh.models.Slider(
        start=APPROACH_TOLERANCE_INTERVAL[0],
        end=APPROACH_TOLERANCE_INTERVAL[1],
        value=APPROACH_TOLERANCE_INTERVAL[0] + APPROACH_TOLERANCE_INTERVAL[2],
        step=APPROACH_TOLERANCE_INTERVAL[2],
        title="Field Line to Charge Approach Tolerance",
    ),
    "n_charges": N_CHARGES_INTERVAL[0] + N_CHARGES_INTERVAL[2],
    "n_points_per_unit_vector": N_POINTS_PER_UNIT_VECTOR_INTERVAL[0]
    + N_POINTS_PER_UNIT_VECTOR_INTERVAL[2],
    "field_lines_per_charge": FIELD_LINES_PER_CHARGE_INTERVAL[0]
    + FIELD_LINES_PER_CHARGE_INTERVAL[2],
    "field_line_length": FIELD_LINE_LENGTH_INTERVAL[0] + FIELD_LINE_LENGTH_INTERVAL[2],
    "approach_tolerance": APPROACH_TOLERANCE_INTERVAL[0] + APPROACH_TOLERANCE_INTERVAL[2],
}

# Create a new Bokeh Figure
_figure = figure(x_range=(-15, 15), y_range=(-15, 15), title="Electric Field from Point Charges")
_figure.xaxis.axis_label = "x"
_figure.yaxis.axis_label = "y"
_charge_plots = {
    "+": _figure.scatter(x=[], y=[], fill_color="red", size=15),
    "-": _figure.scatter(x=[], y=[], fill_color="blue", size=15),
}

# Create the field line plot objects
_field_line_plots = [
    _figure.line()
    for _ in range(FIELD_LINES_PER_CHARGE_INTERVAL[1] * N_CHARGES_INTERVAL[1])
]


def update_plot() -> None:
    application_data["charge_plot_data"] = {
        "+": {"x": [], "y": []},
        "-": {"x": [], "y": []},
    }

    for charge in application_data["charges"][: application_data["n_charges"]]:
        _key: str = "+" if charge.charge > 0 else "-"
        application_data["charge_plot_data"][_key]["x"].append(charge.position[0])
        application_data["charge_plot_data"][_key]["y"].append(charge.position[1])

    # Create the initial field lines and plot these
    _field_lines = mg_fl.field_lines_from_charges(
        application_data["charges"][: application_data["n_charges"]],
        application_data["field_lines_per_charge"],
        application_data["field_line_length"],
        application_data["n_points_per_unit_vector"],
        pow(10, -application_data["approach_tolerance"]),
    )

    application_data["field_line_plot_data"] = [
        {"x": f[:, 0], "y": f[:, 1]} for f in _field_lines
    ]
    application_data["field_line_plot_data"] += [
        {"x": [], "y": []} for _ in range(len(_field_line_plots) - len(_field_lines))
    ]

    for i, field_line in enumerate(application_data["field_line_plot_data"]):
        _field_line_plots[i].data_source.data = field_line

    # Plot the charges as a scatter graph
    for polarity in application_data["charge_plot_data"].keys():
        _charge_plots[polarity].data_source.data = application_data["charge_plot_data"][
            polarity
        ]


def gen_charge_position_callback(
    charge_index: int, vector_index: int
) -> typing.Callable:
    def charge_position_callback(_, new, *args) -> None:
        application_data["charges"][charge_index].position[vector_index] = new
        update_plot()

    return charge_position_callback


def n_charges_callback(_, new, *args) -> None:
    for i, _ in enumerate(application_data["charges"]):
        application_data["charge_position_sliders"]["x"][i].visible = i < new
        application_data["charge_position_sliders"]["y"][i].visible = i < new
    application_data["n_charges"] = new
    update_plot()


def gen_config_callback(value_label: str) -> typing.Callable:
    def config_callback(_, new, *args) -> None:
        application_data[value_label] = new
        update_plot()

    return config_callback


def res_callback(_, new, *args) -> None:
    application_data["resolution"] = new
    update_plot()


# Assign the sliders to the update of position for each of the charges
for i, slider in enumerate(application_data["charge_position_sliders"]["x"]):
    slider.on_change("value", gen_charge_position_callback(i, 0))

for i, slider in enumerate(application_data["charge_position_sliders"]["y"]):
    slider.on_change("value", gen_charge_position_callback(i, 1))

for configurable in {
    "n_points_per_unit_vector",
    "field_lines_per_charge",
    "field_line_length",
    "approach_tolerance"
}:
    application_data[f"{configurable}_slider"].on_change(
        "value", gen_config_callback(configurable)
    )


application_data["n_charges_slider"].on_change("value", n_charges_callback)

update_plot()

_positions_slider_arrangement = []

for i, _ in enumerate(application_data["charge_position_sliders"]["x"]):
    _positions_slider_arrangement.append(application_data["charge_position_sliders"]["x"][i])
    _positions_slider_arrangement.append(application_data["charge_position_sliders"]["y"][i])

# Add all objects to the application
curdoc().add_root(
    row(
        column(
            *_positions_slider_arrangement
        ),
        column(
            application_data["n_charges_slider"],
            application_data["field_line_length_slider"],
            application_data["field_lines_per_charge_slider"],
            application_data["n_points_per_unit_vector_slider"],
            application_data["approach_tolerance_slider"],
        ),
        _figure,
    )
)
