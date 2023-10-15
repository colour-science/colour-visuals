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
from colour.hints import (
    ArrayLike,
    LiteralColourspaceModel,
    LiteralRGBColourspace,
    Sequence,
    cast,
)
from colour.models import RGB_Colourspace
from colour.plotting import (
    colourspace_model_axis_reorder,
    filter_RGB_colourspaces,
)
from colour.utilities import as_float_array, first_item

from colour_visuals.common import (
    XYZ_to_colourspace_model,
    append_channel,
    as_contiguous_array,
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
    Create a 3D *RGB* scatter visual.

    Parameters
    ----------
    RGB
        *RGB* colourspace array.
    colourspace
        *RGB* colourspace of the *RGB* array. ``colourspace`` can be of any
        type or form supported by the
        :func:`colour.plotting.common.filter_RGB_colourspaces` definition.
    model
        Colourspace model, see :attr:`colour.COLOURSPACE_MODELS` attribute for
        the list of supported colourspace models.
    colours
        Colours of the visual, if *None*, the colours are computed from the
        visual geometry.
    opacity
        Opacity of the visual.
    size
        Size of the visual points

    Examples
    --------
    >>> import os
    >>> import pylinalg as la
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
    ...     visual = VisualRGBScatter3D(np.random.random([24, 32, 3]))
    ...     visual.local.rotation = la.quat_from_euler(
    ...         (-np.pi / 4, 0), order="XY"
    ...     )
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualRGBScatter3D.png
        :align: center
        :alt: visual-rgbscatter-3-d
    """

    def __init__(
        self,
        RGB: ArrayLike,
        colourspace: RGB_Colourspace
        | str
        | Sequence[RGB_Colourspace | LiteralRGBColourspace | str] = "sRGB",
        model: LiteralColourspaceModel | str = "CIE xyY",
        colours: ArrayLike | None = None,
        opacity: float = 1,
        size: float = 2,
    ):
        colourspace = cast(
            RGB_Colourspace,
            first_item(filter_RGB_colourspaces(colourspace).values()),
        )

        RGB = as_float_array(RGB).reshape(-1, 3)

        RGB[RGB == 0] = EPSILON

        XYZ = RGB_to_XYZ(RGB, colourspace)

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(XYZ, colourspace.whitepoint, model),
            model,
        )

        if colours is None:  # noqa: SIM108
            colours = RGB
        else:
            colours = np.tile(colours, (RGB.shape[0], 1))

        super().__init__(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(np.full(positions.shape[0], size)),
                colors=as_contiguous_array(append_channel(colours, opacity)),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )


if __name__ == "__main__":
    from colour_visuals.rgb_colourspace import VisualRGBColourspace3D

    scene = gfx.Scene()

    scene.add(
        gfx.Background(
            None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
        )
    )

    visual_1 = VisualRGBScatter3D(np.random.random((64, 64, 3)))
    scene.add(visual_1)

    visual_2 = VisualRGBColourspace3D(segments=8, wireframe=True)
    scene.add(visual_2)

    visual_3 = VisualRGBScatter3D(
        np.random.random((64, 64, 3)), colours=np.array([0.5, 0.5, 0.5])
    )
    visual_3.local.position = np.array([0.5, 0, 0])
    scene.add(visual_3)

    gfx.show(scene, up=np.array([0, 0, 1]))
