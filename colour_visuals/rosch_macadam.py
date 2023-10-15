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
from colour.hints import ArrayLike, LiteralColourspaceModel, Sequence, cast
from colour.models import XYZ_to_RGB
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    colourspace_model_axis_reorder,
    filter_cmfs,
    filter_illuminants,
)
from colour.utilities import (
    first_item,
)
from colour.volume import XYZ_outer_surface

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

__all__ = [
    "VisualRoschMacAdam",
]


class VisualRoschMacAdam(gfx.Line):
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
    colours
        Colours of the visual, if *None*, the colours are computed from the
        visual geometry.
    opacity
        Opacity of the visual.
    thickness
        Thickness of the visual lines.

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
    ...     visual.local.rotation = la.quat_from_euler(
    ...         (-np.pi / 4, 0), order="XY"
    ...     )
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualRoschMacAdam.png
        :align: center
        :alt: visual-rosch-mac-adam
    """

    def __init__(
        self,
        cmfs: MultiSpectralDistributions
        | str
        | Sequence[
            MultiSpectralDistributions | str
        ] = "CIE 1931 2 Degree Standard Observer",
        illuminant: SpectralDistribution
        | str
        | Sequence[SpectralDistribution | str] = "E",
        model: LiteralColourspaceModel | str = "CIE xyY",
        colours: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        cmfs = cast(
            MultiSpectralDistributions, first_item(filter_cmfs(cmfs).values())
        )
        illuminant = cast(
            SpectralDistribution,
            first_item(filter_illuminants(illuminant).values()),
        )

        colourspace = CONSTANTS_COLOUR_STYLE.colour.colourspace

        XYZ = XYZ_outer_surface(
            cmfs.copy().align(
                SpectralShape(cmfs.shape.start, cmfs.shape.end, 5)
            ),
            illuminant,
        )

        XYZ[XYZ == 0] = EPSILON

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(XYZ, colourspace.whitepoint, model),
            model,
        )
        positions = np.concatenate(
            [positions[:-1], positions[1:]], axis=1
        ).reshape([-1, 3])

        if colours is None:
            colours = XYZ_to_RGB(XYZ, colourspace)
            colours = np.concatenate(
                [colours[:-1], colours[1:]], axis=1
            ).reshape([-1, 3])
        else:
            colours = np.tile(colours, (positions.shape[0], 1))

        super().__init__(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colours, opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=thickness, color_mode="vertex"),
        )


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(
            None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
        )
    )

    visual_1 = VisualRoschMacAdam()
    scene.add(visual_1)

    visual_2 = VisualRoschMacAdam(
        model="CIE XYZ", colours=np.array([0.5, 0.5, 0.5])
    )
    visual_2.local.position = np.array([1, 0, 0])
    scene.add(visual_2)

    visual_3 = VisualRoschMacAdam(
        model="JzAzBz", colours=np.array([0.5, 0.5, 0.5])
    )
    visual_3.local.position = np.array([3.5, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualRoschMacAdam(
        model="ICtCp", colours=np.array([0.5, 0.5, 0.5])
    )
    visual_4.local.position = np.array([6, 0, 0])
    scene.add(visual_4)

    gfx.show(scene, up=np.array([0, 0, 1]))
