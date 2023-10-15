# !/usr/bin/env python
"""
RGB Colourspace Visuals
=======================

Defines the *RGB colourspace* visuals:

-   :class:`colour_visuals.VisualRGBColourspace2D`
-   :class:`colour_visuals.VisualRGBColourspace3D`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.constants import EPSILON
from colour.geometry import primitive_cube
from colour.hints import ArrayLike, Type
from colour.models import RGB_to_XYZ, XYZ_to_RGB, xy_to_XYZ
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    METHODS_CHROMATICITY_DIAGRAM,
    colourspace_model_axis_reorder,
    filter_RGB_colourspaces,
)
from colour.utilities import first_item

from colour_visuals.common import (
    append_alpha_channel,
    as_contiguous_array,
    conform_primitive_dtype,
    XYZ_to_colourspace_model,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualRGBColourspace2D",
    "VisualRGBColourspace3D",
]


class VisualRGBColourspace2D(gfx.Line):
    """
    Create a *RGB* colourspace 2D gamut visual.
    """

    def __init__(
        self,
        colourspace: str = "ITU-R BT.709",
        chromaticity_diagram: str = "CIE 1931",
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        thickness: float = 1,
    ):
        colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

        plotting_colourspace = CONSTANTS_COLOUR_STYLE.colour.colourspace

        XYZ_to_ij = METHODS_CHROMATICITY_DIAGRAM[chromaticity_diagram][
            "XYZ_to_ij"
        ]

        ij = XYZ_to_ij(
            xy_to_XYZ(colourspace.primaries), plotting_colourspace.whitepoint
        )
        ij[np.isnan(ij)] = 0

        positions = append_alpha_channel(
            np.array([ij[0], ij[1], ij[1], ij[2], ij[2], ij[0]]), 0
        )

        if colors is None:
            RGB = XYZ_to_RGB(
                xy_to_XYZ(colourspace.primaries), plotting_colourspace
            )
            colors = np.array([RGB[0], RGB[1], RGB[1], RGB[2], RGB[2], RGB[0]])
        else:
            colors = np.tile(colors, (positions.shape[0], 1))

        geometry = gfx.Geometry(
            positions=as_contiguous_array(positions),
            colors=as_contiguous_array(append_alpha_channel(colors, opacity)),
        )

        super().__init__(
            geometry,
            gfx.LineSegmentMaterial(thickness=thickness, color_mode="vertex"),
        )


class VisualRGBColourspace3D(gfx.Mesh):
    """
    Create a *RGB* colourspace 3D volume visual.
    """

    def __init__(
        self,
        colourspace: str = "ITU-R BT.709",
        colourspace_model: str = "CIE xyY",
        segments: int = 16,
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        material: Type[gfx.MeshAbstractMaterial] = gfx.MeshBasicMaterial,
        wireframe: bool = False,
    ):
        colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

        vertices, faces, outline = conform_primitive_dtype(
            primitive_cube(
                width_segments=segments,
                height_segments=segments,
                depth_segments=segments,
            )
        )

        positions = vertices["position"] + 0.5

        if colors is None:
            colors = positions
        else:
            colors = np.tile(colors, (positions.shape[0], 1))

        positions[positions == 0] = EPSILON
        XYZ = RGB_to_XYZ(positions, colourspace)
        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                XYZ, colourspace.whitepoint, colourspace_model
            ),
            colourspace_model,
        )

        geometry = gfx.Geometry(
            positions=as_contiguous_array(positions),
            normals=vertices["normal"],
            indices=outline[..., 1].reshape([-1, 4]),
            colors=as_contiguous_array(append_alpha_channel(colors, opacity)),
        )

        super().__init__(
            geometry,
            material(color_mode="vertex", wireframe=wireframe)
            if wireframe
            else material(color_mode="vertex"),
        )


if __name__ == "__main__":
    from pygfx import (
        AmbientLight,
        Background,
        BackgroundMaterial,
        DirectionalLight,
        Display,
        MeshStandardMaterial,
        MeshNormalMaterial,
        Scene,
    )

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    light_1 = AmbientLight()
    scene.add(light_1)

    light_2 = DirectionalLight()
    light_2.local.position = np.array([1, 1, 0])
    scene.add(light_2)

    visual_1 = VisualRGBColourspace3D()
    scene.add(visual_1)

    visual_2 = VisualRGBColourspace3D(wireframe=True)
    visual_2.local.position = np.array([0.5, 0, 0])
    scene.add(visual_2)

    visual_3 = VisualRGBColourspace3D(material=MeshNormalMaterial)
    visual_3.local.position = np.array([1, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualRGBColourspace3D(
        colourspace_model="CIE Lab",
        colors=np.array([0.5, 0.5, 0.5]),
        opacity=1,
        material=MeshStandardMaterial,
    )
    visual_4.local.position = np.array([2.5, 0, 0])
    scene.add(visual_4)

    visual_5 = VisualRGBColourspace2D()
    visual_5.local.position = np.array([3.5, 0, 0])
    scene.add(visual_5)

    visual_6 = VisualRGBColourspace2D(
        chromaticity_diagram="CIE 1976 UCS",
        colors=np.array([0.5, 0.5, 0.5]),
        opacity=1,
    )
    visual_6.local.position = np.array([4.5, 0, 0])
    scene.add(visual_6)

    gfx.show(scene, up=np.array([0, 0, 1]))
