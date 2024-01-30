# !/usr/bin/env python
"""
Rösch-MacAdam Visuals
=====================

Defines the *Rösch-MacAdam* visuals:

-   :class:`colour_visuals.VisualRoschMacAdam`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.colorimetry import (
    MultiSpectralDistributions,
    SpectralDistribution,
    SpectralShape,
)
from colour.constants import EPSILON
from colour.hints import ArrayLike, LiteralColourspaceModel, Sequence
from colour.models import XYZ_to_RGB
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    colourspace_model_axis_reorder,
)
from colour.volume import XYZ_outer_surface

from colour_visuals.common import (
    XYZ_to_colourspace_model,
    append_channel,
    as_contiguous_array,
)
from colour_visuals.visual import (
    MixinPropertyCMFS,
    MixinPropertyColour,
    MixinPropertyIlluminant,
    MixinPropertyKwargs,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualRoschMacAdam",
]


class VisualRoschMacAdam(
    MixinPropertyCMFS,
    MixinPropertyIlluminant,
    MixinPropertyKwargs,
    MixinPropertyModel,
    MixinPropertyColour,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
    """
    Create a *Rösch-MacAdam* visual.

    Parameters
    ----------
    cmfs
        Standard observer colour matching functions, default to the
        *CIE 1931 2 Degree Standard Observer*. ``cmfs`` can be of any type or
        form supported by the :func:`colour.plotting.common.filter_cmfs`
        definition.
    illuminant
        Illuminant spectral distribution, default to *CIE Illuminant E*.
        ``illuminant`` can be of any type or form supported by the
        :func:`colour.plotting.common.filter_illuminants` definition.
    model
        Colourspace model, see :attr:`colour.COLOURSPACE_MODELS` attribute for
        the list of supported colourspace models.
    colour
        Colour of the visual, if *None*, the colour is computed from the visual
        geometry.
    opacity
        Opacity of the visual.
    thickness
        Thickness of the visual lines.

    Other Parameters
    ----------------
    kwargs
        See the documentation of the supported conversion definitions.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualRoschMacAdam.cmfs`
    -   :attr:`~colour_visuals.VisualRoschMacAdam.illuminant`
    -   :attr:`~colour_visuals.VisualRoschMacAdam.model`
    -   :attr:`~colour_visuals.VisualRoschMacAdam.colour`
    -   :attr:`~colour_visuals.VisualRoschMacAdam.opacity`
    -   :attr:`~colour_visuals.VisualRoschMacAdam.thickness`
    -   :attr:`~colour_visuals.VisualRoschMacAdam.kwargs`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualRoschMacAdam.__init__`
    -   :meth:`~colour_visuals.VisualRoschMacAdam.update`

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
    ...     visual = VisualRoschMacAdam()
    ...     visual.local.rotation = la.quat_from_euler((-np.pi / 4, 0), order="XY")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualRoschMacAdam.png
        :align: center
        :alt: visual-rosch-mac-adam
    """

    def __init__(
        self,
        cmfs: (
            MultiSpectralDistributions
            | str
            | Sequence[MultiSpectralDistributions | str]
        ) = "CIE 1931 2 Degree Standard Observer",
        illuminant: (
            SpectralDistribution | str | Sequence[SpectralDistribution | str]
        ) = "E",
        model: LiteralColourspaceModel | str = "CIE xyY",
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
        **kwargs,
    ):
        super().__init__()

        self._solid = None

        with self.block_update():
            self.cmfs = cmfs
            self.illuminant = illuminant
            self.model = model
            self.colour = colour
            self.opacity = opacity
            self.thickness = thickness
            self.kwargs = kwargs

        self.update()

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        colourspace = CONSTANTS_COLOUR_STYLE.colour.colourspace

        XYZ = XYZ_outer_surface(
            self._cmfs.copy().align(
                SpectralShape(self._cmfs.shape.start, self._cmfs.shape.end, 5)
            ),
            self._illuminant,
        )

        XYZ[XYZ == 0] = EPSILON

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                XYZ,
                colourspace.whitepoint,
                self._model,
                **self._kwargs,
            ),
            self._model,
        )
        positions = np.concatenate([positions[:-1], positions[1:]], axis=1).reshape(
            [-1, 3]
        )

        if self._colour is None:
            colour = XYZ_to_RGB(XYZ, colourspace)
            colour = np.concatenate([colour[:-1], colour[1:]], axis=1).reshape([-1, 3])
        else:
            colour = np.tile(self._colour, (positions.shape[0], 1))

        self._solid = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colour, self._opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
        )
        self.add(self._solid)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualRoschMacAdam()
    scene.add(visual_1)

    visual_2 = VisualRoschMacAdam(model="CIE XYZ", colour=np.array([0.5, 0.5, 0.5]))
    visual_2.local.position = np.array([1, 0, 0])
    scene.add(visual_2)

    visual_3 = VisualRoschMacAdam(model="JzAzBz", colour=np.array([0.5, 0.5, 0.5]))
    visual_3.local.position = np.array([3.5, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualRoschMacAdam(model="ICtCp", colour=np.array([0.5, 0.5, 0.5]))
    visual_4.local.position = np.array([6, 0, 0])
    scene.add(visual_4)

    gfx.show(scene, up=np.array([0, 0, 1]))
