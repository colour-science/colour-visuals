# !/usr/bin/env python
"""
Daylight Locus Visuals
=======================

Defines the *Daylight Locus* visuals:

-   :class:`colour_visuals.VisualDaylightLocus`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.hints import (
    ArrayLike,
    Literal,
)
from colour.plotting import (
    lines_daylight_locus,
)

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    append_channel,
    as_contiguous_array,
)
from colour_visuals.visual import (
    MixinPropertyColour,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
    visual_property,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualDaylightLocus",
]


class VisualDaylightLocus(
    MixinPropertyColour,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
    """
    Create a *Daylight Locus* visual.

    Parameters
    ----------
    method
        *Daylight Locus* method.
    mireds
        Whether to use micro reciprocal degrees for the iso-temperature lines.
    colour
        Colour of the visual, if *None*, the colour is computed from the visual
        geometry.
    opacity
        Opacity of the visual.
    thickness
        Thickness of the visual lines.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualDaylightLocus.method`
    -   :attr:`~colour_visuals.VisualDaylightLocus.mireds`
    -   :attr:`~colour_visuals.VisualDaylightLocus.colour`
    -   :attr:`~colour_visuals.VisualDaylightLocus.opacity`
    -   :attr:`~colour_visuals.VisualDaylightLocus.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualDaylightLocus.__init__`
    -   :meth:`~colour_visuals.VisualDaylightLocus.update`

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
    ...     visual = VisualDaylightLocus()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualDaylightLocus.png
        :align: center
        :alt: visual-daylight-locus
    """

    def __init__(
        self,
        method: (
            Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"] | str
        ) = "CIE 1931",
        mireds: bool = False,
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        self._daylight_locus = None
        self._iso_temperature_lines = []
        self._texts = []

        self._mireds = False

        with self.block_update():
            self.method = method
            self.mireds = mireds
            self.colour = colour
            self.opacity = opacity
            self.thickness = thickness

        self.update()

    @visual_property
    def mireds(
        self,
    ) -> bool:
        """
        Getter and setter property for the mireds state.

        Parameters
        ----------
        value
            Value to set the mireds state with.

        Returns
        -------
        :class:`bool`
             Mireds state.
        """

        return self._mireds

    @mireds.setter
    def mireds(self, value: bool):
        """Setter for the **self.mireds** property."""

        self._mireds = value

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        lines_dl, *_ = lines_daylight_locus(self._mireds, self._method)

        # Daylight Locus
        positions = np.reshape(
            np.concatenate(
                [lines_dl["position"][:-1], lines_dl["position"][1:]], axis=1
            ),
            (-1, 2),
        )

        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if self._colour is None:
            colour_sl = np.reshape(
                np.concatenate(
                    [lines_dl["colour"][:-1], lines_dl["colour"][1:]], axis=1
                ),
                (-1, 3),
            )
        else:
            colour_sl = np.tile(self._colour, (positions.shape[0], 1))

        self._daylight_locus = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colour_sl, self._opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
        )
        self.add(self._daylight_locus)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualDaylightLocus()
    scene.add(visual_1)

    gfx.show(scene, up=np.array([0, 0, 1]))
