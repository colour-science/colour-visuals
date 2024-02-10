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
    NDArray,
    Sequence,
)
from colour.models import RGB_Colourspace
from colour.plotting import (
    colourspace_model_axis_reorder,
)
from colour.utilities import as_float_array

from colour_visuals.common import (
    XYZ_to_colourspace_model,
    append_channel,
    as_contiguous_array,
)
from colour_visuals.visual import (
    MixinPropertyColour,
    MixinPropertyColourspace,
    MixinPropertyKwargs,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertySize,
    Visual,
    visual_property,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["VisualRGBScatter3D"]


class VisualRGBScatter3D(
    MixinPropertyColour,
    MixinPropertyColourspace,
    MixinPropertyKwargs,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertySize,
    Visual,
):
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
    colour
        Colour of the visual, if *None*, the colour is computed from the visual
        geometry.
    opacity
        Opacity of the visual.
    size
        Size of the visual points

    Other Parameters
    ----------------
    kwargs
        See the documentation of the supported conversion definitions.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualRGBScatter3D.RGB`
    -   :attr:`~colour_visuals.VisualRGBScatter3D.colourspace`
    -   :attr:`~colour_visuals.VisualRGBScatter3D.model`
    -   :attr:`~colour_visuals.VisualRGBScatter3D.colour`
    -   :attr:`~colour_visuals.VisualRGBScatter3D.opacity`
    -   :attr:`~colour_visuals.VisualRGBScatter3D.size`
    -   :attr:`~colour_visuals.VisualRGBScatter3D.kwargs`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualRGBScatter3D.__init__`
    -   :meth:`~colour_visuals.VisualRGBScatter3D.update`

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
    ...     visual.local.rotation = la.quat_from_euler((-np.pi / 4, 0), order="XY")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualRGBScatter3D.png
        :align: center
        :alt: visual-rgbscatter-3-d
    """

    def __init__(
        self,
        RGB: ArrayLike,
        colourspace: (
            RGB_Colourspace
            | str
            | Sequence[RGB_Colourspace | LiteralRGBColourspace | str]
        ) = "sRGB",
        model: LiteralColourspaceModel | str = "CIE xyY",
        colour: ArrayLike | None = None,
        opacity: float = 1,
        size: float = 2,
        **kwargs,
    ):
        super().__init__()

        self._RGB = np.array([])
        self._scatter = None

        with self.block_update():
            self.RGB = RGB
            self.colourspace = colourspace
            self.model = model
            self.colour = colour
            self.opacity = opacity
            self.size = size
            self.kwargs = kwargs

        self.update()

    @visual_property
    def RGB(self) -> NDArray:
        """
        Getter and setter property for the *RGB* colourspace array.

        Parameters
        ----------
        value
            Value to set the *RGB* colourspace array with.

        Returns
        -------
        :class:`numpy.ndarray`
            *RGB* colourspace array.
        """

        return self._RGB

    @RGB.setter
    def RGB(self, value: ArrayLike):
        """Setter for the **self.RGB** property."""

        self._RGB = np.reshape(as_float_array(value), (-1, 3))
        self._RGB[self._RGB == 0] = EPSILON

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        XYZ = RGB_to_XYZ(self._RGB, self._colourspace)

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                XYZ,
                self._colourspace.whitepoint,
                self._model,
                **self._kwargs,
            ),
            self._model,
        )

        if self._colour is None:
            colour = self._RGB
        else:
            colour = np.tile(self._colour, (self._RGB.shape[0], 1))

        self._scatter = gfx.Points(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(np.full(positions.shape[0], self._size)),
                colors=as_contiguous_array(append_channel(colour, self._opacity)),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )
        self.add(self._scatter)


if __name__ == "__main__":
    from colour_visuals.rgb_colourspace import VisualRGBColourspace3D

    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualRGBScatter3D(np.random.random((64, 64, 3)))
    scene.add(visual_1)

    visual_2 = VisualRGBColourspace3D(segments=8, wireframe=True)
    scene.add(visual_2)

    visual_3 = VisualRGBScatter3D(
        np.random.random((64, 64, 3)), colour=np.array([0.5, 0.5, 0.5])
    )
    visual_3.local.position = np.array([0.5, 0, 0])
    scene.add(visual_3)

    gfx.show(scene, up=np.array([0, 0, 1]))
