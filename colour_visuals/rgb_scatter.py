# !/usr/bin/env python
"""
RGB Scatter Visuals
===================

Defines the *RGB* scatter visuals:

-   :class:`colour_visuals.VisualRGBScatter3D`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour import RGB_to_XYZ
from colour.constants import EPSILON
from colour.hints import ArrayLike, Type
from colour.plotting import (
    colourspace_model_axis_reorder,
    filter_RGB_colourspaces,
)
from colour.utilities import as_float_array, first_item

from colour_visuals.common import (
    append_alpha_channel,
    as_contiguous_array,
    XYZ_to_colourspace_model,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["VisualRGBScatter3D"]


class VisualRGBScatter3D(gfx.Points):
    """
    Create a *RGB* 3D scatter visual.
    """

    def __init__(
        self,
        RGB: ArrayLike,
        colourspace: str = "ITU-R BT.709",
        colourspace_model: str = "CIE xyY",
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        size: float = 2,
    ):
        colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

        RGB = as_float_array(RGB).reshape(-1, 3)

        RGB[RGB == 0] = EPSILON

        XYZ = RGB_to_XYZ(RGB, colourspace)

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                XYZ, colourspace.whitepoint, colourspace_model
            ),
            colourspace_model,
        )

        if colors is None:
            colors = RGB
        else:
            colors = np.tile(colors, (RGB.shape[0], 1))

        super().__init__(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(np.full(positions.shape[0], size)),
                colors=as_contiguous_array(
                    append_alpha_channel(colors, opacity)
                ),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )


if __name__ == "__main__":
    from pygfx import (
        Background,
        Display,
        BackgroundMaterial,
        Scene,
    )

    from colour_visuals.rgb_colourspace import VisualRGBColourspace3D

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualRGBScatter3D(np.random.random((64, 64, 3)))
    scene.add(visual_1)

    visual_2 = VisualRGBColourspace3D(segments=8, wireframe=True)
    scene.add(visual_2)

    visual_3 = VisualRGBScatter3D(
        np.random.random((64, 64, 3)), colors=np.array([0.5, 0.5, 0.5])
    )
    visual_3.local.position = np.array([0.5, 0, 0])
    scene.add(visual_3)

    gfx.show(scene, up=np.array([0, 0, 1]))
