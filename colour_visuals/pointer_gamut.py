# !/usr/bin/env python
"""
Pointer Gamut Visuals
=====================

Defines the *Pointer's Gamut* visuals:

-   :class:`colour_visuals.VisualPointerGamut2D`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.hints import ArrayLike
from colour.models import (
    CCS_ILLUMINANT_POINTER_GAMUT,
    DATA_POINTER_GAMUT_VOLUME,
    LCHab_to_Lab,
    Lab_to_XYZ,
)
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    XYZ_to_plotting_colourspace,
    colourspace_model_axis_reorder,
    lines_pointer_gamut,
)

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
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

__all__ = ["VisualPointerGamut2D"]


class VisualPointerGamut2D(gfx.Group):
    """
    Create a *Pointer's Gamut* 2D visual.
    """

    def __init__(
        self,
        method: str = "CIE 1931",
        colors: ArrayLike | str | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        lines_b, lines_v = lines_pointer_gamut(method)

        # Boundary
        positions = np.concatenate(
            [lines_b["position"][:-1], lines_b["position"][1:]], axis=1
        ).reshape([-1, 2])
        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if colors is None:
            colors_b = np.concatenate(
                [lines_b["colour"][:-1], lines_b["colour"][1:]], axis=1
            ).reshape([-1, 3])
        else:
            colors_b = np.tile(colors, (positions.shape[0], 1))

        self._pointer_gamut_boundary = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(
                    append_alpha_channel(colors_b, opacity)
                ),
            ),
            gfx.LineSegmentMaterial(thickness=thickness, color_mode="vertex"),
        )
        self.add(self._pointer_gamut_boundary)

        # Volume
        positions = np.hstack(
            [
                lines_v["position"],
                np.full(
                    (lines_v["position"].shape[0], 1),
                    0,
                    DEFAULT_FLOAT_DTYPE_WGPU,
                ),
            ]
        )

        if colors is None:
            colors_v = lines_v["colour"]
        else:
            colors_v = np.tile(colors, (lines_v["colour"].shape[0], 1))

        self._pointer_gamut_volume = gfx.Points(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(
                    np.full(positions.shape[0], thickness * 3)
                ),
                colors=as_contiguous_array(
                    append_alpha_channel(colors_v, opacity)
                ),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )
        self.add(self._pointer_gamut_volume)


class VisualPointerGamut3D(gfx.Line):
    """
    Create a *Pointer's Gamut* 3D visual.
    """

    def __init__(
        self,
        colourspace_model: str = "CIE xyY",
        segments: int = 16,
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        thickness: float = 1,
    ):
        super().__init__()

        illuminant = CONSTANTS_COLOUR_STYLE.colour.colourspace.whitepoint

        data_pointer_gamut = np.reshape(
            Lab_to_XYZ(
                LCHab_to_Lab(DATA_POINTER_GAMUT_VOLUME),
                CCS_ILLUMINANT_POINTER_GAMUT,
            ),
            (16, -1, 3),
        )

        sections = []
        for i in range(16):
            section = np.vstack(
                np.vstack(
                    [data_pointer_gamut[i], data_pointer_gamut[i][0, ...]]
                )
            )
            sections.append(
                np.concatenate([section[:-1], section[1:]], axis=1).reshape(
                    [-1, 3]
                )
            )

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                sections,
                CCS_ILLUMINANT_POINTER_GAMUT,
                colourspace_model,
            ),
            colourspace_model,
        ).reshape([-1, 3])

        if colors is None:
            colors = XYZ_to_plotting_colourspace(sections, illuminant).reshape(
                [-1, 3]
            )
        else:
            colors = np.tile(colors, (positions.shape[0], 1))

        super().__init__(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(
                    append_alpha_channel(colors, opacity)
                ),
            ),
            gfx.LineSegmentMaterial(thickness=thickness, color_mode="vertex"),
        )


if __name__ == "__main__":
    from pygfx import (
        Background,
        Display,
        BackgroundMaterial,
        Scene,
    )

    from colour_visuals.diagrams import VisualSpectralLocus2D

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualSpectralLocus2D()
    scene.add(visual_1)

    visual_2 = VisualPointerGamut2D()
    scene.add(visual_2)

    visual_3 = VisualPointerGamut2D(colors=np.array([0.5, 0.5, 0.5]))
    visual_3.local.position = np.array([1, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualPointerGamut3D()
    visual_4.local.position = np.array([2, 0, 0])
    scene.add(visual_4)

    gfx.show(scene, up=np.array([0, 0, 1]))
