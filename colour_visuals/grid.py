# !/usr/bin/env python
"""
Grid Visuals
============

Defines the grid visuals:

-   :class:`colour_visuals.VisualGrid`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.geometry import primitive_grid
from colour.hints import ArrayLike
from colour.plotting import CONSTANTS_COLOUR_STYLE

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    append_channel,
    as_contiguous_array,
    conform_primitive_dtype,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["VisualGrid"]


class VisualGrid(gfx.Group):
    """
    Create a 3D grid.

    Parameters
    ----------
    size
        Size of the grid.
    major_grid_colours
        Colours of the major grid lines.
    minor_grid_colours
        Colours of the minor grid lines.
    major_tick_labels
        Whether to draw the major tick labels.
    major_tick_label_colours
        Colours of the major tick labels.
    minor_tick_labels
        Whether to draw the minor tick labels.
    minor_tick_label_colours
        Colours of the minor tick labels.

    Examples
    --------
    >>> import os
    >>> from colour.utilities import suppress_stdout
    >>> from wgpu.gui.auto import WgpuCanvas
    >>> with suppress_stdout():
    ...     canvas = WgpuCanvas(size=(960, 540))
    ...     scene = gfx.Scene()
    ...     scene.add(
    ...         gfx.Background(
    ...             None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...         )
    ...     )
    ...     visual = VisualGrid()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualGrid.png
        :align: center
        :alt: visual-grid
    """

    def __init__(
        self,
        size: int = 20,
        major_grid_colours: ArrayLike = np.array([0.5, 0.5, 0.5]),
        minor_grid_colours: ArrayLike = np.array([0.25, 0.25, 0.25]),
        major_tick_labels=True,
        major_tick_label_colours: ArrayLike = np.array([0.75, 0.75, 0.75]),
        minor_tick_labels=True,
        minor_tick_label_colours: ArrayLike = np.array([0.5, 0.5, 0.5]),
    ):
        super().__init__()

        size = int(size)

        vertices, faces, outline = conform_primitive_dtype(
            primitive_grid(
                width_segments=size,
                height_segments=size,
            )
        )
        positions = vertices["position"]

        self._grid_major = gfx.Mesh(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                indices=outline[..., 1].reshape([-1, 4]),
                colors=as_contiguous_array(
                    append_channel(
                        np.tile(major_grid_colours, (positions.shape[0], 1)), 1
                    )
                ),
            ),
            gfx.MeshBasicMaterial(color_mode="vertex", wireframe=True),
        )
        self._grid_major.local.scale = np.array([size, size, 1])
        self.add(self._grid_major)

        vertices, faces, outline = conform_primitive_dtype(
            primitive_grid(
                width_segments=size * 10,
                height_segments=size * 10,
            )
        )
        positions = vertices["position"]

        self._grid_minor = gfx.Mesh(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                indices=outline[..., 1].reshape([-1, 4]),
                colors=as_contiguous_array(
                    append_channel(
                        np.tile(minor_grid_colours, (positions.shape[0], 1)), 1
                    )
                ),
            ),
            gfx.MeshBasicMaterial(color_mode="vertex", wireframe=True),
        )
        self._grid_minor.local.position = np.array([0, 0, -1e-3])
        self._grid_minor.local.scale = np.array([size, size, 1])
        self.add(self._grid_minor)

        axes_positions = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0, 0, 0],
                [0, 1, 0],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )
        axes_positions *= size / 2

        axes_colours = np.array(
            [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )

        self._axes_helper = gfx.Line(
            gfx.Geometry(positions=axes_positions, colors=axes_colours),
            gfx.LineSegmentMaterial(color_mode="vertex", thickness=2),
        )
        self.add(self._axes_helper)

        if major_tick_labels:
            self._ticks_major_x, self._ticks_major_y = [], []
            for i in np.arange(-size // 2, size // 2 + 1, 1):
                x_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} " if i == 0 else str(i),
                        font_size=CONSTANTS_COLOUR_STYLE.font_size.medium,
                        screen_space=True,
                        anchor="Top-Right" if i == 0 else "Top-Center",
                    ),
                    gfx.TextMaterial(
                        color=major_tick_label_colours  # pyright: ignore
                    ),
                )
                x_text.local.position = np.array([i, 0, 1e-3])
                self.add(x_text)
                self._ticks_major_x.append(x_text)

                if i == 0:
                    continue

                y_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} ",
                        font_size=CONSTANTS_COLOUR_STYLE.font_size.medium,
                        screen_space=True,
                        anchor="Center-Right",
                    ),
                    gfx.TextMaterial(
                        color=major_tick_label_colours  # pyright: ignore
                    ),
                )
                y_text.local.position = np.array([0, i, 1e-3])
                self.add(y_text)
                self._ticks_major_y.append(y_text)

        if minor_tick_labels:
            self._ticks_minor_x, self._ticks_minor_y = [], []
            for i in np.arange(-size // 2, size // 2 + 0.1, 0.1):
                if np.around(i, 0) == np.around(i, 1):
                    continue

                i = np.around(i, 1)  # noqa: PLW2901

                x_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} " if i == 0 else str(i),
                        font_size=CONSTANTS_COLOUR_STYLE.font_size.small,
                        screen_space=True,
                        anchor="Top-Right" if i == 0 else "Top-Center",
                    ),
                    gfx.TextMaterial(
                        color=minor_tick_label_colours  # pyright: ignore
                    ),
                )
                x_text.local.position = np.array([i, 0, 1e-3])
                self.add(x_text)
                self._ticks_minor_x.append(x_text)

                if i == 0:
                    continue

                y_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} ",
                        font_size=CONSTANTS_COLOUR_STYLE.font_size.small,
                        screen_space=True,
                        anchor="Center-Right",
                    ),
                    gfx.TextMaterial(
                        color=minor_tick_label_colours  # pyright: ignore
                    ),
                )
                y_text.local.position = np.array([0, i, 1e-3])
                self.add(y_text)
                self._ticks_minor_y.append(y_text)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(
            None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
        )
    )

    visual_1 = VisualGrid()
    scene.add(visual_1)

    gfx.show(scene, up=np.array([0, 0, 1]))
