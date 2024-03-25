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
from colour.hints import ArrayLike, Literal, LiteralColourspaceModel
from colour.models import (
    CCS_ILLUMINANT_POINTER_GAMUT,
    DATA_POINTER_GAMUT_VOLUME,
    Lab_to_XYZ,
    LCHab_to_Lab,
)
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    XYZ_to_plotting_colourspace,
    colourspace_model_axis_reorder,
    lines_pointer_gamut,
)

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    XYZ_to_colourspace_model,
    append_channel,
    as_contiguous_array,
)
from colour_visuals.visual import (
    MixinPropertyColour,
    MixinPropertyKwargs,
    MixinPropertyMethod,
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

__all__ = ["VisualPointerGamut2D", "VisualPointerGamut3D"]


class VisualPointerGamut2D(
    MixinPropertyColour,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
    """
    Create a 2D *Pointer's Gamut* visual.

    Parameters
    ----------
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
    -   :attr:`~colour_visuals.VisualPointerGamut2D.method`
    -   :attr:`~colour_visuals.VisualPointerGamut2D.colour`
    -   :attr:`~colour_visuals.VisualPointerGamut2D.opacity`
    -   :attr:`~colour_visuals.VisualPointerGamut2D.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualPointerGamut2D.__init__`
    -   :meth:`~colour_visuals.VisualPointerGamut2D.update`

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
    ...     visual = VisualPointerGamut2D()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualPointerGamut2D.png
        :align: center
        :alt: visual-pointer-gamut-2-d
    """

    def __init__(
        self,
        method: (
            Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"] | str
        ) = "CIE 1931",
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        self._pointer_gamut_boundary = None
        self._pointer_gamut_volume = None

        with self.block_update():
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

        lines_b, lines_v = lines_pointer_gamut(self._method)

        # Boundary
        positions = np.reshape(
            np.concatenate([lines_b["position"][:-1], lines_b["position"][1:]], axis=1),
            (-1, 2),
        )
        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if self._colour is None:
            colour_b = np.reshape(
                np.concatenate([lines_b["colour"][:-1], lines_b["colour"][1:]], axis=1),
                (-1, 3),
            )
        else:
            colour_b = np.tile(self._colour, (positions.shape[0], 1))

        self._pointer_gamut_boundary = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colour_b, self._opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
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

        if self._colour is None:
            colour_v = lines_v["colour"]
        else:
            colour_v = np.tile(self._colour, (lines_v["colour"].shape[0], 1))

        self._pointer_gamut_volume = gfx.Points(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(
                    np.full(positions.shape[0], self._thickness * 3)
                ),
                colors=as_contiguous_array(append_channel(colour_v, self._opacity)),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )
        self.add(self._pointer_gamut_volume)


class VisualPointerGamut3D(
    MixinPropertyColour,
    MixinPropertyKwargs,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
    """
    Create a 3D *Pointer's Gamut* visual.

    Parameters
    ----------
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

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualPointerGamut3D.model`
    -   :attr:`~colour_visuals.VisualPointerGamut3D.colour`
    -   :attr:`~colour_visuals.VisualPointerGamut3D.opacity`
    -   :attr:`~colour_visuals.VisualPointerGamut3D.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualPointerGamut3D.__init__`
    -   :meth:`~colour_visuals.VisualPointerGamut3D.update`

    Other Parameters
    ----------------
    kwargs
        See the documentation of the supported conversion definitions.

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
    ...     visual = VisualPointerGamut3D()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualPointerGamut3D.png
        :align: center
        :alt: visual-pointer-gamut-3-d
    """

    def __init__(
        self,
        model: LiteralColourspaceModel | str = "CIE xyY",
        colour: ArrayLike | None = None,
        opacity: float = 0.5,
        thickness: float = 1,
        **kwargs,
    ):
        super().__init__()

        self._pointer_gamut_boundary = None
        self._pointer_gamut_volume = None

        with self.block_update():
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
            section = np.vstack([data_pointer_gamut[i], data_pointer_gamut[i][0, ...]])
            sections.append(
                np.reshape(np.concatenate([section[:-1], section[1:]], axis=1), (-1, 3))
            )

        positions = np.reshape(
            colourspace_model_axis_reorder(
                XYZ_to_colourspace_model(
                    sections,
                    CCS_ILLUMINANT_POINTER_GAMUT,
                    self._model,
                    **self._kwargs,
                ),
                self._model,
            ),
            (-1, 3),
        )

        if self._colour is None:
            colour = np.reshape(
                XYZ_to_plotting_colourspace(sections, illuminant), (-1, 3)
            )
        else:
            colour = np.tile(self._colour, (positions.shape[0], 1))

        self._pointer_gamut = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colour, self._opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
        )
        self.add(self._pointer_gamut)


if __name__ == "__main__":
    from colour_visuals.diagrams import VisualSpectralLocus2D

    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualSpectralLocus2D()
    scene.add(visual_1)

    visual_2 = VisualPointerGamut2D()
    scene.add(visual_2)

    visual_3 = VisualPointerGamut2D(colour=np.array([0.5, 0.5, 0.5]))
    visual_3.local.position = np.array([1, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualPointerGamut3D()
    visual_4.local.position = np.array([2, 0, 0])
    scene.add(visual_4)

    gfx.show(scene, up=np.array([0, 0, 1]))
