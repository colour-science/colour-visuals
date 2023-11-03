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
)
from colour.plotting.diagrams import lines_spectral_locus
from colour.utilities import (
    full,
    optional,
    tstack,
)
from scipy.spatial import Delaunay

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    DEFAULT_INT_DTYPE_WGPU,
    XYZ_to_colourspace_model,
    append_channel,
    as_contiguous_array,
)
from colour_visuals.visual import (
    MixinPropertyCMFS,
    MixinPropertyColour,
    MixinPropertyKwargs,
    MixinPropertyMethod,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertySamples,
    MixinPropertyThickness,
    MixinPropertyTypeMaterial,
    MixinPropertyWireframe,
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
    "VisualSpectralLocus2D",
    "VisualSpectralLocus3D",
    "VisualChromaticityDiagram",
    "MixinPropertyKwargsVisualSpectralLocus",
    "MixinPropertyKwargsVisualChromaticityDiagram",
    "VisualChromaticityDiagramCIE1931",
    "VisualChromaticityDiagramCIE1960UCS",
    "VisualChromaticityDiagramCIE1976UCS",
]


class VisualSpectralLocus2D(
    MixinPropertyCMFS,
    MixinPropertyColour,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
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
    colour
        Colour of the visual, if *None*, the colour is computed from the visual
        geometry.
    opacity
        Opacity of the visual.
    thickness
        Thickness of the visual lines.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualSpectralLocus2D.cmfs`
    -   :attr:`~colour_visuals.VisualSpectralLocus2D.method`
    -   :attr:`~colour_visuals.VisualSpectralLocus2D.labels`
    -   :attr:`~colour_visuals.VisualSpectralLocus2D.colour`
    -   :attr:`~colour_visuals.VisualSpectralLocus2D.opacity`
    -   :attr:`~colour_visuals.VisualSpectralLocus2D.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualSpectralLocus2D.__init__`
    -   :meth:`~colour_visuals.VisualSpectralLocus2D.update`

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
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        self._spectral_locus = None
        self._wavelengths = None
        self._texts = None
        self._points = None

        self._labels = None

        with self.block_update():
            self.cmfs = cmfs
            self.method = method
            self.labels = labels
            self.colour = colour
            self.opacity = opacity
            self.thickness = thickness

        self.update()

    @visual_property
    def labels(
        self,
    ) -> Sequence | None:
        """
        Getter and setter property for the labels.

        Parameters
        ----------
        value
            Value to set the labels with.

        Returns
        -------
        :class:`str`
            Labels.
        """

        return self._labels

    @labels.setter
    def labels(self, value: Sequence | None):
        """Setter for the **self.labels** property."""

        self._labels = cast(
            Sequence,
            optional(value, LABELS_CHROMATICITY_DIAGRAM_DEFAULT[self._method]),
        )

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        lines_sl, lines_w = lines_spectral_locus(
            self._cmfs, self._labels, self._method
        )

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

        if self._colour is None:
            colour_sl = np.concatenate(
                [lines_sl["colour"][:-1], lines_sl["colour"][1:]], axis=1
            ).reshape([-1, 3])
        else:
            colour_sl = np.tile(self._colour, (positions.shape[0], 1))

        self._spectral_locus = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(
                    append_channel(colour_sl, self._opacity)
                ),
            ),
            gfx.LineSegmentMaterial(
                thickness=self._thickness, color_mode="vertex"
            ),
        )
        self.add(self._spectral_locus)

        if not self._labels:
            return

        # Wavelengths
        positions = lines_w["position"]
        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if self._colour is None:
            colour_w = lines_w["colour"]
        else:
            colour_w = np.tile(self._colour, (positions.shape[0], 1))

        self._wavelengths = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(
                    append_channel(colour_w, self._opacity)
                ),
            ),
            gfx.LineSegmentMaterial(
                thickness=self._thickness, color_mode="vertex"
            ),
        )
        self.add(self._wavelengths)

        # Labels
        self._texts = []
        for i, label in enumerate(
            [
                label
                for label in self._labels
                if label in self._cmfs.wavelengths
            ]
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
                    positions[i, 0] + normals[i, 0] / 50 * 1.25,
                    positions[i, 1] + normals[i, 1] / 50 * 1.25,
                    0,
                ]
            )
            self._texts.append(text)
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

        if self._colour is None:
            colour_lp = lines_w["colour"][::2]
        else:
            colour_lp = np.tile(self._colour, (positions.shape[0], 1))

        self._points = gfx.Points(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                sizes=as_contiguous_array(
                    full(
                        lines_w["position"][::2].shape[0], self._thickness * 3
                    )
                ),
                colors=as_contiguous_array(
                    append_channel(colour_lp, self._opacity)
                ),
            ),
            gfx.PointsMaterial(color_mode="vertex", vertex_sizes=True),
        )
        self.add(self._points)


class VisualSpectralLocus3D(
    MixinPropertyCMFS,
    MixinPropertyColour,
    MixinPropertyKwargs,
    MixinPropertyModel,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
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
    -   :attr:`~colour_visuals.VisualSpectralLocus3D.cmfs`
    -   :attr:`~colour_visuals.VisualSpectralLocus3D.model`
    -   :attr:`~colour_visuals.VisualSpectralLocus3D.labels`
    -   :attr:`~colour_visuals.VisualSpectralLocus3D.colour`
    -   :attr:`~colour_visuals.VisualSpectralLocus3D.opacity`
    -   :attr:`~colour_visuals.VisualSpectralLocus3D.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualSpectralLocus3D.__init__`
    -   :meth:`~colour_visuals.VisualSpectralLocus3D.update`

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
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
        **kwargs,
    ):
        super().__init__()

        self._spectral_locus = None

        with self.block_update():
            self.cmfs = cmfs
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

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                self._cmfs.values,
                colourspace.whitepoint,
                self._model,
                **self._kwargs,
            ),
            self._model,
        )
        positions = np.concatenate(
            [positions[:-1], positions[1:]], axis=1
        ).reshape([-1, 3])

        if self._colour is None:
            colour = XYZ_to_RGB(self._cmfs.values, colourspace)
            colour = np.concatenate([colour[:-1], colour[1:]], axis=1).reshape(
                [-1, 3]
            )
        else:
            colour = np.tile(self._colour, (positions.shape[0], 1))

        self._spectral_locus = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(
                    append_channel(colour, self._opacity)
                ),
            ),
            gfx.LineSegmentMaterial(
                thickness=self._thickness, color_mode="vertex"
            ),
        )
        self.add(self._spectral_locus)


class VisualChromaticityDiagram(
    MixinPropertyCMFS,
    MixinPropertyColour,
    MixinPropertyTypeMaterial,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertySamples,
    MixinPropertyWireframe,
    Visual,
):
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
        Colour of the visual, if *None*, the colours are computed from the
        visual geometry.
    opacity
        Opacity of the visual.
    material
        Material used to surface the visual geometry.
    wireframe
        Whether to render the visual as a wireframe, i.e., only render edges.
    samples
        Samples count used for generating the *Chromaticity Diagram* Delaunay
        tesselation.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.cmfs`
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.method`
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.colours`
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.opacity`
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.type_material`
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.wireframe`
    -   :attr:`~colour_visuals.VisualChromaticityDiagram.samples`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualChromaticityDiagram.__init__`
    -   :meth:`~colour_visuals.VisualChromaticityDiagram.update`

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
        super().__init__()

        self._chromaticity_diagram = None

        with self.block_update():
            self.cmfs = cmfs
            self.method = method
            self.colours = colours
            self.opacity = opacity
            self.type_material = material
            self.wireframe = wireframe
            self.samples = samples

        self.update()

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        illuminant = CONSTANTS_COLOUR_STYLE.colour.colourspace.whitepoint

        XYZ_to_ij = METHODS_CHROMATICITY_DIAGRAM[self._method]["XYZ_to_ij"]
        ij_to_XYZ = METHODS_CHROMATICITY_DIAGRAM[self._method]["ij_to_XYZ"]

        # CMFS
        ij_l = XYZ_to_ij(self._cmfs.values, illuminant)

        # Line of Purples
        d = euclidean_distance(ij_l[0], ij_l[-1])
        ij_p = tstack(
            [
                np.linspace(ij_l[0][0], ij_l[-1][0], int(d * self._samples)),
                np.linspace(ij_l[0][1], ij_l[-1][1], int(d * self._samples)),
            ]
        )

        # Grid
        triangulation = Delaunay(ij_l, qhull_options="QJ")
        xi = np.linspace(0, 1, self._samples)
        ii_g, jj_g = np.meshgrid(xi, xi)
        ij_g = tstack([ii_g, jj_g])
        ij_g = ij_g[triangulation.find_simplex(ij_g) > 0]

        ij = np.vstack([ij_l, illuminant, ij_p, ij_g])
        triangulation = Delaunay(ij, qhull_options="QJ")
        positions = np.hstack(
            [ij, np.full((ij.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU)]
        )

        if self._colour is None:
            colours = normalise_maximum(
                XYZ_to_plotting_colourspace(
                    ij_to_XYZ(positions[..., :2], illuminant), illuminant
                ),
                axis=-1,
            )
        else:
            colours = np.tile(self._colour, (positions.shape[0], 1))

        geometry = gfx.Geometry(
            positions=as_contiguous_array(positions),
            indices=as_contiguous_array(
                triangulation.simplices, DEFAULT_INT_DTYPE_WGPU
            ),
            colors=as_contiguous_array(append_channel(colours, self._opacity)),
        )

        self._chromaticity_diagram = gfx.Mesh(
            geometry,
            self._type_material(color_mode="vertex", wireframe=self._wireframe)
            if self._wireframe
            else self._type_material(color_mode="vertex"),
        )
        self.add(self._chromaticity_diagram)


class MixinPropertyKwargsVisualSpectralLocus:
    """
    Define a mixin for keyword arguments for the
    :class:`colour_visuals.VisualSpectralLocus2D` class.

    Attributes
    ----------
    -   :attr:`~colour_visuals.diagrams.MixinPropertyKwargsVisualSpectralLocus.\
kwargs_visual_spectral_locus`
    """

    def __init__(self):
        self._spectral_locus = None
        self._kwargs_visual_spectral_locus = {}

        super().__init__()

    @property
    def kwargs_visual_spectral_locus(self) -> dict:
        """
        Getter and setter property for the visual kwargs for the
        *Spectral Locus*.

        Parameters
        ----------
        value
            Value to set visual kwargs for the *Spectral Locus* with.

        Returns
        -------
        :class:`dict`
            Visual kwargs for the *Spectral Locus*.
        """

        return self._kwargs_visual_spectral_locus

    @kwargs_visual_spectral_locus.setter
    def kwargs_visual_spectral_locus(self, value: dict):
        """
        Setter for the **self.kwargs_visual_spectral_locus** property.
        """

        self._kwargs_visual_spectral_locus = value

        for key, value in self._kwargs_visual_spectral_locus.items():
            setattr(self._spectral_locus, key, value)


class MixinPropertyKwargsVisualChromaticityDiagram:
    """
    Define a mixin for keyword arguments for the
    :class:`colour_visuals.VisualChromaticityDiagram` class.

    Attributes
    ----------
    -   :attr:`~colour_visuals.diagrams.\
MixinPropertyKwargsVisualChromaticityDiagram.kwargs_visual_chromaticity_diagram`
    """

    def __init__(self):
        self._chromaticity_diagram = None
        self._kwargs_visual_chromaticity_diagram = {}

        super().__init__()

    @property
    def kwargs_visual_chromaticity_diagram(self) -> dict:
        """
        Getter and setter property for the visual kwargs for the
        *Chromaticity Diagram*.

        Parameters
        ----------
        value
            Value to set visual kwargs for the *Chromaticity Diagram* with.

        Returns
        -------
        :class:`dict`
            Visual kwargs for the *Chromaticity Diagram*.
        """

        return self._kwargs_visual_chromaticity_diagram

    @kwargs_visual_chromaticity_diagram.setter
    def kwargs_visual_chromaticity_diagram(self, value: dict):
        """
        Setter for the **self.kwargs_visual_chromaticity_diagram** property.
        """

        self._kwargs_visual_chromaticity_diagram = value

        for key, value in self._kwargs_visual_chromaticity_diagram.items():
            setattr(self._chromaticity_diagram, key, value)


class VisualChromaticityDiagramCIE1931(
    MixinPropertyKwargsVisualSpectralLocus,
    MixinPropertyKwargsVisualChromaticityDiagram,
    Visual,
):
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

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualChromaticityDiagramCIE1931.\
kwargs_visual_spectral_locus`
    -   :attr:`~colour_visuals.VisualChromaticityDiagramCIE1931.\
kwargs_visual_chromaticity_diagram`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualChromaticityDiagramCIE1931.__init__`
    -   :meth:`~colour_visuals.VisualChromaticityDiagramCIE1931.update`

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

        if kwargs_visual_spectral_locus is None:
            kwargs_visual_spectral_locus = {}

        if kwargs_visual_chromaticity_diagram is None:
            kwargs_visual_chromaticity_diagram = {}

        self._spectral_locus = VisualSpectralLocus2D(method="CIE 1931")
        self.add(self._spectral_locus)

        self._chromaticity_diagram = VisualChromaticityDiagram(
            method="CIE 1931"
        )
        self.add(self._chromaticity_diagram)

        self.kwargs_visual_spectral_locus = kwargs_visual_spectral_locus
        self.kwargs_visual_chromaticity_diagram = (
            kwargs_visual_chromaticity_diagram
        )

    def update(self):
        """Update the visual."""


class VisualChromaticityDiagramCIE1960UCS(
    MixinPropertyKwargsVisualSpectralLocus,
    MixinPropertyKwargsVisualChromaticityDiagram,
    Visual,
):
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

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualChromaticityDiagramCIE1960UCS.\
kwargs_visual_spectral_locus`
    -   :attr:`~colour_visuals.VisualChromaticityDiagramCIE1960UCS.\
kwargs_visual_chromaticity_diagram`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualChromaticityDiagramCIE1960UCS.__init__`
    -   :meth:`~colour_visuals.VisualChromaticityDiagramCIE1960UCS.update`

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

        if kwargs_visual_spectral_locus is None:
            kwargs_visual_spectral_locus = {}

        if kwargs_visual_chromaticity_diagram is None:
            kwargs_visual_chromaticity_diagram = {}

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

        self.kwargs_visual_spectral_locus = kwargs_visual_spectral_locus
        self.kwargs_visual_chromaticity_diagram = (
            kwargs_visual_chromaticity_diagram
        )

    def update(self):
        """Update the visual."""


class VisualChromaticityDiagramCIE1976UCS(
    MixinPropertyKwargsVisualSpectralLocus,
    MixinPropertyKwargsVisualChromaticityDiagram,
    Visual,
):
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

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualChromaticityDiagramCIE1976UCS.\
kwargs_visual_spectral_locus`
    -   :attr:`~colour_visuals.VisualChromaticityDiagramCIE1976UCS.\
kwargs_visual_chromaticity_diagram`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualChromaticityDiagramCIE1976UCS.__init__`
    -   :meth:`~colour_visuals.VisualChromaticityDiagramCIE1976UCS.update`

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

        if kwargs_visual_spectral_locus is None:
            kwargs_visual_spectral_locus = {}

        if kwargs_visual_chromaticity_diagram is None:
            kwargs_visual_chromaticity_diagram = {}

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

        self.kwargs_visual_spectral_locus = kwargs_visual_spectral_locus
        self.kwargs_visual_chromaticity_diagram = (
            kwargs_visual_chromaticity_diagram
        )

    def update(self):
        """Update the visual."""


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

    visual_6 = VisualSpectralLocus2D(colour=[0.5, 0.5, 0.5])
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
