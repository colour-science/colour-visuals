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
from colour.hints import (
    ArrayLike,
    Literal,
    LiteralColourspaceModel,
    LiteralRGBColourspace,
    Sequence,
    Type,
)
from colour.models import RGB_Colourspace, RGB_to_XYZ, XYZ_to_RGB, xy_to_XYZ
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    METHODS_CHROMATICITY_DIAGRAM,
    colourspace_model_axis_reorder,
)
from colour.utilities import full

from colour_visuals.common import (
    XYZ_to_colourspace_model,
    append_channel,
    as_contiguous_array,
    conform_primitive_dtype,
)
from colour_visuals.visual import (
    MixinPropertyColour,
    MixinPropertyColourspace,
    MixinPropertyKwargs,
    MixinPropertyMethod,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertySegments,
    MixinPropertyThickness,
    MixinPropertyTypeMaterial,
    MixinPropertyWireframe,
    Visual,
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


class VisualRGBColourspace2D(
    MixinPropertyColourspace,
    MixinPropertyMethod,
    MixinPropertyColour,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
    """
    Create a 2D *RGB* colourspace gamut visual.

    Parameters
    ----------
    colourspace
        *RGB* colourspace to plot the gamut of. ``colourspaces`` elements
        can be of any type or form supported by the
        :func:`colour.plotting.common.filter_RGB_colourspaces` definition.
    method
        *Chromaticity Diagram* method.
    colour
        Colour of the visual, if *None*, the colour is computed from the visual
        geometry.
    opacity
        Opacity of the visual.
    thickness
        Thickness of the visual lines.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualRGBColourspace2D.colourspace`
    -   :attr:`~colour_visuals.VisualRGBColourspace2D.method`
    -   :attr:`~colour_visuals.VisualRGBColourspace2D.colour`
    -   :attr:`~colour_visuals.VisualRGBColourspace2D.opacity`
    -   :attr:`~colour_visuals.VisualRGBColourspace2D.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualRGBColourspace2D.__init__`
    -   :meth:`~colour_visuals.VisualRGBColourspace2D.update`

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
    ...     visual = VisualRGBColourspace2D()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualRGBColourspace2D.png
        :align: center
        :alt: visual-rgbcolourspace-2-d
    """

    def __init__(
        self,
        colourspace: (
            RGB_Colourspace
            | str
            | Sequence[RGB_Colourspace | LiteralRGBColourspace | str]
        ) = "sRGB",
        method: (
            Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"] | str
        ) = "CIE 1931",
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        self._gamut = None
        self._whitepoint = None

        with self.block_update():
            self.colourspace = colourspace
            self.method = method
            self.colour = colour
            self.opacity = opacity
            self.thickness = thickness

        self.update()

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        plotting_colourspace = CONSTANTS_COLOUR_STYLE.colour.colourspace

        XYZ_to_ij = METHODS_CHROMATICITY_DIAGRAM[self._method]["XYZ_to_ij"]

        ij = XYZ_to_ij(
            xy_to_XYZ(self._colourspace.primaries),
            plotting_colourspace.whitepoint,
        )
        ij[np.isnan(ij)] = 0

        positions = append_channel(
            np.array([ij[0], ij[1], ij[1], ij[2], ij[2], ij[0]]), 0
        )

        if self._colour is None:
            RGB = XYZ_to_RGB(
                xy_to_XYZ(self._colourspace.primaries), plotting_colourspace
            )
            colour_g = np.array([RGB[0], RGB[1], RGB[1], RGB[2], RGB[2], RGB[0]])
        else:
            colour_g = np.tile(self._colour, (positions.shape[0], 1))

        self._gamut = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colour_g, self._opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
        )
        self.add(self._gamut)

        ij = XYZ_to_ij(
            xy_to_XYZ(self._colourspace.whitepoint),
            plotting_colourspace.whitepoint,
        )

        positions = append_channel(ij, 0).reshape([-1, 3])

        if self._colour is None:
            colour_w = XYZ_to_RGB(
                xy_to_XYZ(self._colourspace.whitepoint), plotting_colourspace
            ).reshape([-1, 3])
        else:
            colour_w = np.tile(self._colour, (positions.shape[0], 1))

        self._whitepoint = gfx.Points(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(
                    full(positions.shape[0], self._thickness * 3)
                ),
                colors=as_contiguous_array(append_channel(colour_w, self._opacity)),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )
        self.add(self._whitepoint)


class VisualRGBColourspace3D(
    MixinPropertyColourspace,
    MixinPropertyModel,
    MixinPropertyColour,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    MixinPropertyTypeMaterial,
    MixinPropertyWireframe,
    MixinPropertySegments,
    MixinPropertyKwargs,
    Visual,
):
    """
    Create a 3D *RGB* colourspace volume visual.

    Parameters
    ----------
    colourspace
        *RGB* colourspace to plot the gamut of. ``colourspaces`` elements
        can be of any type or form supported by the
        :func:`colour.plotting.common.filter_RGB_colourspaces` definition.
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
    material
        Material used to surface the visual geometry.
    wireframe
        Whether to render the visual as a wireframe, i.e., only render edges.
    segments
        Edge segments count for the *RGB* colourspace cube.

    Other Parameters
    ----------------
    kwargs
        See the documentation of the supported conversion definitions.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.colourspace`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.model`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.colour`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.opacity`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.thickness`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.type_material`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.wireframe`
    -   :attr:`~colour_visuals.VisualRGBColourspace3D.segments`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualRGBColourspace3D.__init__`
    -   :meth:`~colour_visuals.VisualRGBColourspace3D.update`

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
    ...     visual = VisualRGBColourspace3D(wireframe=True)
    ...     visual.local.rotation = la.quat_from_euler((-np.pi / 4, 0), order="XY")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualRGBColourspace3D.png
        :align: center
        :alt: visual-rgbcolourspace-3-d
    """

    def __init__(
        self,
        colourspace: (
            RGB_Colourspace
            | str
            | Sequence[RGB_Colourspace | LiteralRGBColourspace | str]
        ) = "sRGB",
        model: LiteralColourspaceModel | str = "CIE xyY",
        colour: ArrayLike | None = None,
        opacity: float = 1,
        material: Type[gfx.MeshAbstractMaterial] = gfx.MeshBasicMaterial,
        wireframe: bool = False,
        segments: int = 16,
        **kwargs,
    ):
        super().__init__()

        self._gamut = None
        self._whitepoint = None

        with self.block_update():
            self.colourspace = colourspace
            self.model = model
            self.colour = colour
            self.opacity = opacity
            self.type_material = material
            self.wireframe = wireframe
            self.segments = segments
            self.kwargs = kwargs

        self.update()

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        vertices, faces, outline = conform_primitive_dtype(
            primitive_cube(
                width_segments=self._segments,
                height_segments=self._segments,
                depth_segments=self._segments,
            )
        )

        positions = vertices["position"] + 0.5

        positions[positions == 0] = EPSILON

        if self._colour is None:
            colour = positions
        else:
            colour = np.tile(self._colour, (positions.shape[0], 1))

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                RGB_to_XYZ(positions, self._colourspace),
                self._colourspace.whitepoint,
                self._model,
                **self._kwargs,
            ),
            self._model,
        )

        self._gamut = gfx.Mesh(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                normals=vertices["normal"],
                indices=outline[..., 1].reshape([-1, 4]),
                colors=as_contiguous_array(append_channel(colour, self._opacity)),
            ),
            (
                self._type_material(color_mode="vertex", wireframe=self._wireframe)
                if self._wireframe
                else self._type_material(color_mode="vertex")
            ),
        )
        self.add(self._gamut)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    light_1 = gfx.AmbientLight()
    scene.add(light_1)

    light_2 = gfx.DirectionalLight()
    light_2.local.position = np.array([1, 1, 0])
    scene.add(light_2)

    visual_1 = VisualRGBColourspace3D()
    scene.add(visual_1)

    visual_2 = VisualRGBColourspace3D(wireframe=True)
    visual_2.local.position = np.array([0.5, 0, 0])
    scene.add(visual_2)

    visual_3 = VisualRGBColourspace3D(material=gfx.MeshNormalMaterial)
    visual_3.local.position = np.array([1, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualRGBColourspace3D(
        model="CIE Lab",
        colour=np.array([0.5, 0.5, 0.5]),
        opacity=1,
        material=gfx.MeshStandardMaterial,
    )
    visual_4.local.position = np.array([2.5, 0, 0])
    scene.add(visual_4)

    visual_5 = VisualRGBColourspace2D()
    visual_5.local.position = np.array([3.5, 0, 0])
    scene.add(visual_5)

    visual_6 = VisualRGBColourspace2D(
        method="CIE 1976 UCS",
        colour=np.array([0.5, 0.5, 0.5]),
        opacity=1,
    )
    visual_6.local.position = np.array([4.5, 0, 0])
    scene.add(visual_6)

    visual_7 = VisualRGBColourspace3D(model="RGB")
    visual_7.local.position = np.array([5.5, 0, 0])
    scene.add(visual_7)

    gfx.show(scene, up=np.array([0, 0, 1]))
