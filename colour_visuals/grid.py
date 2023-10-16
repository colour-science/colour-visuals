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

from colour.hints import ArrayLike
from colour.geometry import primitive_grid
from colour.plotting import CONSTANTS_COLOUR_STYLE

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    append_alpha_channel,
    conform_primitive_dtype,
    as_contiguous_array,
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
    Create a *RGB* 3D scatter visual.
    """

    def __init__(
        self,
        size: int = 20,
        major_grid_color: ArrayLike = np.array([0.5, 0.5, 0.5]),
        minor_grid_color: ArrayLike = np.array([0.25, 0.25, 0.25]),
        major_tick_labels=True,
        major_tick_label_color: ArrayLike = np.array([0.75, 0.75, 0.75]),
        minor_tick_labels=True,
        minor_tick_label_color: ArrayLike = np.array([0.5, 0.5, 0.5]),
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
                    append_alpha_channel(
                        np.tile(major_grid_color, (positions.shape[0], 1)), 1
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
                    append_alpha_channel(
                        np.tile(minor_grid_color, (positions.shape[0], 1)), 1
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

        axes_colors = np.array(
            [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )

        self._axes_helper = gfx.Line(
            gfx.Geometry(positions=axes_positions, colors=axes_colors),
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
                    gfx.TextMaterial(color=major_tick_label_color),
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
                    gfx.TextMaterial(color=major_tick_label_color),
                )
                y_text.local.position = np.array([0, i, 1e-3])
                self.add(y_text)
                self._ticks_major_y.append(y_text)

        if minor_tick_labels:
            self._ticks_minor_x, self._ticks_minor_y = [], []
            for i in np.arange(-size // 2, size // 2 + 0.1, 0.1):
                if np.around(i, 0) == np.around(i, 1):
                    continue

                i = np.around(i, 1)

                x_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} " if i == 0 else str(i),
                        font_size=CONSTANTS_COLOUR_STYLE.font_size.small,
                        screen_space=True,
                        anchor="Top-Right" if i == 0 else "Top-Center",
                    ),
                    gfx.TextMaterial(color=minor_tick_label_color),
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
                    gfx.TextMaterial(color=minor_tick_label_color),
                )
                y_text.local.position = np.array([0, i, 1e-3])
                self.add(y_text)
                self._ticks_minor_y.append(y_text)


if __name__ == "__main__":
    from pygfx import (
        Background,
        Display,
        BackgroundMaterial,
        Scene,
    )

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualGrid()
    scene.add(visual_1)

    gfx.show(scene, up=np.array([0, 0, 1]))
