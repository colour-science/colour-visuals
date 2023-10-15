# !/usr/bin/env python
"""
Chromaticity Diagram Visuals
============================

Defines the *Chromaticity Diagram* visuals:

-   :class:`colour_visuals.VisualSpectralLocus2D`
-   :class:`colour_visuals.VisualSpectralLocus3D`
-   :class:`colour_visuals.VisualChromaticityDiagram`
-   :class:`colour_visuals.VisualChromaticityDiagramCIE1931`
-   :class:`colour_visuals.VisualChromaticityDiagramCIE1960UCS`
-   :class:`colour_visuals.VisualChromaticityDiagramCIE1976UCS`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.algebra import euclidean_distance, normalise_maximum
from colour.colorimetry import MultiSpectralDistributions
from colour.hints import (
    ArrayLike,
    Literal,
    LiteralColourspaceModel,
    Sequence,
    Type,
    cast,
)
from colour.models import XYZ_to_RGB
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    LABELS_CHROMATICITY_DIAGRAM_DEFAULT,
    METHODS_CHROMATICITY_DIAGRAM,
    XYZ_to_plotting_colourspace,
    colourspace_model_axis_reorder,
    filter_cmfs,
)
from colour.plotting.diagrams import lines_spectral_locus
from colour.utilities import (
    first_item,
    full,
    optional,
    tstack,
    validate_method,
)
from scipy.spatial import Delaunay

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    DEFAULT_INT_DTYPE_WGPU,
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
    "VisualSpectralLocus2D",
    "VisualSpectralLocus3D",
    "VisualChromaticityDiagram",
    "VisualChromaticityDiagramCIE1931",
    "VisualChromaticityDiagramCIE1960UCS",
    "VisualChromaticityDiagramCIE1976UCS",
]


class VisualSpectralLocus2D(gfx.Group):
    """
    Create a 2D *Spectral Locus* visual.

    Parameters
    ----------
    cmfs
        Standard observer colour matching functions used for computing the
        spectrum domain and colours. ``cmfs`` can be of any type or form
        supported by the :func:`colour.plotting.common.filter_cmfs` definition.
    method
        *Chromaticity Diagram* method.
    labels
        Array of wavelength labels used to customise which labels will be drawn
        around the spectral locus. Passing an empty array will result in no
        wavelength labels being drawn.
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
    ...     visual = VisualSpectralLocus2D()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualSpectralLocus2D.png
        :align: center
        :alt: visual-spectral-locus-2d
    """

    def __init__(
        self,
        cmfs: MultiSpectralDistributions
        | str
        | Sequence[
            MultiSpectralDistributions | str
        ] = "CIE 1931 2 Degree Standard Observer",
        method: Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"]
        | str = "CIE 1931",
        labels: Sequence | None = None,
        colours: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        cmfs = cast(
            MultiSpectralDistributions, first_item(filter_cmfs(cmfs).values())
        )
        method = validate_method(method, tuple(METHODS_CHROMATICITY_DIAGRAM))
        labels = cast(
            Sequence,
            optional(labels, LABELS_CHROMATICITY_DIAGRAM_DEFAULT[method]),
        )

        lines_sl, lines_w = lines_spectral_locus(cmfs, labels, method)

        # Spectral Locus
        positions = np.concatenate(
            [lines_sl["position"][:-1], lines_sl["position"][1:]], axis=1
        ).reshape([-1, 2])

        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if colours is None:
            colours_sl = np.concatenate(
                [lines_sl["colour"][:-1], lines_sl["colour"][1:]], axis=1
            ).reshape([-1, 3])
        else:
            colours_sl = np.tile(colours, (positions.shape[0], 1))

        self._spectral_locus = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(
                    append_channel(colours_sl, opacity)
                ),
            ),
            gfx.LineSegmentMaterial(thickness=thickness, color_mode="vertex"),
        )
        self.add(self._spectral_locus)

        # Wavelengths
        positions = lines_w["position"]
        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if colours is None:
            colours_w = lines_w["colour"]
        else:
            colours_w = np.tile(colours, (positions.shape[0], 1))

        self._wavelengths = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colours_w, opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=thickness, color_mode="vertex"),
        )
        self.add(self._wavelengths)

        # Labels
        self._labels = []
        for i, label in enumerate(
            [label for label in labels if label in cmfs.wavelengths]
        ):
            positions = lines_w["position"][::2]
            normals = lines_w["normal"][::2]

            text = gfx.Text(
                gfx.TextGeometry(
                    str(label),
                    font_size=CONSTANTS_COLOUR_STYLE.font_size.medium,
                    screen_space=True,
                    anchor="Center-Left"
                    if lines_w["normal"][::2][i, 0] >= 0
                    else "Center-Right",
                ),
                gfx.TextMaterial(color=CONSTANTS_COLOUR_STYLE.colour.light),
            )
            text.local.position = np.array(
                [
                    positions[i, 0] + normals[i, 0] * 1.5,
                    positions[i, 1] + normals[i, 1] * 1.5,
                    0,
                ]
            )
            self._labels.append(text)
            self.add(text)

        positions = np.hstack(
            [
                lines_w["position"][::2],
                np.full(
                    (lines_w["position"][::2].shape[0], 1),
                    0,
                    DEFAULT_FLOAT_DTYPE_WGPU,
                ),
            ]
        )

        if colours is None:
            colours_lp = lines_w["colour"][::2]
        else:
            colours_lp = np.tile(colours, (positions.shape[0], 1))

        self._points = gfx.Points(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(
                    full(lines_w["position"][::2].shape[0], thickness * 3)
                ),
                colors=as_contiguous_array(
                    append_channel(colours_lp, opacity)
                ),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )
        self.add(self._points)


class VisualSpectralLocus3D(gfx.Line):
    """
    Create a 3D *Spectral Locus* visual.

    Parameters
    ----------
    cmfs
        Standard observer colour matching functions used for computing the
        spectrum domain and colours. ``cmfs`` can be of any type or form
        supported by the :func:`colour.plotting.common.filter_cmfs` definition.
    model
        Colourspace model, see :attr:`colour.COLOURSPACE_MODELS` attribute for
        the list of supported colourspace models.
    labels
        Array of wavelength labels used to customise which labels will be drawn
        around the spectral locus. Passing an empty array will result in no
        wavelength labels being drawn.
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
    ...     visual = VisualSpectralLocus3D(model="CIE XYZ")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualSpectralLocus3D.png
        :align: center
        :alt: visual-spectral-locus-3d
    """

    def __init__(
        self,
        cmfs: MultiSpectralDistributions
        | str
        | Sequence[
            MultiSpectralDistributions | str
        ] = "CIE 1931 2 Degree Standard Observer",
        model: LiteralColourspaceModel | str = "CIE xyY",
        colours: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        cmfs = cast(
            MultiSpectralDistributions, first_item(filter_cmfs(cmfs).values())
        )

        colourspace = CONSTANTS_COLOUR_STYLE.colour.colourspace

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                cmfs.values, colourspace.whitepoint, model
            ),
            model,
        )
        positions = np.concatenate(
            [positions[:-1], positions[1:]], axis=1
        ).reshape([-1, 3])

        if colours is None:
            colours = XYZ_to_RGB(cmfs.values, colourspace)
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


class VisualChromaticityDiagram(gfx.Mesh):
    """
    Create a *Chromaticity Diagram* visual.

    Parameters
    ----------
    cmfs
        Standard observer colour matching functions used for computing the
        spectrum domain and colours. ``cmfs`` can be of any type or form
        supported by the :func:`colour.plotting.common.filter_cmfs` definition.
    method
        *Chromaticity Diagram* method.
    colours
        Colours of the visual, if *None*, the colours are computed from the
        visual geometry.
    opacity
        Opacity of the visual.
    material
        Material used to surface the visual geomeetry.
    wireframe
        Whether to render the visual as a wireframe, i.e., only render edges.
    samples
        Samples count used for generating the *Chromaticity Diagram* Delaunay
        tesselation.

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
    ...     visual = VisualChromaticityDiagram()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualChromaticityDiagram.png
        :align: center
        :alt: visual-chromaticity-diagram
    """

    def __init__(
        self,
        cmfs: MultiSpectralDistributions
        | str
        | Sequence[
            MultiSpectralDistributions | str
        ] = "CIE 1931 2 Degree Standard Observer",
        method: Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"]
        | str = "CIE 1931",
        colours: ArrayLike | None = None,
        opacity: float = 1,
        material: Type[gfx.MeshAbstractMaterial] = gfx.MeshBasicMaterial,
        wireframe: bool = False,
        samples: int = 64,
    ):
        cmfs = cast(
            MultiSpectralDistributions, first_item(filter_cmfs(cmfs).values())
        )

        illuminant = CONSTANTS_COLOUR_STYLE.colour.colourspace.whitepoint

        XYZ_to_ij = METHODS_CHROMATICITY_DIAGRAM[method]["XYZ_to_ij"]
        ij_to_XYZ = METHODS_CHROMATICITY_DIAGRAM[method]["ij_to_XYZ"]

        # CMFS
        ij_l = XYZ_to_ij(cmfs.values, illuminant)

        # Line of Purples
        d = euclidean_distance(ij_l[0], ij_l[-1])
        ij_p = tstack(
            [
                np.linspace(ij_l[0][0], ij_l[-1][0], int(d * samples)),
                np.linspace(ij_l[0][1], ij_l[-1][1], int(d * samples)),
            ]
        )

        # Grid
        triangulation = Delaunay(ij_l, qhull_options="QJ")
        xi = np.linspace(0, 1, samples)
        ii_g, jj_g = np.meshgrid(xi, xi)
        ij_g = tstack([ii_g, jj_g])
        ij_g = ij_g[triangulation.find_simplex(ij_g) > 0]

        ij = np.vstack([ij_l, illuminant, ij_p, ij_g])
        triangulation = Delaunay(ij, qhull_options="QJ")
        positions = np.hstack(
            [ij, np.full((ij.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU)]
        )

        if colours is None:
            colours = normalise_maximum(
                XYZ_to_plotting_colourspace(
                    ij_to_XYZ(positions[..., :2], illuminant), illuminant
                ),
                axis=-1,
            )
        else:
            colours = np.tile(colours, (positions.shape[0], 1))

        geometry = gfx.Geometry(
            positions=as_contiguous_array(positions),
            indices=as_contiguous_array(
                triangulation.simplices, DEFAULT_INT_DTYPE_WGPU
            ),
            colors=as_contiguous_array(append_channel(colours, opacity)),
        )

        super().__init__(
            geometry,
            material(color_mode="vertex", wireframe=wireframe)
            if wireframe
            else material(color_mode="vertex"),
        )


class VisualChromaticityDiagramCIE1931(gfx.Group):
    """
    Create the *CIE 1931* *Chromaticity Diagram* visual.

    Parameters
    ----------
    kwargs_visual_spectral_locus
        Keyword arguments for the underlying
        :class:`colour_visuals.VisualSpectralLocus2D` class.
    kwargs_visual_chromaticity_diagram
        Keyword arguments for the underlying
        :class:`colour_visuals.VisualChromaticityDiagram` class.

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
    ...     visual = VisualChromaticityDiagramCIE1931(
    ...         kwargs_visual_chromaticity_diagram={"opacity": 0.25}
    ...     )
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualChromaticityDiagramCIE1931.png
        :align: center
        :alt: visual-chromaticity-diagram-cie-1931
    """

    def __init__(
        self,
        kwargs_visual_spectral_locus: dict | None = None,
        kwargs_visual_chromaticity_diagram: dict | None = None,
    ):
        super().__init__()

        self._spectral_locus = VisualSpectralLocus2D(
            method="CIE 1931", **(optional(kwargs_visual_spectral_locus, {}))
        )
        self.add(self._spectral_locus)

        self._chromaticity_diagram = VisualChromaticityDiagram(
            method="CIE 1931",
            **(optional(kwargs_visual_chromaticity_diagram, {})),
        )
        self.add(self._chromaticity_diagram)


class VisualChromaticityDiagramCIE1960UCS(gfx.Group):
    """
    Create the *CIE 1960 UCS* *Chromaticity Diagram* visual.

    Parameters
    ----------
    kwargs_visual_spectral_locus
        Keyword arguments for the underlying
        :class:`colour_visuals.VisualSpectralLocus2D` class.
    kwargs_visual_chromaticity_diagram
        Keyword arguments for the underlying
        :class:`colour_visuals.VisualChromaticityDiagram` class.

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
    ...     visual = VisualChromaticityDiagramCIE1960UCS(
    ...         kwargs_visual_chromaticity_diagram={"opacity": 0.25}
    ...     )
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualChromaticityDiagramCIE1960UCS.png
        :align: center
        :alt: visual-chromaticity-diagram-cie-1960-ucs
    """

    def __init__(
        self,
        kwargs_visual_spectral_locus: dict | None = None,
        kwargs_visual_chromaticity_diagram: dict | None = None,
    ):
        super().__init__()

        self._spectral_locus = VisualSpectralLocus2D(
            method="CIE 1960 UCS",
            **(optional(kwargs_visual_spectral_locus, {})),
        )
        self.add(self._spectral_locus)

        self._chromaticity_diagram = VisualChromaticityDiagram(
            method="CIE 1960 UCS",
            **(optional(kwargs_visual_chromaticity_diagram, {})),
        )
        self.add(self._chromaticity_diagram)


class VisualChromaticityDiagramCIE1976UCS(gfx.Group):
    """
    Create the *CIE 1976 UCS* *Chromaticity Diagram* visual.

    Parameters
    ----------
    kwargs_visual_spectral_locus
        Keyword arguments for the underlying
        :class:`colour_visuals.VisualSpectralLocus2D` class.
    kwargs_visual_chromaticity_diagram
        Keyword arguments for the underlying
        :class:`colour_visuals.VisualChromaticityDiagram` class.

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
    ...     visual = VisualChromaticityDiagramCIE1976UCS(
    ...         kwargs_visual_chromaticity_diagram={"opacity": 0.25}
    ...     )
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)
    ...

    .. image:: ../_static/Plotting_VisualChromaticityDiagramCIE1976UCS.png
        :align: center
        :alt: visual-chromaticity-diagram-cie-1976-ucs
    """

    def __init__(
        self,
        kwargs_visual_spectral_locus: dict | None = None,
        kwargs_visual_chromaticity_diagram: dict | None = None,
    ):
        super().__init__()

        self._spectral_locus = VisualSpectralLocus2D(
            method="CIE 1976 UCS",
            **(optional(kwargs_visual_spectral_locus, {})),
        )
        self.add(self._spectral_locus)

        self._chromaticity_diagram = VisualChromaticityDiagram(
            method="CIE 1976 UCS",
            **(optional(kwargs_visual_chromaticity_diagram, {})),
        )
        self.add(self._chromaticity_diagram)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(
            None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
        )
    )

    visual_1 = VisualChromaticityDiagramCIE1931()
    scene.add(visual_1)

    visual_2 = VisualChromaticityDiagramCIE1931(
        kwargs_visual_chromaticity_diagram={"wireframe": True, "opacity": 0.5}
    )
    visual_2.local.position = np.array([1, 0, 0])
    scene.add(visual_2)

    visual_3 = VisualChromaticityDiagramCIE1931(
        kwargs_visual_chromaticity_diagram={"colours": [0.5, 0.5, 0.5]}
    )
    visual_3.local.position = np.array([2, 0, 0])
    scene.add(visual_3)

    visual_4 = VisualChromaticityDiagramCIE1960UCS()
    visual_4.local.position = np.array([3, 0, 0])
    scene.add(visual_4)

    visual_5 = VisualChromaticityDiagramCIE1976UCS()
    visual_5.local.position = np.array([4, 0, 0])
    scene.add(visual_5)

    visual_6 = VisualSpectralLocus2D(colours=[0.5, 0.5, 0.5])
    visual_6.local.position = np.array([5, 0, 0])
    scene.add(visual_6)

    visual_7 = VisualSpectralLocus3D()
    scene.add(visual_7)

    visual_8 = VisualSpectralLocus3D(colours=[0.5, 0.5, 0.5])
    visual_8.local.position = np.array([5, 0, 0])
    scene.add(visual_8)

    visual_9 = VisualSpectralLocus3D(model="CIE XYZ")
    visual_9.local.position = np.array([6, 0, 0])
    scene.add(visual_9)

    gfx.show(scene, up=np.array([0, 0, 1]))
