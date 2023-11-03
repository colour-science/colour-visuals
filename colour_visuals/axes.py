# !/usr/bin/env python
"""
Axes Visuals
============

Defines the axes visuals:

-   :class:`colour_visuals.VisualAxes`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.hints import LiteralColourspaceModel
from colour.models import COLOURSPACE_MODELS_AXIS_LABELS
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    colourspace_model_axis_reorder,
)
from colour.utilities import as_int_array

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    unlatexify,
)
from colour_visuals.visual import (
    MixinPropertyModel,
    MixinPropertySize,
    Visual,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["VisualAxes"]


class VisualAxes(MixinPropertyModel, MixinPropertySize, Visual):
    """
    Create an axes visual.

    Parameters
    ----------
    model
        Colourspace model, see :attr:`colour.COLOURSPACE_MODELS` attribute for
        the list of supported colourspace models.
    size
        Size of the axes.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualAxes.model`
    -   :attr:`~colour_visuals.VisualAxes.size`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualAxes.__init__`
    -   :meth:`~colour_visuals.VisualAxes.update`

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
    ...     visual = VisualAxes("CIE Lab")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualAxes.png
        :align: center
        :alt: visual-grid
    """

    def __init__(
        self,
        model: LiteralColourspaceModel | str = "CIE xyY",
        size: int = 1,
    ):
        super().__init__()

        self._axes_helper = None
        self._x_text = None
        self._y_text = None
        self._z_text = None

        with self.block_update():
            self.model = model
            self.size = size

        self.update()

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        axes_positions = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0],
                [0, 0, 1],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )
        axes_positions *= int(self._size)

        axes_colours = np.array(
            [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )

        self._axes_helper = gfx.Line(
            gfx.Geometry(positions=axes_positions, colors=axes_colours),
            gfx.LineSegmentMaterial(color_mode="vertex", thickness=2),
        )
        self.add(self._axes_helper)

        labels = np.array(COLOURSPACE_MODELS_AXIS_LABELS[self._model])[
            as_int_array(
                colourspace_model_axis_reorder([0, 1, 2], self._model)
            )
        ]

        self._x_text = gfx.Text(
            gfx.TextGeometry(
                unlatexify(labels[0]),
                font_size=CONSTANTS_COLOUR_STYLE.font.size
                * CONSTANTS_COLOUR_STYLE.font.scaling.xx_large,
                screen_space=True,
                anchor="Middle-Center",
            ),
            gfx.TextMaterial(color=np.array([1, 0, 0])),
        )
        self._x_text.local.position = np.array([1 * self._size * 1.05, 0, 0])
        self.add(self._x_text)

        self._y_text = gfx.Text(
            gfx.TextGeometry(
                unlatexify(labels[1]),
                font_size=CONSTANTS_COLOUR_STYLE.font.size
                * CONSTANTS_COLOUR_STYLE.font.scaling.xx_large,
                screen_space=True,
                anchor="Middle-Center",
            ),
            gfx.TextMaterial(color=np.array([0, 1, 0])),
        )
        self._y_text.local.position = np.array([0, 1 * self._size * 1.05, 0])
        self.add(self._y_text)

        self._z_text = gfx.Text(
            gfx.TextGeometry(
                unlatexify(labels[2]),
                font_size=CONSTANTS_COLOUR_STYLE.font.size
                * CONSTANTS_COLOUR_STYLE.font.scaling.xx_large,
                screen_space=True,
                anchor="Middle-Center",
            ),
            gfx.TextMaterial(color=np.array([0, 0, 1])),
        )
        self._z_text.local.position = np.array([0, 0, 1 * self._size * 1.05])
        self.add(self._z_text)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(
            None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
        )
    )

    visual_1 = VisualAxes(model="CIE Lab")
    scene.add(visual_1)

    gfx.show(scene, up=np.array([0, 0, 1]))
